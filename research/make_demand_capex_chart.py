#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
观点 2 需求端：Hyperscaler CAPEX —— 与供给端产能的增速对决
==========================================================

对标的口径
----------
Herman Jin 观点 2：「AI 算力需求是**乘法**，供给是**加法**」。
供给端已单独成图（`supply-capacity-cowos-hbm-2023-2028.png`）；本图补上**需求端**，
并让两侧在同一年度轴上对照，检验缺口是在扩大还是在收敛。

需求端代理变量为什么选 CAPEX
----------------------------
他逻辑链里需求侧的可观测中间变量是「云厂商和国家资本被迫持续增加 CAPEX」——
这是公开、可审计、四家可比的一手数据（其余如 Token 使用量无连贯官方序列）。
本图测的因此是**需求意愿的强度**，不是最终算力消耗；两者的差别见脚注。

数据源
------
- 需求：SEC XBRL（10-Q/10-K 现金流量表），由 `fetch_hyperscaler_capex.py` 抓取。
  四家 = MSFT / AMZN / GOOGL / META；`PaymentsToAcquirePropertyPlantAndEquipment`
  （AMZN 用 `PaymentsToAcquireProductiveAssets`）。单位：百万美元。
  ⚠️ 现金流口径的 property & equipment 付款额，**不含融资租赁**所购算力；
  引用卖方「AI CAPEX」时须注意口径差异。
- 云收入增速：公司披露 YoY（SEC 8-K/6-K 附件与 IR 财报稿）。
- 供给：CoWoS / HBM，取自 `supply-capacity-notes-2026-09-17.md`。

输出：research/demand-capex-vs-supply-2023-2026.png
"""

import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "STHeiti", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

HERE = Path(__file__).parent
OUT = HERE / "demand-capex-vs-supply-2023-2026.png"
CSV_PATH = HERE / "data-hyperscaler-capex-quarterly.csv"
JSON_PATH = HERE / "data-hyperscaler-capex-quarterly.json"

INK = "#1a1f24"
MUTE = "#5b6570"
FAINT = "#8b959f"
GRID = "#dde2e7"

C = {"MSFT": "#5a6b7b", "AMZN": "#e08a1e", "GOOGL": "#2f6fd0", "META": "#7b3fb5"}
C_TOT = "#b3261e"
C_ADD = "#b3261e"
C_MUL = "#2f6fd0"

# 供给端增速（与 supply-capacity-notes 一致）
COWOS_YOY = {2024: 1.333, 2025: 1.071, 2026: 0.655, 2027: 0.488, 2028: 0.317}
HBM_YOY = {2026: 0.889, 2027: 0.471, 2028: 0.360}

# 云收入增速（公司披露 YoY，%）—— 2023Q1 ~ 2026Q2
CLOUD_Q = ["2023Q1", "2023Q2", "2023Q3", "2023Q4",
           "2024Q1", "2024Q2", "2024Q3", "2024Q4",
           "2025Q1", "2025Q2", "2025Q3", "2025Q4",
           "2026Q1", "2026Q2"]
CLOUD = {
    "AWS": [16, 12, 12, 13, 17, 19, 19, 19, 17, 17, 20, 24, 28, 37],
    "Azure": [27, 26, 29, 30, 31, 29, 33, 31, 33, 39, 40, 39, 40, 43],
    "Google Cloud": [28, 28, 22, 26, 28, 29, 35, 30, 28, 32, 34, 48, 63, 82],
    "Alibaba Cloud": [-2, 4, 2, 3, 3, 6, 7, 13, 18, 26, 34, 36, 38, 45],
}


def load_capex() -> tuple[list[str], dict[str, list[float]]]:
    """优先读抓取脚本产出的 JSON；缺失则退回 CSV。"""
    if JSON_PATH.exists():
        d = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        series = d["series"]
        qs = sorted(q for q in {k for s in series.values() for k in s}
                    if any(q in series[n] for n in C))
        qs = [q for q in qs if q >= "2023Q1"
              and all(q in series[n] for n in C)]
        return qs, {n: [series[n][q] for q in qs] for n in C}
    names = list(C)
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    qs = [r["quarter"] for r in rows if r["quarter"] >= "2023Q1"
          and all(r[n] for n in names)]
    idx = {r["quarter"]: r for r in rows}
    return qs, {n: [float(idx[q][n]) for q in qs] for n in names}


QS, CAPEX = load_capex()
TOT = [sum(CAPEX[n][i] for n in C) / 1000 for i in range(len(QS))]     # → $B
CAPEX_B = {n: [v / 1000 for v in CAPEX[n]] for n in C}

# 季度同比（合计）
YOY_Q, YOY_LAB = [], []
for i, q in enumerate(QS):
    y, qq = int(q[:4]), int(q[-1])
    py = f"{y - 1}Q{qq}"
    if py in QS:
        j = QS.index(py)
        YOY_Q.append((i, (TOT[i] / TOT[j] - 1) * 100))
        YOY_LAB.append(q)

# 年度需求增速
def year_total(y: int) -> float:
    return sum(v for q, v in zip(QS, TOT) if q.startswith(str(y)))


DEMAND_YOY = {}
for y in (2024, 2025):
    DEMAND_YOY[y] = year_total(y) / year_total(y - 1) - 1
# 2026 尚无全年，用 H1 vs H1（实测口径，不做年化假设）
_h1_26 = sum(v for q, v in zip(QS, TOT) if q.startswith("2026"))
_h1_25 = sum(v for q, v in zip(QS, TOT) if q.startswith("2025") and int(q[-1]) <= 2)
DEMAND_YOY[2026] = _h1_26 / _h1_25 - 1

YEARS_C = [2024, 2025, 2026, 2027, 2028]

COWOS_MID = {2023: 15.0, 2024: 35.0, 2025: 72.5, 2026: 120.0, 2027: 178.5, 2028: 235.0}
ADD_LINE = {y: 15.0 + 44.0 * (y - 2023) for y in [2023, 2024, 2025, 2026, 2027, 2028]}
CAGR = (COWOS_MID[2028] / COWOS_MID[2023]) ** (1 / 5) - 1


def header(ax, title, note):
    ax.text(0.0, 1.118, title, transform=ax.transAxes, fontsize=13.0,
            fontweight="bold", color=INK, ha="left", va="bottom")
    ax.text(0.0, 1.040, note, transform=ax.transAxes, fontsize=8.9,
            color=FAINT, ha="left", va="bottom")


def style(ax, ylab, ylim, yticks):
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.set_ylim(*ylim)
    ax.set_yticks(yticks)
    ax.set_ylabel(ylab, fontsize=10.5, color=MUTE, labelpad=8)
    ax.tick_params(axis="both", labelsize=10, colors=MUTE, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.85)
    ax.set_axisbelow(True)


fig = plt.figure(figsize=(14.6, 13.8), dpi=160)
gs = fig.add_gridspec(3, 1, height_ratios=[1.02, 0.96, 1.0], hspace=0.56,
                      left=0.072, right=0.958, top=0.888, bottom=0.102)

fig.text(0.072, 0.966, "观点 2 · 需求端 CAPEX：需求是乘法，供给是加法？",
         fontsize=19.5, fontweight="bold", color=INK, ha="left")
fig.text(0.072, 0.938,
         "需求侧用四大云厂 CAPEX（SEC 一手，现金流口径）作代理变量；供给侧沿用 CoWoS / HBM 产能。"
         "三面板同一主题：① 规模　② 需求增速的形状　③ 供需增速对决。",
         fontsize=10.2, color=MUTE, ha="left")

# ==================== Panel A：季度 CAPEX 堆叠 ====================
axA = fig.add_subplot(gs[0])
style(axA, "季度 CAPEX（十亿美元）", (0, 185), [0, 40, 80, 120, 160])
x = np.arange(len(QS))
bottom = np.zeros(len(QS))
for n in C:
    axA.bar(x, CAPEX_B[n], bottom=bottom, width=0.64, color=C[n], alpha=0.92,
            zorder=5, label=n, linewidth=0)
    bottom += np.array(CAPEX_B[n])
axA.plot(x, TOT, color=C_TOT, linewidth=2.0, marker="o", markersize=4.6,
         markerfacecolor="white", markeredgecolor=C_TOT, markeredgewidth=1.7,
         zorder=8)
for i in (0, len(QS) - 1):
    axA.annotate(f"{TOT[i]:.0f}", xy=(i, TOT[i]), xytext=(0, 12),
                 textcoords="offset points", ha="center", fontsize=10.4,
                 fontweight="bold", color=C_TOT, zorder=10)

axA.set_xlim(-0.7, len(QS) - 0.3)
axA.set_xticks(x)
axA.set_xticklabels(QS, fontsize=8.9, color=MUTE, rotation=0)
for i, q in enumerate(QS):
    if q.endswith("Q1"):
        axA.axvline(i - 0.5, color="#eef1f4", linewidth=1.0, zorder=0)

legA = axA.legend(loc="upper left", fontsize=9.6, frameon=True, framealpha=0.96,
                  edgecolor=GRID, borderpad=0.7, ncol=2)
legA.get_frame().set_facecolor("white")

header(axA, "① 需求端规模：2026Q2 单季投入已超过 2023 年全年",
       "堆叠柱 = 四家季度 CAPEX（SEC 10-Q/10-K 现金流量表，现金流口径，不含融资租赁）；红线 = 合计。")
axA.text(7.05, 176,
         "2026Q2 合计 165.0 bn ＞ 2023 全年 147.2 bn",
         fontsize=10.0, color=C_TOT, fontweight="bold", ha="left", va="top")

# ==================== Panel B：需求增速的形状 ====================
axB = fig.add_subplot(gs[1])
style(axB, "合计 CAPEX 同比增速（%）", (0, 108), [0, 25, 50, 75, 100])
xx = [i for i, _ in YOY_Q]
yy = [v for _, v in YOY_Q]
axB.bar(xx, yy, width=0.62, color="#c9a227", alpha=0.88, zorder=5,
        edgecolor="#8a6d1a", linewidth=0.6)
for i, v in zip(xx, yy):
    axB.annotate(f"+{v:.0f}%", xy=(i, v), xytext=(0, 4), textcoords="offset points",
                 ha="center", fontsize=9.6, fontweight="bold", color="#8a6d1a",
                 zorder=9)
axB.set_xlim(-0.7, len(QS) - 0.3)
axB.set_xticks(x)
axB.set_xticklabels(QS, fontsize=8.9, color=MUTE)
for i, q in enumerate(QS):
    if q.endswith("Q1"):
        axB.axvline(i - 0.5, color="#eef1f4", linewidth=1.0, zorder=0)

axB.annotate("若需求是「乘法」（增速恒定），这里应是一条水平线；\n"
             "实测增速从 +30% 一路升至 +87% —— 需求端比「乘法」更强",
             xy=(len(QS) - 1, 87), xytext=(6.2, 26),
             fontsize=9.8, color=INK, fontweight="bold", ha="left", va="center",
             linespacing=1.55, zorder=12,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#fdf8f2",
                       edgecolor="#e0c9a8", linewidth=1.0),
             arrowprops=dict(arrowstyle="->", color="#b08a55", linewidth=1.4,
                             connectionstyle="arc3,rad=-0.22"))

header(axB, "② 需求增速的形状：不仅没减速，反而在加速",
       "柱 = 四家合计 CAPEX 的季度同比；自 2024Q1 起可算（需上年同季）。")

# ==================== Panel C：供需增速对决 ====================
axC = fig.add_subplot(gs[2])
style(axC, "同比增速（%）", (-6, 152), [0, 30, 60, 90, 120, 150])

w = 0.26
pos = np.arange(len(YEARS_C))
dem = [DEMAND_YOY.get(y) for y in YEARS_C]
cow = [COWOS_YOY.get(y) for y in YEARS_C]
hbm = [HBM_YOY.get(y) for y in YEARS_C]

axC.bar(pos - w, [v * 100 if v is not None else 0 for v in dem], width=w,
        color=C_TOT, alpha=0.90, zorder=6, linewidth=0, label="需求：四大云厂 CAPEX")
axC.bar(pos, [v * 100 if v is not None else 0 for v in cow], width=w,
        color="#1f5c99", alpha=0.90, zorder=6, linewidth=0, label="供给：CoWoS 产能")
axC.bar(pos + w, [v * 100 if v is not None else 0 for v in hbm], width=w,
        color="#7b3fb5", alpha=0.90, zorder=6, linewidth=0, label="供给：HBM 出货量")

for i, v in enumerate(dem):
    if v is None:
        axC.text(pos[i] - w, 3, "无数据", ha="center", va="bottom", fontsize=8.6,
                 color=FAINT, rotation=90)
        continue
    lab = f"+{v * 100:.0f}%" + ("*" if YEARS_C[i] == 2026 else "")
    axC.annotate(lab, xy=(pos[i] - w, v * 100), xytext=(0, 4),
                 textcoords="offset points", ha="center", fontsize=9.8,
                 fontweight="bold", color=C_TOT, zorder=9)
for i, v in enumerate(cow):
    if v is None:
        continue
    axC.annotate(f"+{v * 100:.0f}%", xy=(pos[i], v * 100), xytext=(0, 4),
                 textcoords="offset points", ha="center", fontsize=9.8,
                 fontweight="bold", color="#1f5c99", zorder=9)
for i, v in enumerate(hbm):
    if v is None:
        continue
    axC.annotate(f"+{v * 100:.0f}%", xy=(pos[i] + w, v * 100), xytext=(0, 4),
                 textcoords="offset points", ha="center", fontsize=9.8,
                 fontweight="bold", color="#7b3fb5", zorder=9)

axC.set_xticks(pos)
axC.set_xticklabels([f"{y}" if y < 2026 else f"{y}E" for y in YEARS_C],
                    fontsize=10.5, color=MUTE)
axC.set_xlim(-0.62, len(YEARS_C) - 0.38)

axC.annotate("2026 年交点：需求增速（+84%）\n首次超过 CoWoS 供给增速（+66%）\n→ 缺口由收敛转为扩大",
             xy=(2 - w + 0.06, 84), xytext=(2.62, 132),
             fontsize=9.8, color=INK, fontweight="bold", ha="left", va="center",
             linespacing=1.55, zorder=12,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#fdf8f2",
                       edgecolor="#e0c9a8", linewidth=1.0),
             arrowprops=dict(arrowstyle="->", color="#b08a55", linewidth=1.4,
                             connectionstyle="arc3,rad=0.22"))

header(axC, "③ 供需增速对决：2026 年出现「需求增速反超供给增速」的交点",
       "需求 = 四大云厂 CAPEX 年度增速（2026 为 H1 vs H1，标 *）；供给 = CoWoS 产能 / HBM 出货量年度增速。"
       "两者基数与口径不同，仅可比较增速方向，不可相减得出缺口。")

legC = axC.legend(loc="upper left", fontsize=9.5, frameon=True, framealpha=0.96,
                  edgecolor=GRID, borderpad=0.7)
legC.get_frame().set_facecolor("white")

fig.text(0.072, 0.058,
         "数据源：需求 = SEC XBRL（`fetch_hyperscaler_capex.py` 抓取；单季值由 YTD 累计差分得到，"
         "并与公司自报单季值交叉校验，偏差 ≤1 百万美元）；供给 = Jefferies / JPMorgan / UBS / Bernstein / 交银国际"
         "（见供给端图说明文档）。",
         fontsize=8.6, color=FAINT, ha="left", va="top", linespacing=1.6)
fig.text(0.072, 0.040,
         "口径限制：① CAPEX 为现金流口径的 property & equipment 付款额，**不含融资租赁所购算力**，与卖方「AI CAPEX」口径可能不同；"
         "② CAPEX 是需求**意愿**的代理，不是最终算力消耗；",
         fontsize=8.6, color=FAINT, ha="left", va="top", linespacing=1.6)
fig.text(0.072, 0.020,
         "③ 2027 年及以后需求侧无一致预测，故留白；2026 年 6 月以后为卖方预测。本图为供需盘点，不构成投资建议。",
         fontsize=8.6, color=FAINT, ha="left", va="top", linespacing=1.6)

fig.savefig(OUT, facecolor="white")
print(f"written: {OUT}")
print(f"需求年度增速: " + "  ".join(f"{y}={DEMAND_YOY[y]*100:+.1f}%" for y in sorted(DEMAND_YOY)))
print(f"2026H1={_h1_26:.0f} vs 2025H1={_h1_25:.0f} → {DEMAND_YOY[2026]*100:+.1f}%")
print(f"季度同比: " + "  ".join(f"{q}={v:+.0f}%" for q, (_, v) in zip(YOY_LAB, YOY_Q)))
