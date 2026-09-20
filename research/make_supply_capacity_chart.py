#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
观点 2 供给端产能爬坡图（横轴年份 / 纵轴产能）
==============================================

对标的口径
----------
Herman Jin 观点 2：「AI 算力需求是乘法，供给是加法——所以半导体是结构性卖方市场」。
本图只画**供给端**，并直接检验「供给是加法」这一半命题是否成立。

为什么必须分面板
----------------
1) 两个供给品的**单位不可相加**：TSMC 的供给品是 CoWoS 先进封装产能（千片/月，kwpm），
   存储三家的供给品是 HBM 比特出货量（bn Gb）。混在一根纵轴上没有物理意义。
2) HBM 存在**两个冲突口径**（UBS 三家合计 vs 交银国际行业总出货），已判定 UBS 高估
   25–50%（rollup 观点 2 复核 Problem 2），故必须分开绘制并标注，不能平均。

数据源
------
全部取自 `Herman-Jin 观点 rollup.md` 观点 2「供给端产能爬坡独立复核」表 1/表 2，
为**卖方预测与产业链调研口径，非公司审计数据**。个案来源逐点标注在图上。

核心结论（Panel C）
-------------------
「加法」= 绝对增量恒定 ⇒ YoY 增速按 1/t 递减；「乘法」= 增速恒定。
实测两条独立的供给曲线（CoWoS 与 HBM）增速路径几乎重合，且**单调递减**：
    CoWoS  133% → 107% → 66% → 49% → 32%
    HBM      —     —    89% → 47% → 36%
以恒定 CAGR 73.4%（CoWoS 首尾锚定）为「乘法」参考线，可见供给增速在 2027 年
**向下穿越乘法线、收敛至加法线** —— 即「供给是加法」在爬坡后段成立，但在
2025–2026 的瓶颈突破期，供给本身更接近乘法。这解释了他 2025 年假设的「纯线性」
为何偏慢。

输出：research/supply-capacity-cowos-hbm-2023-2028.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "STHeiti", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).with_name("supply-capacity-cowos-hbm-2023-2028.png")

INK = "#1a1f24"
MUTE = "#5b6570"
FAINT = "#8b959f"
GRID = "#dde2e7"

C_TSMC = "#1f5c99"      # 台积电 CoWoS
C_IND = "#c05621"       # 行业总产能（含 OSAT）
C_HBM = "#7b3fb5"       # 交银口径：行业总出货（可信）
C_UBS = "#8b959f"       # UBS 三家合计（高估，灰色）
C_SS = "#2f9e8f"        # Samsung
C_HY = "#d4762a"        # SK Hynix
C_MU = "#4a7fb5"        # Micron

C_ADD = "#b3261e"       # 加法参考线
C_MUL = "#2f6fd0"       # 乘法参考线
C_DEM = "#c9a227"       # 需求侧（BofA）

YEARS = [2023, 2024, 2025, 2026, 2027, 2028]

# ---------------------------------------------------------------------------
# 1. CoWoS 先进封装（kwpm = 千片/月，年底产能口径）
# ---------------------------------------------------------------------------
COWOS_MID = {2023: 15.0, 2024: 35.0, 2025: 72.5, 2026: 120.0, 2027: 178.5, 2028: 235.0}
COWOS_LO = {2025: 70.0, 2026: 100.0, 2027: 160.0, 2028: 220.0}
COWOS_HI = {2025: 75.0, 2026: 140.0, 2027: 197.0, 2028: 250.0}
# 各家点名预测（散点，展示预测分歧）
COWOS_CALLS = [
    (2026, 105), (2026, 115), (2026, 130), (2026, 140),
    (2027, 170), (2027, 175), (2027, 197),
    (2028, 220), (2028, 250),
]
COWOS_IND = {2026: 160.0, 2027: 250.0}   # 行业总产能（UBS 2026-07-01，含 OSAT）

# ---------------------------------------------------------------------------
# 2. HBM 出货量（bn Gb；1 EB = 8 bn Gb）
# ---------------------------------------------------------------------------
HBM_TOTAL = {2025: 21.6, 2026: 40.8, 2027: 60.0, 2028: 81.6}   # 交银国际 2026-08-03
HBM_UBS = {2024: 12.8, 2025: 27.3, 2026: 39.0}                 # UBS 2025-09-18（高估）
HBM_VENDORS = {                                                # UBS，Samsung 取下修值
    "Samsung": (C_SS, {2024: 5.1, 2025: 8.6, 2026: 9.7}),
    "SK Hynix": (C_HY, {2024: 6.8, 2025: 13.0, 2026: 17.6}),
    "Micron": (C_MU, {2024: 0.9, 2025: 5.7, 2026: 8.8}),
}

# ---------------------------------------------------------------------------
# 3. 增速检验
# ---------------------------------------------------------------------------
def yoy(series: dict) -> dict:
    out = {}
    ks = sorted(series)
    for a, b in zip(ks, ks[1:]):
        out[b] = series[b] / series[a] - 1.0
    return out


COWOS_YOY = yoy(COWOS_MID)
HBM_YOY = yoy(HBM_TOTAL)

# 「加法」参考线：2023→2028 线性（绝对增量恒定 = +44 kwpm/年）
ADD_LINE = {y: 15.0 + 44.0 * (y - 2023) for y in YEARS}
ADD_YOY = yoy(ADD_LINE)
# 「乘法」参考线：恒定 CAGR（首尾锚定）
CAGR = (COWOS_MID[2028] / COWOS_MID[2023]) ** (1 / 5) - 1   # ≈ 73.4%
MUL_YOY = {y: CAGR for y in YEARS[1:]}

# 供需增速对比（BofA 2026-05-21）
BALANCE = [(2026, 0.59, 0.92), (2027, 0.68, 0.54)]


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
    ax.set_xlim(2022.55, 2028.8)
    ax.set_xticks(YEARS)
    ax.set_xticklabels([f"{y}" if y < 2026 else f"{y}E" for y in YEARS],
                       fontsize=10.5, color=MUTE)
    for y in YEARS:
        ax.axvline(y, color="#f1f4f7", linewidth=0.7, zorder=0)


def header(ax, title, note):
    """手工排版面板标题与脚注，避免与 matplotlib title 机制抢占同一空间。"""
    ax.text(0.0, 1.118, title, transform=ax.transAxes, fontsize=13.0,
            fontweight="bold", color=INK, ha="left", va="bottom")
    ax.text(0.0, 1.040, note, transform=ax.transAxes, fontsize=8.9,
            color=FAINT, ha="left", va="bottom")


fig = plt.figure(figsize=(14.6, 13.8), dpi=160)
gs = fig.add_gridspec(3, 1, height_ratios=[1.0, 1.0, 1.02], hspace=0.56,
                      left=0.070, right=0.958, top=0.888, bottom=0.100)

fig.text(0.070, 0.966, "观点 2 · 供给端产能爬坡：需求是乘法，供给是加法？",
         fontsize=19.5, fontweight="bold", color=INK, ha="left")
fig.text(0.070, 0.938,
         "横轴为年份，纵轴为供给品产能。三个面板同一时间轴；因单位不可相加，CoWoS（千片/月）与 HBM（bn Gb）分列。"
         "全部为卖方预测与产业链调研口径，非公司审计数据。",
         fontsize=10.2, color=MUTE, ha="left")

# ==================== Panel A：CoWoS ====================
axA = fig.add_subplot(gs[0])
style(axA, "CoWoS 产能（千片 / 月，年底）", (0, 312),
      [0, 50, 100, 150, 200, 250, 300])

band_x = [2025, 2026, 2027, 2028]
axA.fill_between(band_x, [COWOS_LO[y] for y in band_x],
                 [COWOS_HI[y] for y in band_x],
                 color=C_TSMC, alpha=0.10, zorder=2, linewidth=0)
axA.plot(band_x, [COWOS_LO[y] for y in band_x], color=C_TSMC, linewidth=0.9,
         alpha=0.45, zorder=3)
axA.plot(band_x, [COWOS_HI[y] for y in band_x], color=C_TSMC, linewidth=0.9,
         alpha=0.45, zorder=3)

mx = sorted(COWOS_MID)
axA.plot(mx, [COWOS_MID[y] for y in mx], color=C_TSMC, linewidth=3.2, zorder=6,
         marker="o", markersize=8.0, markerfacecolor="white",
         markeredgecolor=C_TSMC, markeredgewidth=2.6)
for y in mx:
    # 2026 上方要让位给行业总产能标记，故改标在点下方
    off = (0, -21) if y == 2026 else (0, 13)
    axA.annotate(f"{COWOS_MID[y]:g}", xy=(y, COWOS_MID[y]), xytext=off,
                 textcoords="offset points", ha="center", fontsize=10.2,
                 fontweight="bold", color=C_TSMC, zorder=9)

for y, v in COWOS_CALLS:
    axA.plot([y], [v], marker="o", markersize=4.0, color=C_TSMC, alpha=0.50,
             zorder=5)

ix = sorted(COWOS_IND)
axA.plot(ix, [COWOS_IND[y] for y in ix], color=C_IND, linewidth=1.9,
         linestyle=(0, (4, 2.6)), zorder=7, marker="s", markersize=7.2,
         markerfacecolor="white", markeredgecolor=C_IND, markeredgewidth=2.0)
axA.annotate("~160", xy=(2026, 160), xytext=(13, -3), textcoords="offset points",
             fontsize=9.4, fontweight="bold", color=C_IND, va="center", zorder=9)
axA.annotate("行业总产能（含 OSAT，UBS）\n2026 ~160 · 2027 ~250",
             xy=(2027, 250), xytext=(2025.58, 272),
             fontsize=9.6, color=C_IND, fontweight="bold", ha="left", va="center",
             linespacing=1.45, zorder=9,
             arrowprops=dict(arrowstyle="->", color=C_IND, linewidth=1.25,
                             connectionstyle="arc3,rad=-0.2"))

header(axA, "① CoWoS 先进封装：5 年约 15.7 倍，但斜率在放缓",
       "实线 = 台积电中值（各家预测区间的中点）；浅蓝带 = 预测区间；小圆点 = 各家点名预测；"
       "方点虚线 = 行业总产能（含 OSAT）。2023–2025 为单点口径，无区间。")
axA.text(2022.72, 296,
         "台积电占行业总产能：2026 ≈ 75%　2027 ≈ 71%",
         fontsize=9.3, color=MUTE, ha="left", va="top")
axA.text(2026.04, 44,
         "年绝对增量（kwpm）\n+20 → +37.5 → +47.5 → +58.5 → +56.5\n"
         "递增后趋稳，并非恒定：前段是瓶颈突破，后段才进入线性节奏",
         fontsize=9.0, color=MUTE, ha="left", va="center", linespacing=1.5,
         bbox=dict(boxstyle="round,pad=0.45", facecolor="#f4f7fa",
                   edgecolor="#cfdae6", linewidth=0.9), zorder=9)

# ==================== Panel B：HBM ====================
axB = fig.add_subplot(gs[1])
style(axB, "HBM 出货量（bn Gb）", (0, 122), [0, 20, 40, 60, 80, 100])

tx = sorted(HBM_TOTAL)
axB.plot(tx, [HBM_TOTAL[y] for y in tx], color=C_HBM, linewidth=3.2, zorder=7,
         marker="o", markersize=8.4, markerfacecolor="white",
         markeredgecolor=C_HBM, markeredgewidth=2.7)
for y in tx:
    axB.annotate(f"{HBM_TOTAL[y]:g}", xy=(y, HBM_TOTAL[y]), xytext=(0, 13),
                 textcoords="offset points", ha="center", fontsize=10.2,
                 fontweight="bold", color=C_HBM, zorder=9)

ux = sorted(HBM_UBS)
axB.plot(ux, [HBM_UBS[y] for y in ux], color=C_UBS, linewidth=1.9,
         linestyle=(0, (4, 2.6)), zorder=6, marker="s", markersize=7.0,
         markerfacecolor="white", markeredgecolor=C_UBS, markeredgewidth=1.9)
axB.annotate("UBS 三家合计（2025-09-18）\n已判定高估 25–50%，不作主线",
             xy=(2025, 27.3), xytext=(2022.98, 44.0),
             fontsize=9.4, color=C_UBS, ha="left", va="center", linespacing=1.45,
             zorder=9,
             arrowprops=dict(arrowstyle="->", color=C_UBS, linewidth=1.2,
                             connectionstyle="arc3,rad=0.22"))

for name, (c, ser) in HBM_VENDORS.items():
    ks = sorted(ser)
    axB.plot(ks, [ser[y] for y in ks], color=c, linewidth=1.15, alpha=0.72,
             linestyle=(0, (2, 2)), zorder=4, marker="o", markersize=4.6,
             markerfacecolor="white", markeredgecolor=c, markeredgewidth=1.4)

legB = axB.legend(handles=[
    Line2D([], [], color=C_HBM, lw=3.0, marker="o", markersize=7,
           markerfacecolor="white", markeredgecolor=C_HBM, markeredgewidth=2.2,
           label="行业总出货（交银国际 2026-08-03）"),
    Line2D([], [], color=C_UBS, lw=1.9, ls=(0, (4, 2.6)), marker="s", markersize=6,
           markerfacecolor="white", markeredgecolor=C_UBS, markeredgewidth=1.7,
           label="三家合计（UBS 2025-09-18，高估）"),
    Line2D([], [], color=C_HY, lw=1.35, ls=(0, (2, 2)), marker="o", markersize=4,
           markerfacecolor="white", markeredgecolor=C_HY, markeredgewidth=1.3,
           label="SK Hynix / Samsung / Micron 分列（UBS）"),
], loc="upper left", bbox_to_anchor=(0.004, 0.995), fontsize=9.2,
    frameon=True, framealpha=0.96, edgecolor=GRID, borderpad=0.65)
legB.get_frame().set_facecolor("white")

header(axB, "② HBM：3 年约 3.8 倍，但两个口径冲突达 25–50%，必须分开看",
       "实线 = 交银国际行业总出货（原始单位 2.7 / 5.1 / 7.5 / 10.2 EB，按 1 EB = 8 bn Gb 换算）；"
       "灰色虚线 = UBS 三家合计（高估）；细虚线 = UBS 三家分列。")
axB.text(2026.06, 118,
         "物理产能口径（UBS）：2026 年底 ≈ 230k wpm → 2027 年底 ≈ 270k wpm，仅 +17%；\n"
         "同期出货量 +47% —— 增量靠良率与堆叠层数，而非单纯扩产",
         fontsize=9.0, color=MUTE, ha="left", va="top", linespacing=1.5)

# ==================== Panel C：增速检验 ====================
axC = fig.add_subplot(gs[2])
style(axC, "同比增速（%）", (-8, 196), [0, 50, 100, 150])

# 加法参考线自 2025 起绘制：2024 的值（+293%）是线性锚定首年的伪影，画出会被 y 轴截断而失真
ADD_YOY_PLOT = {y: v for y, v in ADD_YOY.items() if y >= 2025}
axC.plot(sorted(ADD_YOY_PLOT), [ADD_YOY_PLOT[y] * 100 for y in sorted(ADD_YOY_PLOT)],
         color=C_ADD, linewidth=1.7, linestyle=(0, (5, 2.5)), zorder=4)
axC.plot(sorted(MUL_YOY), [MUL_YOY[y] * 100 for y in sorted(MUL_YOY)],
         color=C_MUL, linewidth=1.7, linestyle=(0, (1.6, 2.2)), zorder=4)

w = 0.32
cy = sorted(COWOS_YOY)
axC.bar([y - 0.20 for y in cy], [COWOS_YOY[y] * 100 for y in cy], width=w,
        color=C_TSMC, alpha=0.90, zorder=6)
hy = sorted(HBM_YOY)
axC.bar([y + 0.20 for y in hy], [HBM_YOY[y] * 100 for y in hy], width=w,
        color=C_HBM, alpha=0.90, zorder=6)

for y in cy:
    axC.annotate(f"+{COWOS_YOY[y] * 100:.0f}%", xy=(y - 0.20, COWOS_YOY[y] * 100),
                 xytext=(0, 4), textcoords="offset points", ha="center",
                 fontsize=9.6, fontweight="bold", color=C_TSMC, zorder=9)
for y in hy:
    axC.annotate(f"+{HBM_YOY[y] * 100:.0f}%", xy=(y + 0.20, HBM_YOY[y] * 100),
                 xytext=(0, 4), textcoords="offset points", ha="center",
                 fontsize=9.6, fontweight="bold", color=C_HBM, zorder=9)

for y, sup, dem in BALANCE:
    axC.plot([y + 0.44], [dem * 100], marker="*", markersize=15, color=C_DEM,
             zorder=8, markeredgecolor="#8a6d1a", markeredgewidth=0.8)
    axC.annotate(f"需求\n+{dem * 100:.0f}%", xy=(y + 0.44, dem * 100),
                 xytext=(0, 11), textcoords="offset points", ha="center",
                 fontsize=8.8, color="#8a6d1a", fontweight="bold",
                 linespacing=1.3, zorder=9)

axC.annotate("供给增速在此穿越「乘法」参考线\n→ 由准乘法节奏转入加法节奏",
             xy=(2027, 50), xytext=(2022.85, 160),
             fontsize=9.6, color=INK, fontweight="bold", ha="left", va="center",
             linespacing=1.55, zorder=12,
             bbox=dict(boxstyle="round,pad=0.5", facecolor="#fdf8f2",
                       edgecolor="#e0c9a8", linewidth=1.0),
             arrowprops=dict(arrowstyle="->", color="#b08a55", linewidth=1.4,
                             connectionstyle="arc3,rad=-0.24"))

header(axC, "③ 检验「供给是加法」：增速单调递减，2027 年起收敛至加法线",
       "柱 = 供给端同比增速（CoWoS 取中值；HBM 取交银口径）；红虚线 = 加法参考（+44 kwpm/年）；"
       "蓝点线 = 乘法参考（CoWoS 锚定 73.4%／HBM 55.9%，HBM 于 2026E 穿越）；★ = BofA 供需增速")
axC.text(2022.72, 193,
         "两条独立供给曲线（CoWoS 与 HBM）增速路径几乎重合，且逐年单调递减。",
         fontsize=9.2, color=MUTE, ha="left", va="top")

legC = axC.legend(handles=[
    Line2D([], [], color=C_TSMC, lw=9, alpha=0.90, label="CoWoS 产能 YoY"),
    Line2D([], [], color=C_HBM, lw=9, alpha=0.90, label="HBM 出货量 YoY"),
    Line2D([], [], color=C_ADD, lw=1.7, ls=(0, (5, 2.5)), label="加法参考（增量恒定）"),
    Line2D([], [], color=C_MUL, lw=1.7, ls=(0, (1.6, 2.2)), label="乘法参考（CoWoS 锚定 73.4%；HBM 对应 55.9%）"),
    Line2D([], [], color=C_DEM, marker="*", lw=0, markersize=12,
           markeredgecolor="#8a6d1a", label="需求侧增速（BofA，独立口径）"),
], loc="upper right", fontsize=9.3, frameon=True, framealpha=0.96,
    edgecolor=GRID, borderpad=0.7)
legC.get_frame().set_facecolor("white")

fig.text(0.070, 0.058,
         "数据源：`Herman-Jin 观点 rollup.md` 观点 2「供给端产能爬坡独立复核」表 1 / 表 2（经卖方研报库检索，2026-09-17）。"
         "个案：台积电 2023–2025 与 2028 为 Jefferies / JPMorgan / UBS / Bernstein 点名预测；行业总产能为 UBS 2026-07-01（含 OSAT）；",
         fontsize=8.6, color=FAINT, ha="left", va="top", linespacing=1.6)
fig.text(0.070, 0.040,
         "HBM 行业总出货为交银国际 2026-08-03（原始单位 EB，按 1 EB = 8 bn Gb 换算）；HBM 物理产能与供需增速对比为 UBS 2026-08-07 / BofA 2026-05-21。",
         fontsize=8.6, color=FAINT, ha="left", va="top", linespacing=1.6)
fig.text(0.070, 0.020,
         "口径限制：2026 年及以后均为卖方预测（标 E），非实际值；CoWoS 与 HBM 单位不同，禁止相加或折算为同一总量。本图为供给端产能盘点，不构成投资建议。",
         fontsize=8.6, color=FAINT, ha="left", va="top", linespacing=1.6)

fig.savefig(OUT, facecolor="white")
print(f"written: {OUT}")
