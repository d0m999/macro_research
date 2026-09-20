#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 SEC XBRL 抓取四大云厂季度 CAPEX（现金流量表口径）
====================================================

用途
----
为 Herman Jin 观点 2「需求是乘法，供给是加法」的**需求端**提供一手数据。
CAPEX 是他逻辑链里的显式中间变量：「云厂商和国家资本被迫持续增加 CAPEX」。

口径
----
- 来源：SEC XBRL companyconcept API（一手，免费，无需 key）。
- 标签：MSFT / GOOGL / META 用 `PaymentsToAcquirePropertyPlantAndEquipment`；
  AMZN 用 `PaymentsToAcquireProductiveAssets`（其现金流量表对应行）。
- **关键：10-Q 现金流量表披露的是年初至今（YTD）累计值，不是单季值。**
  直接筛"跨度 80–100 天"的记录只能捞到天然等于单季的 Q1 —— 这正是第一版
  错误（CSV 里每年只有一行）的成因。正确做法是**按财年做差分**：
      Q1 = YTD(Q1)；Q2 = YTD(H1) − YTD(Q1)；Q3 = YTD(9M) − YTD(H1)；Q4 = YTD(FY) − YTD(9M)
  差分结果再与显式单季记录交叉验证（实测完全一致，如 AMZN 2025Q2：
  57,202 − 25,019 = 32,183 = 其自报的 CY2025Q2 frame 值）。
- 财年差异不影响结果：一律按**期末日期**归属日历季度，故 MSFT 的 6 月财年
  （FY2026Q1 止于 2025-09-30）自动落到 CY2025Q3。
- 同一 (start, end) 若有多条（修订/重述），取 `filed` 日期最新的一条。

输出
----
research/data-hyperscaler-capex-quarterly.csv  —— 四家 × 季度，单位：百万美元

注意
----
CAM（计算机设备）等租赁口径不在此表的现金流 CAPEX 内；它是四家自报的
"property and equipment / productive assets" 付款额，四家之间可比，但
**与卖方常用的 "AI capex" 口径（含融资租赁）可能不同**，引用时须标注。
"""

import csv
import datetime as dt
import json
import subprocess
from pathlib import Path

UA = "VibeTrading Research research@example.com"
ENTITIES = {
    "MSFT": ("0000789019", "PaymentsToAcquirePropertyPlantAndEquipment"),
    "AMZN": ("0001018724", "PaymentsToAcquireProductiveAssets"),
    "GOOGL": ("0001652044", "PaymentsToAcquirePropertyPlantAndEquipment"),
    "META": ("0001326801", "PaymentsToAcquirePropertyPlantAndEquipment"),
}

OUT_CSV = Path(__file__).with_name("data-hyperscaler-capex-quarterly.csv")
OUT_JSON = Path(__file__).with_name("data-hyperscaler-capex-quarterly.json")


def fetch(cik: str, tag: str) -> dict:
    """用 curl 取数：macOS 上 python.org 的 Python 常缺根证书，python-ssl 会 CERTIFICATE_VERIFY_FAILED。"""
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json"
    raw = subprocess.run(
        ["curl", "-sS", "-m", "40", "-H", f"User-Agent: {UA}", url],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(raw)


def quarter_of(d: dt.date) -> str:
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


def dedupe(records: list) -> dict:
    """同一 (start, end) 取 filed 最新的一条（含重述）。"""
    uniq: dict[tuple, dict] = {}
    for r in records:
        if not r.get("start") or not r.get("end"):
            continue
        k = (r["start"], r["end"])
        if k not in uniq or r["filed"] > uniq[k]["filed"]:
            uniq[k] = r
    return uniq


# 单季 / H1 / 9M / FY 四档跨度（天）。52/53 周财年会让跨度有 ±7 天浮动，故留足区间。
SPAN_BUCKETS = [(80, 100), (170, 195), (260, 285), (350, 375)]


def bucket_of(span: int):
    for i, (lo, hi) in enumerate(SPAN_BUCKETS):
        if lo <= span <= hi:
            return i
    return None


def extract_quarters(raw: dict) -> dict[str, float]:
    """把 YTD 累计序列差分成单季度；再用显式单季度记录覆盖/校验。

    坑（第一版踩过两次）：
      1. 10-Q 现金流量表是 YTD 累计，直接筛"90 天左右"只能捞到 Q1。
      2. **不能按 start 简单分组后顺序差分** —— 同一 start 下会混杂 364 天滚动
         TTM 记录（实例 AMZN：start=2024-07-01 组内是 91d 与 364d 两条，
         差分后 85,036 被当成 2025Q2，把自报的 32,183 覆盖掉，偏差 3 倍）。
    正解：按**跨度分档**（单季/H1/9M/FY），档位必须连续可差分；链条一断即停。
    """
    uniq = dedupe(raw["units"]["USD"])

    by_start: dict[str, list] = {}
    for (s, _e), r in uniq.items():
        by_start.setdefault(s, []).append(r)

    quarterly: dict[str, tuple[float, str]] = {}
    for s, rows in by_start.items():
        # 每档只留一条（同档多条取 filed 最新）
        buckets: dict[int, dict] = {}
        for r in rows:
            span = (dt.date.fromisoformat(r["end"])
                    - dt.date.fromisoformat(s)).days
            b = bucket_of(span)
            if b is None:
                continue
            if b not in buckets or r["filed"] > buckets[b]["filed"]:
                buckets[b] = r
        if 0 not in buckets:                 # 没有单季档 ⇒ 不是财年累计序列
            continue
        prev = 0.0
        for b in sorted(buckets):
            if b > 0 and (b - 1) not in buckets:
                break                        # 档位不连续 ⇒ 链条断裂，停止
            r = buckets[b]
            seg = r["val"] - prev
            if seg < 0:
                break
            q = quarter_of(dt.date.fromisoformat(r["end"]))
            v = seg / 1e6                    # → 百万美元
            if q not in quarterly or r["filed"] > quarterly[q][1]:
                quarterly[q] = (v, r["filed"])
            prev = r["val"]

    # 显式单季度记录（跨度落在单季档）：最可靠来源，用于覆盖 + 交叉验证
    explicit: dict[str, tuple[float, str]] = {}
    for (s, e), r in uniq.items():
        span = (dt.date.fromisoformat(e) - dt.date.fromisoformat(s)).days
        if bucket_of(span) == 0:
            q = quarter_of(dt.date.fromisoformat(e))
            if q not in explicit or r["filed"] > explicit[q][1]:
                explicit[q] = (r["val"] / 1e6, r["filed"])

    check = [(q, quarterly[q][0], v) for q, (v, _f) in explicit.items()
             if q in quarterly]
    quarterly = {q: v for q, (v, _f) in quarterly.items()}   # 先降为纯值备覆盖
    merged = dict(quarterly)
    merged.update({q: v for q, (v, _f) in explicit.items()})

    # 自检：差分值与自报值应完全一致
    if check:
        worst = max(abs(a - b) for _q, a, b in check)
        print(f"    校验：{len(check)} 个季度同时有差分值与自报值，"
              f"最大偏差 {worst:.1f} 百万美元")
        for q, a, b in sorted(check):
            if abs(a - b) > 1:
                print(f"      ! {q}: 差分 {a:,.0f} vs 自报 {b:,.0f}")

    return merged


def main() -> None:
    series: dict[str, dict[str, float]] = {}
    for name, (cik, tag) in ENTITIES.items():
        print(f"{name}:")
        series[name] = extract_quarters(fetch(cik, tag))
        ks = sorted(series[name])
        print(f"    季度数 {len(ks)}  区间 {ks[0]} ~ {ks[-1]}")

    quarters = sorted({q for s in series.values() for q in s})
    covered = [q for q in quarters if sum(q in series[n] for n in ENTITIES) >= 3]
    print(f"\n全部季度 {len(quarters)} 个；≥3 家齐备 {len(covered)} 个："
          f" {covered[0]} ~ {covered[-1]}\n")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["quarter", *ENTITIES, "TOTAL"])
        for q in sorted(quarters):
            if q not in covered:
                continue
            vals = [series[n][q] if q in series[n] else None for n in ENTITIES]
            tot = sum(v for v in vals if v is not None)
            if any(v is None for v in vals):        # 缺一家则不合计，避免口径漂移
                w.writerow([q, *[f"{v:.0f}" if v is not None else "" for v in vals],
                            f"{tot:.0f}*"])
            else:
                w.writerow([q, *[f"{v:.0f}" for v in vals], f"{tot:.0f}"])
    print(f"written: {OUT_CSV}")

    OUT_JSON.write_text(json.dumps(
        {"unit": "USD millions", "series": series,
         "note": "derived from YTD cumulative cash-flow values by differencing"},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"written: {OUT_JSON}")

    print("\n日历年度合计（百万美元；2026 仅 H1）")
    for y in range(2021, 2027):
        row = []
        for n in ENTITIES:
            qs = [q for q in series[n] if q.startswith(str(y))]
            row.append(sum(series[n][q] for q in qs) if qs else 0.0)
        tag = "H1" if y == 2026 else "FY"
        print(f"  {y}{tag:3s} " + "  ".join(f"{n}={v:>9,.0f}" for n, v in zip(ENTITIES, row))
              + f"   TOTAL={sum(row):>10,.0f}")
        if y == 2026:
            continue
        prev = []
        for n in ENTITIES:
            qs = [q for q in series[n] if q.startswith(str(y - 1))]
            prev.append(sum(series[n][q] for q in qs) if qs else 0.0)
        if sum(prev) and y >= 2022:
            print(f"        YoY: " + "  ".join(
                f"{n}={(v / p - 1) * 100:+.0f}%" if p else f"{n}=n/a"
                for n, v, p in zip(ENTITIES, row, prev))
                + f"   TOTAL={(sum(row) / sum(prev) - 1) * 100:+.0f}%")


if __name__ == "__main__":
    main()
