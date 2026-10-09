#!/usr/bin/env python3
"""回测守门层 —— 判定一个结果能不能进入下一轮。

设计原则：与回测引擎解耦
------------------------
本脚本**不是回测引擎**，也不计算信号或持仓。它只接受外部回测导出的
「日收益序列 + 元信息」，然后做统计与规范性检查。

这样设计有两个理由：
1. 按 CLAUDE.md 与 tools/factors/README.md，本仓库不引入回测撮合引擎。
   守门层与引擎解耦后，Pine、mjs、pandas 任何一种回测都能接入。
2. 让「生成结果」和「判定结果」跑在两条独立路径上。同一个模型既生成
   策略又评价策略是循环论证 —— 评价必须由独立代码产出。

检查项
------
    [登记]      hyp_id 必须在 registry 里，且状态不是 retired/rejected
    [数据]      收益序列合法、长度足够；给了成本就要求给换手率
    [future]    静态扫描提交的代码，找读未来的反模式
    [Bonferroni] 多重检验校正后的显著性
    [PSR]       Deflated Sharpe / 概率夏普比率（考虑试验次数的阈值）
    [样本外]    给了 is_split 就比对样本内外

关于 [future] 扫描，必须说清它的局限
-----------------------------------
它是**正则启发式，不是数据流分析**。它会漏报（绕开写法的未来函数扫不出来），
也会误报（变量名含 future 但其实是预测输出）。

⇒ 因此命中的后果是 **WARN，不是 FAIL**，也不会让整体判定变 PASS。
   把它当 FAIL 会制造假安全感（以为扫过就没问题）；
   把它完全去掉又会放任最致命的一类错误。
   正确用法：命中后人工确认那一行，确认无害就在报告里记一笔。

统计口径
--------
Sharpe 一律按**单期（非年化）**计算后做检验，避免因年化因子选 252 还是 365
而改变结论；报告里另外给出年化值仅供阅读。

PSR 用 Bailey & López de Prado 的定义：

    PSR(SR*) = Φ[ (SR̂ − SR*)·√(n−1) / √(1 − γ̂₃·SR̂ + ((γ̂₄−1)/4)·SR̂²) ]
    SR*      = √V[SR̂] · [ (1−γ)·Φ⁻¹(1 − 1/N) + γ·Φ⁻¹(1 − 1/(N·e)) ]

V[SR̂] 取 Lo (2002) 的 IID 渐近方差 (1 + SR̂²/2)/n。
注意：若收益存在自相关，该值会被低估，PSR 偏乐观 —— 本脚本不修正自相关。

输入 JSON
---------
    {
      "hyp_id": "H-20261009-001",
      "returns": [0.0012, -0.0008, ...],
      "trials": 5,                      实际试验次数（覆盖注册表的 trials_planned）
      "code_paths": ["research/x/backtest.py"],   用于 future 扫描，可省略
      "is_split": 0.7,                  样本内比例，可省略
      "cost_bps": 5.0,                  单边成本 bps，给了就必须给 turnover
      "turnover": [1.0, 0.0, ...],      与 returns 等长，可省略
      "annualization": 365              阅读用年化因子，默认 365
    }

用法
----
    python3 gate.py --result result.json
    python3 gate.py --result result.json --json      机器可读
    python3 gate.py --result result.json --min-n 250 --psr-threshold 0.99

退出码（与 tools/validation 一致）
----------------------------------
    0 PASS  1 FAIL  2 INCONCLUSIVE（数据不足以判定）  3 ERROR
"""

import argparse
import json
import math
import os
import re
import sys

REPO = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)
DEFAULT_REGISTRY = os.path.join(REPO, "research", "hypotheses", "registry.jsonl")

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_INCONCLUSIVE = 2
EXIT_ERROR = 3

DEFAULT_MIN_N = 100
DEFAULT_ALPHA = 0.05
DEFAULT_PSR_THRESHOLD = 0.95
DEFAULT_ANNUALIZATION = 365

# ---- future 反模式（启发式，见文件头说明） ------------------------------------
# 每项 = (正则, 说明)。按扩展名分组；"*" 对所有文件生效。
FUTURE_PATTERNS = {
    "*": [
        (r"\.shift\(\s*-\s*\d+", "shift(负数)：向前取数，等于读未来"),
        (r"\[::-1\]", "序列反转：确认不是把未来挪到过去"),
        (r"lookahead\s*=\s*(barmerge\.lookahead_on|True|1)",
         "显式开启 lookahead"),
        (r"\.bfill\(\)", "向后填充：用后值补前值"),
    ],
    ".py": [
        (r"\bfuture_\w*\s*=", "变量名含 future：确认不是拿未来值当特征"),
        (r"\.iloc\[[^\]]*\+\s*1[^\]]*\]", "iloc 里出现 +1：确认没越界取到未来"),
    ],
    ".pine": [
        (r"request\.security\s*\([^)]*lookahead_on",
         "request.security 开 lookahead_on：会引入未来数据"),
    ],
    ".mjs": [
        (r"\bi\s*\+\s*1\s*\]", "下标 +1：确认循环没读到未发生的 bar"),
    ],
}


# ---- 统计：与 attribute.py 共用 _stats，保证两处口径一致 -------------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _stats import (
    NORM, deflated_sr_threshold, kurtosis_raw, max_drawdown, mean,
    psr, skewness, stdev,
)


# ---- 各项检查 ----------------------------------------------------------------

def load_registry(path):
    if not os.path.exists(path):
        return {}
    latest = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            latest[e.get("id")] = e
    return latest


def check_registration(hyp_id, registry):
    if not hyp_id:
        return ("FAIL", "result 未声明 hyp_id。未登记的假设不予评估。")
    e = registry.get(hyp_id)
    if not e:
        return ("FAIL", "registry 中查不到 %s。先跑 hypotheses.py register。" % hyp_id)
    st = e.get("status")
    if st in ("retired", "rejected"):
        return ("FAIL", "%s 当前状态为 %s，不接受新的结果提交。" % (hyp_id, st))
    return ("PASS", "状态=%s，计划试验=%s" % (st, e.get("trials_planned", "?")))


def check_future(code_paths):
    """返回 (status, msg, hits)；hits 是 [(文件, 行号, 说明)]。"""
    if not code_paths:
        return ("SKIP", "未提供 code_paths，未做静态扫描", [])
    hits = []
    for p in code_paths:
        if not os.path.exists(p):
            hits.append((p, 0, "文件不存在，无法扫描"))
            continue
        ext = os.path.splitext(p)[1].lower()
        pats = FUTURE_PATTERNS.get("*", []) + FUTURE_PATTERNS.get(ext, [])
        with open(p, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                for pat, desc in pats:
                    if re.search(pat, line):
                        hits.append((p, i, "%s  |  %s" % (desc, line.strip()[:90])))
    if not hits:
        return ("PASS", "扫描 %d 个文件，未命中已知反模式" % len(code_paths), [])
    # 明确：命中只给 WARN。理由见文件头。
    return ("WARN", "命中 %d 处（启发式，可能误报，需人工确认）" % len(hits), hits)


def check_bonferroni(sr_hat, n, trials, alpha):
    if trials < 1:
        trials = 1
    alpha_adj = alpha / trials
    t = sr_hat * math.sqrt(n)
    p = 2.0 * (1.0 - NORM.cdf(abs(t)))
    ok = p < alpha_adj
    return (
        ("PASS" if ok else "FAIL"),
        "α=%g/%d=%.4g, t=%.2f, p=%.4g %s %.4g" % (
            alpha, trials, alpha_adj, t, p, "<" if ok else ">=", alpha_adj),
    )


def check_psr(sr_hat, n, trials, skew, kurt, threshold):
    sr_star = deflated_sr_threshold(n, trials, sr_hat)
    val = psr(sr_hat, n, sr_star, skew, kurt)
    ok = val >= threshold
    return (
        ("PASS" if ok else "FAIL"),
        "PSR=%.3f %s %.2f（N=%d, 运气阈值 SR*=%.4f, 偏度=%.2f, 峰度=%.2f）" % (
            val, ">=" if ok else "<", threshold, trials, sr_star, skew, kurt),
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="回测守门层（与回测引擎解耦）")
    ap.add_argument("--result", required=True, help="回测结果 JSON 路径")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--min-n", type=int, default=DEFAULT_MIN_N)
    ap.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    ap.add_argument("--psr-threshold", type=float, default=DEFAULT_PSR_THRESHOLD)
    ap.add_argument("--json", action="store_true", help="输出机器可读结果")
    args = ap.parse_args(argv)

    try:
        with open(args.result, encoding="utf-8") as fh:
            res = json.load(fh)
    except Exception as e:  # noqa: BLE001
        print("读取 %s 失败: %s" % (args.result, e), file=sys.stderr)
        return EXIT_ERROR

    if not os.path.exists(args.registry):
        print("registry 不存在: %s" % args.registry, file=sys.stderr)
        print("先跑 tools/research/hypotheses.py register 登记假设。", file=sys.stderr)
        return EXIT_ERROR

    returns = res.get("returns") or []
    hyp_id = res.get("hyp_id")
    trials = int(res.get("trials") or 0)
    annualization = float(res.get("annualization") or DEFAULT_ANNUALIZATION)

    report = {"hyp_id": hyp_id, "checks": [], "warnings": []}
    registry = load_registry(args.registry)

    # ---- 1. 登记 ----
    status, msg = check_registration(hyp_id, registry)
    if status == "FAIL":
        print("未通过登记检查：%s" % msg, file=sys.stderr)
        report["checks"].append({"name": "登记", "status": status, "detail": msg})
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return EXIT_FAIL
    report["checks"].append({"name": "登记", "status": status, "detail": msg})

    # 未显式给 trials 时，退回注册表的 trials_planned
    if trials == 0:
        trials = int(registry.get(hyp_id, {}).get("trials_planned") or 1)
        report["warnings"].append("result 未给 trials，已用注册表的 trials_planned=%d；"
                                  "实际跑的比这个多就必须如实上报" % trials)

    # ---- 2. 数据 ----
    clean = []
    for x in returns:
        try:
            clean.append(float(x))
        except (TypeError, ValueError):
            pass
    if len(clean) != len(returns) and returns:
        report["warnings"].append("收益序列含 %d 个非数值项，已丢弃"
                                  % (len(returns) - len(clean)))
    returns = clean

    cost_bps = res.get("cost_bps")
    turnover = res.get("turnover") or []
    if cost_bps is not None:
        if len(turnover) != len(returns):
            print("给了 cost_bps 但 turnover 长度与 returns 不一致（或缺省）。",
                  file=sys.stderr)
            print("没有换手率就无法扣成本，本项判定为 INCONCLUSIVE。", file=sys.stderr)
            report["checks"].append({"name": "成本", "status": "INCONCLUSIVE",
                                     "detail": "缺 turnover，成本未扣减"})
            cost_note = "成本未扣（缺 turnover）"
        else:
            returns = [r - float(cost_bps) / 10000.0 * float(t)
                       for r, t in zip(returns, turnover)]
            cost_note = "已扣 %.1fbps×换手" % float(cost_bps)
    else:
        cost_note = "未声明成本"

    n = len(returns)
    if n < args.min_n:
        report["checks"].append({"name": "样本量", "status": "INCONCLUSIVE",
                                 "detail": "n=%d < min_n=%d，统计功效不足" % (n, args.min_n)})
        report["checks"].append({"name": "成本", "status": "PASS", "detail": cost_note})
        print("样本量不足：n=%d < %d，无法判定。" % (n, args.min_n))
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        return EXIT_INCONCLUSIVE
    report["checks"].append({"name": "数据", "status": "PASS",
                             "detail": "n=%d, %s" % (n, cost_note)})

    # ---- 3. future 静态扫描 ----
    status, msg, hits = check_future(res.get("code_paths"))
    report["checks"].append({"name": "future", "status": status, "detail": msg,
                             "hits": [{"file": f, "line": i, "note": t}
                                      for f, i, t in hits]})

    # ---- 4/5. 统计 ----
    sd = stdev(returns)
    sr_hat = mean(returns) / sd if sd > 0 else 0.0
    skew, kurt = skewness(returns), kurtosis_raw(returns)

    st, msg = check_bonferroni(sr_hat, n, trials, args.alpha)
    report["checks"].append({"name": "多重检验", "status": st, "detail": msg})
    st, msg = check_psr(sr_hat, n, trials, skew, kurt, args.psr_threshold)
    report["checks"].append({"name": "PSR", "status": st, "detail": msg})

    # ---- 6. 样本外 ----
    split = res.get("is_split")
    if not split:
        report["checks"].append({"name": "样本外", "status": "SKIP",
                                 "detail": "未提供 is_split，未做内外比对"})
    else:
        k = int(n * float(split))
        if k < 20 or n - k < 20:
            report["checks"].append({"name": "样本外", "status": "INCONCLUSIVE",
                                     "detail": "分段太短（IS=%d, OOS=%d）" % (k, n - k)})
        else:
            is_ret, oos_ret = returns[:k], returns[k:]
            is_sd, oos_sd = stdev(is_ret), stdev(oos_ret)
            is_sr = mean(is_ret) / is_sd if is_sd > 0 else 0.0
            oos_sr = mean(oos_ret) / oos_sd if oos_sd > 0 else 0.0
            ok = oos_sr > 0
            report["checks"].append({
                "name": "样本外", "status": "PASS" if ok else "FAIL",
                "detail": "IS Sharpe/期=%.4f, OOS Sharpe/期=%.4f%s" % (
                    is_sr, oos_sr, "" if ok else "（样本外为负，判 FAIL）")})

    # ---- 汇总 ----
    hard = [c for c in report["checks"] if c["status"] == "FAIL"]
    verdict = "FAIL" if hard else "PASS"
    report["verdict"] = verdict
    report["stats"] = {
        "n": n,
        "sharpe_per_period": round(sr_hat, 6),
        "sharpe_annualized": round(sr_hat * math.sqrt(annualization), 4),
        "annualization": annualization,
        "mean_return": round(mean(returns), 8),
        "stdev": round(sd, 8),
        "skew": round(skew, 4),
        "kurtosis_raw": round(kurt, 4),
        "max_drawdown": round(max_drawdown(returns), 6),
        "trials": trials,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return EXIT_FAIL if verdict == "FAIL" else EXIT_PASS

    print("=" * 68)
    print("守门报告  %s" % hyp_id)
    print("=" * 68)
    for c in report["checks"]:
        print("[%-10s] %-6s %s" % (c["name"], c["status"], c["detail"]))
        for h in c.get("hits", []):
            print("             └ %s:%s  %s" % (h["file"], h["line"], h["note"]))
    print("-" * 68)
    s = report["stats"]
    print("Sharpe/期 %.4f   年化 %.2f (×√%d)   n=%d" % (
        s["sharpe_per_period"], s["sharpe_annualized"], s["annualization"], s["n"]))
    print("均值 %.6f  标准差 %.6f  偏度 %.2f  峰度 %.2f  最大回撤 %.2f%%" % (
        s["mean_return"], s["stdev"], s["skew"], s["kurtosis_raw"],
        s["max_drawdown"] * 100))
    for w in report["warnings"]:
        print("! %s" % w)
    print("-" * 68)
    print("结论: %s" % verdict)
    if verdict == "PASS":
        print("提醒: PASS 只表示未被本层拦下，不等于策略可用。实盘才是唯一 ground truth。")
    return EXIT_FAIL if verdict == "FAIL" else EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
