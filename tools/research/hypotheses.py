#!/usr/bin/env python3
"""假设注册表 —— 回测前必须先落盘。

为什么要有这道手续
------------------
用 LLM 批量产出假设时，最大的失效模式不是「假设质量差」，而是
「先看到结果、再倒编一个解释」。一旦允许事后编造机制与证伪条件，
回测就退化成拟合噪声，而且迭代越快、假阳越多。

本脚本把假设**在看到任何回测结果之前**写进 append-only 的 jsonl，
并强制要求四个字段齐全：设想、传导机制、可获取数据源、证伪条件。
缺「证伪条件」的假设直接拒绝登记 —— 不可证伪的陈述不是假设。

登记后的 id 是 gate.py 的通行证：没有登记过的 id，守门层拒绝评估。

边界
----
按 CLAUDE.md 与 tools/factors/README.md：本仓库禁止重新引入 Python 交易执行层
（FreqTrade / 下单接口 / 账户签名 / Docker 部署 / 交易数据库），也禁止回测撮合引擎。
本脚本只做「登记与状态流转」，不计算任何收益、不接触订单与仓位。

用法
----
    python3 hypotheses.py register \
        --statement "BTC 永续资金费连续 3 日为负后，次日收益为正" \
        --mechanism "负资金费=空头付费，空头拥挤，轧空压力推升价格" \
        --data-source "data/raw/binance-futures/BTCUSDT_funding.csv + BTCUSDT_perp_1d.csv" \
        --falsification "样本外 Sharpe<=0，或去掉 2021-05 后显著性消失" \
        --direction long --universe BTCUSDT --frequency 1d --trials-planned 5

    python3 hypotheses.py list [--status registered]
    python3 hypotheses.py show H-20261009-001
    python3 hypotheses.py status H-20261009-001 testing

状态流转
--------
    registered  已登记，尚未回测
    testing     回测中
    accepted    通过守门层，可进入下一轮验证
    rejected    未通过守门层
    retired     主动废弃（数据源失效、机制已被证伪等）

注意：**状态可以改，条目不能删**。registry 是 append-only 的，
改状态会追加一条新记录（带 prev_status），旧记录保留，形成可审计的时间线。
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)
DEFAULT_REGISTRY = os.path.join(REPO, "research", "hypotheses", "registry.jsonl")

REQUIRED_FIELDS = ("statement", "mechanism", "data_source", "falsification")
VALID_DIRECTIONS = ("long", "short", "both", "neutral")
VALID_STATUSES = ("registered", "testing", "accepted", "rejected", "retired")
ID_RE = re.compile(r"^H-(\d{8})-(\d{3})$")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_NOT_FOUND = 3


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path):
    """读取 jsonl，返回全部条目（保持文件顺序）。"""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def _latest(entries):
    """同一 id 只保留最后一次状态变更后的条目。"""
    latest = {}
    for e in entries:
        latest[e.get("id")] = e
    return latest


def _next_id(entries, today=None):
    """ID 按**本地日期**编号（registered_at 仍记 UTC）。

    用 UTC 会让跨零点的本地会话拿到「昨天」的编号，与人的直觉错位。
    """
    today = today or datetime.now().strftime("%Y%m%d")
    max_n = 0
    for e in entries:
        m = ID_RE.match(e.get("id", ""))
        if m and m.group(1) == today:
            max_n = max(max_n, int(m.group(2)))
    return "H-%s-%03d" % (today, max_n + 1)


def _append(path, entry):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def cmd_register(args):
    missing = [f for f in REQUIRED_FIELDS if not getattr(args, f, None)]
    if missing:
        print("拒绝登记：以下必填字段缺失 -> %s" % ", ".join(missing), file=sys.stderr)
        print("缺少「证伪条件」的陈述不是假设，先补上再来。", file=sys.stderr)
        return EXIT_USAGE
    if args.direction not in VALID_DIRECTIONS:
        print("direction 必须是 %s" % "/".join(VALID_DIRECTIONS), file=sys.stderr)
        return EXIT_USAGE
    if args.trials_planned < 1:
        print("trials-planned 必须 >= 1（没做过试验就填 1）", file=sys.stderr)
        return EXIT_USAGE

    entries = _load(args.registry)
    hyp_id = _next_id(entries)
    entry = {
        "id": hyp_id,
        "registered_at": _now(),
        "status": "registered",
        "statement": args.statement,
        "mechanism": args.mechanism,
        "data_source": args.data_source,
        "falsification": args.falsification,
        "direction": args.direction,
        "universe": args.universe,
        "frequency": args.frequency,
        "trials_planned": args.trials_planned,
        "tags": args.tags or [],
    }
    _append(args.registry, entry)
    print("已登记 %s" % hyp_id)
    print("  设想      %s" % entry["statement"])
    print("  证伪条件  %s" % entry["falsification"])
    print("  计划试验  %d 次（守门层会据此做多重检验校正）" % entry["trials_planned"])
    print("")
    print("回测完成后：python3 gate.py --result <result.json>")
    return EXIT_OK


def cmd_list(args):
    entries = _load(args.registry)
    latest = _latest(entries)
    rows = sorted(latest.values(), key=lambda e: e.get("id", ""))
    if args.status:
        rows = [r for r in rows if r.get("status") == args.status]
    if not rows:
        print("（注册表为空）" if not args.status else "（无 %s 状态的条目）" % args.status)
        return EXIT_OK
    print("%-16s %-11s %-5s %-6s %s" % ("ID", "STATUS", "TRIAL", "DIR", "STATEMENT"))
    for r in rows:
        stmt = r.get("statement", "")
        if len(stmt) > 46:
            stmt = stmt[:43] + "..."
        print("%-16s %-11s %-5s %-6s %s" % (
            r.get("id", "?"), r.get("status", "?"),
            r.get("trials_planned", "?"), r.get("direction", "?"), stmt))
    return EXIT_OK


def cmd_show(args):
    entries = _load(args.registry)
    latest = _latest(entries)
    e = latest.get(args.hyp_id)
    if not e:
        print("未找到 %s" % args.hyp_id, file=sys.stderr)
        return EXIT_NOT_FOUND
    print(json.dumps(e, ensure_ascii=False, indent=2))
    history = [x for x in entries if x.get("id") == args.hyp_id]
    if len(history) > 1:
        print("")
        print("状态变更历史（%d 条，append-only）:" % len(history))
        for h in history:
            print("  %s  %s -> %s%s" % (
                h.get("changed_at", h.get("registered_at", "?")),
                h.get("prev_status", "-"), h.get("status", "?"),
                ("  (%s)" % h["note"]) if h.get("note") else ""))
    return EXIT_OK


def cmd_status(args):
    if args.status not in VALID_STATUSES:
        print("status 必须是 %s" % "/".join(VALID_STATUSES), file=sys.stderr)
        return EXIT_USAGE
    entries = _load(args.registry)
    latest = _latest(entries)
    old = latest.get(args.hyp_id)
    if not old:
        print("未找到 %s" % args.hyp_id, file=sys.stderr)
        return EXIT_NOT_FOUND
    new = dict(old)
    new["prev_status"] = old.get("status")
    new["status"] = args.status
    new["changed_at"] = _now()
    if args.note:
        new["note"] = args.note
    _append(args.registry, new)
    print("%s: %s -> %s" % (args.hyp_id, old.get("status"), args.status))
    return EXIT_OK


def main(argv=None):
    ap = argparse.ArgumentParser(description="假设注册表（回测前落盘）")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("register", help="登记新假设（四要素必填）")
    r.add_argument("--statement", required=True, help="设想：一句话说清预期关系")
    r.add_argument("--mechanism", required=True, help="传导机制：为什么会成立")
    r.add_argument("--data-source", required=True, help="可获取数据源")
    r.add_argument("--falsification", required=True, help="证伪条件：什么情况下算被推翻")
    r.add_argument("--direction", default="both", choices=VALID_DIRECTIONS)
    r.add_argument("--universe", default="BTCUSDT")
    r.add_argument("--frequency", default="1d")
    r.add_argument("--trials-planned", type=int, default=1,
                   help="本假设计划/已做的试验次数，用于多重检验校正")
    r.add_argument("--tags", nargs="*", default=[])
    r.set_defaults(func=cmd_register)

    ls = sub.add_parser("list", help="列出假设")
    ls.add_argument("--status", choices=VALID_STATUSES)
    ls.set_defaults(func=cmd_list)

    sh = sub.add_parser("show", help="查看单条假设与其变更历史")
    sh.add_argument("hyp_id")
    sh.set_defaults(func=cmd_show)

    st = sub.add_parser("status", help="变更状态（追加记录，不删除）")
    st.add_argument("hyp_id")
    st.add_argument("status", choices=VALID_STATUSES)
    st.add_argument("--note", default=None)
    st.set_defaults(func=cmd_status)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
