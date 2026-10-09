#!/usr/bin/env python3
"""失效归因 —— 回答「这个策略在什么时候不赚钱」。

守门层只判「能不能过」，不解释「为什么」。本脚本补第二问：
把一个收益序列按**时间**和**波动状态**切开，看每段各是什么表现。

如果一段策略的收益高度集中在某一段时间、或只在某一类波动环境里成立，
那么 Sharpe 再高也不该信 —— 这说明它吃的是特定行情，不是可重复的机制。
这一条 Chan 那本没讲，却是过拟合最常见的藏身处。

分段维度
--------
    time   按时间等分成 k 段（默认 4），看收益是否随时间衰减
    vol    用滚动 window 期波动率把每期分到 低/中/高 三档，看是否依赖波动环境

输出每段：n、单期 Sharpe、累计收益、胜率、最大回撤，以及该段贡献占全期
累计收益的比例。

「集中度」判定
--------------
单段贡献占比超过 --concentration-limit（默认 0.6，即 60%）就告警：
收益过度依赖单一区间，稳健性存疑，需要补样本或改写假设。

边界
----
按 CLAUDE.md 与 tools/factors/README.md：不引入交易执行层、不引入回测撮合引擎。
本脚本只读收益序列，不计算信号、不接触订单与仓位。

用法
----
    python3 attribute.py --result result.json
    python3 attribute.py --result result.json --k 6 --window 21 --json
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats import cumulative, max_drawdown, mean, sharpe, stdev, win_rate  # noqa: E402

EXIT_OK = 0
EXIT_ERROR = 3

DEFAULT_K = 4
DEFAULT_WINDOW = 21
DEFAULT_CONCENTRATION_LIMIT = 0.6


def segment_stats(returns):
    return {
        "n": len(returns),
        "sharpe": round(sharpe(returns), 4),
        "cum": round(cumulative(returns), 4),
        "win_rate": round(win_rate(returns), 4),
        "max_dd": round(max_drawdown(returns), 4),
        "mean": round(mean(returns), 8),
    }


def split_by_time(returns, k):
    """按时间顺序等分 k 段（尾部余量并入最后一段）。"""
    n = len(returns)
    size = n // k
    if size < 1:
        return []
    out = []
    for i in range(k):
        lo = i * size
        hi = (i + 1) * size if i < k - 1 else n
        out.append(("Q%d [%d:%d]" % (i + 1, lo, hi), returns[lo:hi]))
    return out


def split_by_vol(returns, window):
    """按滚动 window 期波动率把每期归入 低/中/高 三档。

    波动率用最近 window 期（含当期）的收益标准差；前 window-1 期因窗口不完整，
    用已有部分计算（会偏低，故该段样本量小的时候看结论要保守）。
    """
    n = len(returns)
    vols = []
    for i in range(n):
        lo = max(0, i - window + 1)
        vols.append(stdev(returns[lo:i + 1]))
    ordered = sorted(vols)
    if not ordered:
        return []

    def q(p):
        idx = min(n - 1, max(0, int(round(p * (n - 1)))))
        return ordered[idx]

    lo_thr, hi_thr = q(1 / 3), q(2 / 3)
    buckets = {"低波动": [], "中波动": [], "高波动": []}
    for r, v in zip(returns, vols):
        if v <= lo_thr:
            buckets["低波动"].append(r)
        elif v >= hi_thr:
            buckets["高波动"].append(r)
        else:
            buckets["中波动"].append(r)
    return [(name, vals) for name, vals in buckets.items() if vals]


def load_returns(args):
    if args.result:
        with open(args.result, encoding="utf-8") as fh:
            res = json.load(fh)
        returns = res.get("returns") or []
        hyp_id = res.get("hyp_id")
    else:
        with open(args.returns, encoding="utf-8") as fh:
            returns = json.load(fh)
        hyp_id = None
    clean = []
    for x in returns:
        try:
            clean.append(float(x))
        except (TypeError, ValueError):
            pass
    return clean, hyp_id


def print_table(title, groups, total_cum, limit):
    print("")
    print("--- %s ---" % title)
    print("%-16s %6s %9s %9s %8s %9s %8s" % (
        "段", "n", "Sharpe/期", "累计", "胜率", "最大回撤", "贡献占比"))
    flagged = []
    for name, vals in groups:
        if len(vals) < 2:
            print("%-16s %6d %9s %9s %8s %9s %8s" % (
                name, len(vals), "-", "-", "-", "-", "-"))
            continue
        s = segment_stats(vals)
        share = (s["cum"] / total_cum) if total_cum else 0.0
        mark = ""
        if abs(share) > limit:
            mark = " <<<"
            flagged.append((name, share))
        print("%-16s %6d %9.4f %9.4f %8.1f%% %9.2f%% %7.1f%%%s" % (
            name, s["n"], s["sharpe"], s["cum"], s["win_rate"] * 100,
            s["max_dd"] * 100, share * 100, mark))
    return flagged


def main(argv=None):
    ap = argparse.ArgumentParser(description="失效归因（分段拆解收益序列）")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--result", help="gate.py 同款的结果 JSON")
    g.add_argument("--returns", help="纯收益序列 JSON 数组文件")
    ap.add_argument("--k", type=int, default=DEFAULT_K, help="时间等分段数")
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW,
                    help="滚动波动率窗口（期）")
    ap.add_argument("--concentration-limit", type=float,
                    default=DEFAULT_CONCENTRATION_LIMIT,
                    help="单段贡献占比告警阈值")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        returns, hyp_id = load_returns(args)
    except Exception as e:  # noqa: BLE001
        print("读取失败: %s" % e, file=sys.stderr)
        return EXIT_ERROR

    if len(returns) < args.k * 2:
        print("样本太短：n=%d，无法按 k=%d 分段（至少需要 %d）"
              % (len(returns), args.k, args.k * 2), file=sys.stderr)
        return EXIT_ERROR

    total_cum = cumulative(returns)
    overall = segment_stats(returns)

    if args.json:
        payload = {
            "hyp_id": hyp_id,
            "overall": overall,
            "by_time": [{"segment": n, **segment_stats(v)}
                        for n, v in split_by_time(returns, args.k)],
            "by_vol": [{"segment": n, **segment_stats(v)}
                       for n, v in split_by_vol(returns, args.window)],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return EXIT_OK

    print("=" * 78)
    print("归因报告  %s" % (hyp_id or "(未登记假设)"))
    print("=" * 78)
    print("全期: n=%d  Sharpe/期=%.4f  累计=%.2f%%  胜率=%.1f%%  最大回撤=%.2f%%" % (
        overall["n"], overall["sharpe"], overall["cum"] * 100,
        overall["win_rate"] * 100, overall["max_dd"] * 100))

    f1 = print_table("按时间 %d 等分" % args.k,
                     split_by_time(returns, args.k), total_cum,
                     args.concentration_limit)
    f2 = print_table("按滚动 %d 期波动率分档" % args.window,
                     split_by_vol(returns, args.window), total_cum,
                     args.concentration_limit)

    print("")
    if f1 or f2:
        print("! 集中度告警（单段贡献占比 > %.0f%%）:" % (args.concentration_limit * 100))
        for name, share in f1 + f2:
            print("    %s 贡献 %.1f%% —— 收益高度依赖该区间，稳健性存疑" % (
                name, share * 100))
        print("  建议：补样本跨过该区间，或把该区间的外部条件写进假设的证伪条件。")
    else:
        print("未触发集中度告警。")
    print("")
    print("注意: 分段一旦由「看结果之后」选定，就会引入新的选择偏差。")
    print("      要用分段做决策，先在注册表里把分段口径登记进去，再跑。")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
