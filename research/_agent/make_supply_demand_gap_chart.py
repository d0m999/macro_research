#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
观点 2 · 供需缺口怎么读
=======================

为什么需要这张图
----------------
已有的两张图（`supply-capacity-cowos-hbm-2023-2028.png`、
`demand-capex-vs-supply-2023-2026.png`）各自把「需求」和「供给」画清楚了，
但**都没有画缺口本身**——它们只把两侧并排放在同一条年份轴上。

读者想「看出缺口」，就必须自己做减法。而直接相减会踩两个坑：

  坑 1：量纲不同。需求是「百万美元」，供给是「千片/月」和「bn Gb」。
        垂直距离没有任何意义，任何"缺口金额"都是伪造量纲。
  坑 2：层级不同。CAPEX（钱）与 CoWoS 片数（物）之间隔着「单价 x 结构」，
        而 BofA 给的「需求 +54%」是晶圆片数口径，和 CAPEX 不是一回事。

  正解：缺口**只能存在于无量纲的增速空间**，单位是「百分点（pp）」。

本图要回答三件事
----------------
  ① 缺口 = 需求增速 - 有效供给增速；有效供给 = 互补品中**较紧**的那一个（min）。
  ② 缺口看**符号**，不看绝对值 —— 负 = 供给跑在前面，正 = 需求跑在前面。
  ③ 瓶颈归属：缺口的"边"由谁决定（2026 是先进封装，2027 后两者齐头并进）。

数据源
------
- 需求：四大云厂 CAPEX，SEC XBRL 一手（`data-hyperscaler-capex-quarterly.csv`，
        rollup 观点 2；原 notes 已于 2026-09-22 删除）。2026 为 H1 vs H1 实测口径，非年化。
- 供给：CoWoS / HBM，卖方口径（rollup 观点 2 表 1/表 2）。
        2026 及以后为预测值。

⚠️ 字体注意：Hiragino Sans GB **不含 U+2212（MINUS SIGN）字形**，负号必须用
   ASCII 连字符 `-`，否则渲染成豆腐块。本脚本已全部改用 ASCII 连字符。

输出：research/supply-demand-gap-2024-2027.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "STHeiti", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

HERE = Path(__file__).parent
OUT = HERE / "supply-demand-gap-2024-2027.png"

INK = "#1a1f24"
MUTE = "#5b6570"
FAINT = "#8b959f"
GRID = "#dde2e7"

C_DEM = "#b3261e"      # 需求
C_SUP = "#1f5c99"      # 有效供给（瓶颈）
C_COW = "#1f5c99"      # CoWoS
C_HBM = "#7b3fb5"      # HBM
C_LOOSE = "#3f7d54"    # 供给跑在前面（宽松）
C_TIGHT = "#b3261e"    # 需求跑在前面（紧张）

# ============================================================
# 数据（全部集中于此，改数不动绘图逻辑）
# ============================================================

# 需求：四大云厂 CAPEX 合计，同比（%）。2026 为 H1 vs H1。
DEM = {2024: 55.1, 2025: 64.7, 2026: 84.1}

# 供给：产能 / 出货量同比（%）
COWOS = {2024: 133.3, 2025: 107.1, 2026: 65.5, 2027: 48.8, 2028: 31.7}
HBM = {2026: 88.9, 2027: 47.1, 2028: 36.0}    # 交银口径，2025 及以前无同源基数


def effective_supply(y):
    """有效供给 = 互补品中较紧者（增速较低的那个）。"""
    vals = [d[y] for d in (COWOS, HBM) if y in d]
    return min(vals) if vals else None


SUP = {y: effective_supply(y) for y in (2024, 2025, 2026, 2027, 2028)}
GAP = {y: DEM[y] - SUP[y] for y in DEM if SUP.get(y) is not None}

YEARS_G = [2024, 2025, 2026]


def header(ax, title, note):
    ax.text(0.0, 1.112, title, transform=ax.transAxes, fontsize=13.0,
            fontweight="bold", color=INK, ha="left", va="bottom")
    ax.text(0.0, 1.034, note, transform=ax.transAxes, fontsize=8.9,
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


fig = plt.figure(figsize=(14.6, 14.2), dpi=160)
gs = fig.add_gridspec(3, 1, height_ratios=[1.08, 0.90, 1.00], hspace=0.62,
                      left=0.076, right=0.958, top=0.884, bottom=0.146)

fig.text(0.076, 0.963, "观点 2 · 供需缺口怎么读：缺口只存在于「增速」维度",
         fontsize=19.5, fontweight="bold", color=INK, ha="left")
fig.text(0.076, 0.935,
         "两张原图各自都没画缺口——它们只把需求与供给并排放在同一条年份轴上。"
         "本图补上那一步减法，并说明减法只能在无量纲的增速空间里做。",
         fontsize=10.2, color=MUTE, ha="left")

# ==================== Panel A：缺口的两条边 ====================
axA = fig.add_subplot(gs[0])
style(axA, "同比增速（%）", (14, 172), [30, 60, 90, 120, 150])

xs = np.array(YEARS_G, dtype=float)
dm = np.array([DEM[y] for y in YEARS_G], dtype=float)
sp = np.array([SUP[y] for y in YEARS_G], dtype=float)

axA.fill_between(xs, dm, sp, where=(sp >= dm), interpolate=True,
                 color=C_LOOSE, alpha=0.20, zorder=2, linewidth=0)
axA.fill_between(xs, dm, sp, where=(dm >= sp), interpolate=True,
                 color=C_TIGHT, alpha=0.22, zorder=2, linewidth=0)

axA.plot(xs, sp, color=C_SUP, linewidth=3.0, marker="s", markersize=7.4,
         markerfacecolor="white", markeredgecolor=C_SUP, markeredgewidth=2.4,
         zorder=8, label="有效供给增速（互补品中较紧者）")
axA.plot([2026.0, 2027.0], [SUP[2026], SUP[2027]], color=C_SUP, linewidth=2.0,
         linestyle=(0, (3, 3)), marker="s", markersize=6.4, markerfacecolor="white",
         markeredgecolor=C_SUP, markeredgewidth=1.8, alpha=0.75, zorder=7)
axA.plot(xs, dm, color=C_DEM, linewidth=3.0, marker="o", markersize=7.4,
         markerfacecolor="white", markeredgecolor=C_DEM, markeredgewidth=2.4,
         zorder=9, label="需求增速（四大云厂 CAPEX）")

for xv, v in zip(YEARS_G, dm):
    axA.annotate(f"+{v:.0f}%", xy=(xv, v), xytext=(0, 15),
                 textcoords="offset points", ha="center", fontsize=10.6,
                 fontweight="bold", color=C_DEM, zorder=11)
for xv, v in zip(YEARS_G, sp):
    axA.annotate(f"+{v:.0f}%", xy=(xv, v), xytext=(0, -22),
                 textcoords="offset points", ha="center", fontsize=10.6,
                 fontweight="bold", color=C_SUP, zorder=11)
axA.annotate("+47%\n(2027E)", xy=(2027, SUP[2027]), xytext=(0, -26),
             textcoords="offset points", ha="center", fontsize=9.4,
             color=C_SUP, alpha=0.85, zorder=11, linespacing=1.4)

axA.text(2024.58, 90, "缺口 -78pp\n（供给跑在前面）", ha="center", va="center",
         fontsize=10.4, fontweight="bold", color=C_LOOSE, linespacing=1.55,
         zorder=12)
axA.annotate("缺口 +18.6pp\n（需求反超）", xy=(2026, 76.5), xytext=(2026.30, 116),
             fontsize=10.4, fontweight="bold", color=C_TIGHT, ha="center",
             va="bottom", linespacing=1.55, zorder=12,
             arrowprops=dict(arrowstyle="->", color=C_TIGHT, linewidth=1.5,
                             connectionstyle="arc3,rad=0.20"))

axA.axvline(2025.70, color=FAINT, linewidth=1.0, linestyle=(0, (2, 3)), zorder=3)
axA.text(2025.62, 26, "两线交点落在 2025→2026 之间", fontsize=9.3, color=FAINT,
         ha="right", va="bottom", zorder=12)

axA.set_xlim(2023.55, 2027.55)
axA.set_xticks([2024, 2025, 2026, 2027])
axA.set_xticklabels(["2024", "2025", "2026E*", "2027E"], fontsize=11, color=MUTE)

lgA = axA.legend(loc="upper left", fontsize=9.8, frameon=True, framealpha=0.96,
                 edgecolor=GRID, borderpad=0.7)
lgA.get_frame().set_facecolor("white")

header(axA, "① 缺口 = 两条增速线之间的垂直距离，不是任何一根柱子的高度",
       "红区 = 需求跑在前面（紧张）；绿区 = 供给跑在前面（宽松）。"
       "2027E 只有供给线（虚线）——需求侧无一致预测，故缺口不可知。")

# ==================== Panel B：缺口柱（看符号，不看绝对值） ====================
axB = fig.add_subplot(gs[1])
style(axB, "缺口 = 需求增速 - 有效供给增速（pp）", (-98, 46), [-90, -60, -30, 0, 30])

pos_b = np.arange(len(YEARS_G))
gaps = [GAP[y] for y in YEARS_G]
cols = [C_LOOSE if g < 0 else C_TIGHT for g in gaps]
axB.bar(pos_b, gaps, width=0.50, color=cols, alpha=0.94, zorder=6, linewidth=0)
axB.axhline(0, color=MUTE, linewidth=1.4, zorder=7)

# 数值标签放在柱内靠零轴处（白字），彻底避开刻度与说明文字
for i, g in enumerate(gaps):
    axB.annotate(f"{g:+.1f}pp", xy=(pos_b[i], -4 if g < 0 else 4),
                 ha="center", va="top" if g < 0 else "bottom",
                 fontsize=11.8, fontweight="bold", color="white", zorder=11)

axB.annotate("若改以 HBM 为约束：\n"
             "84.1 - 88.9 = -4.8pp\n"
             "→ 必须先定义有效供给",
             xy=(2.86, 42), xytext=(2.86, 42), ha="right", va="top",
             fontsize=9.3, color=C_HBM, linespacing=1.55, zorder=12,
             bbox=dict(boxstyle="round,pad=0.42", facecolor="#f7f3fb",
                       edgecolor="#d9c9ea", linewidth=0.9))

lgB = axB.legend(handles=[
    Patch(facecolor=C_LOOSE, alpha=0.94, label="缺口为负：供给扩张快于需求（2024-2025 逆风期）"),
    Patch(facecolor=C_TIGHT, alpha=0.94, label="缺口为正：需求扩张快于供给（2026 首次出现）"),
], loc="lower right", fontsize=9.4, frameon=True, framealpha=0.96,
    edgecolor=GRID, borderpad=0.7)
lgB.get_frame().set_facecolor("white")

axB.set_xlim(-0.62, 2.95)
axB.set_xticks(pos_b)
axB.set_xticklabels(["2024", "2025", "2026E*"], fontsize=11, color=MUTE)

header(axB, "② 缺口在 2026 年首次转正 —— 这是观点 2 唯一被正向支持的时点",
       "柱高 = 需求增速 - 有效供给增速。2024-2025 缺口为负，说明当年「供给是加法」并不成立"
       "（供给在超线性扩张）。")

# ==================== Panel C：瓶颈归属 ====================
axC = fig.add_subplot(gs[2])
style(axC, "供给同比增速（%）", (18, 154), [30, 60, 90, 120, 150])

xs_c = np.array(sorted(COWOS), dtype=float)
ys_cow = np.array([COWOS[y] for y in sorted(COWOS)], dtype=float)
xs_h = np.array(sorted(HBM), dtype=float)
ys_hbm = np.array([HBM[y] for y in sorted(HBM)], dtype=float)

axC.plot(xs_c, ys_cow, color=C_COW, linewidth=2.6, marker="o", markersize=6.6,
         markerfacecolor="white", markeredgecolor=C_COW, markeredgewidth=2.0,
         zorder=8, label="CoWoS 先进封装产能")
axC.plot(xs_h, ys_hbm, color=C_HBM, linewidth=2.6, marker="o", markersize=6.6,
         markerfacecolor="white", markeredgecolor=C_HBM, markeredgewidth=2.0,
         zorder=8, label="HBM 出货量")

# 较紧约束（min）用浅色大圆点突出
for y in sorted(HBM):
    if COWOS[y] <= HBM[y]:
        axC.plot([y], [COWOS[y]], marker="o", markersize=13.0, color=C_COW,
                 alpha=0.28, zorder=6)
    else:
        axC.plot([y], [HBM[y]], marker="o", markersize=13.0, color=C_HBM,
                 alpha=0.28, zorder=6)

# 点位数值：CoWoS 一律左偏、HBM 一律右偏，同一年两个标签不会互撞
for y in sorted(COWOS):
    axC.annotate(f"{COWOS[y]:.0f}%", xy=(y, COWOS[y]), xytext=(-11, 12),
                 textcoords="offset points", ha="right", fontsize=9.6,
                 fontweight="bold", color=C_COW, zorder=11)
for y in sorted(HBM):
    axC.annotate(f"{HBM[y]:.0f}%", xy=(y, HBM[y]), xytext=(11, 12),
                 textcoords="offset points", ha="left", fontsize=9.6,
                 fontweight="bold", color=C_HBM, zorder=11)

# 2026 差值双箭头
axC.annotate("", xy=(2026, COWOS[2026]), xytext=(2026, HBM[2026]),
             arrowprops=dict(arrowstyle="<->", color=MUTE, linewidth=1.4), zorder=7)
axC.annotate("2026 差 23.4pp：瓶颈明确在 CoWoS",
             xy=(2028.38, 141), xytext=(2028.38, 141),
             ha="right", va="center", fontsize=10.2, fontweight="bold",
             color=MUTE, zorder=12)

axC.annotate("2027 起两者收敛到 4.3pp 以内\n（2027 差 1.7pp / 2028 差 4.3pp）\n"
             "→ 瓶颈不再是单点卡脖子",
             xy=(2027.45, 52), xytext=(2027.46, 88),
             fontsize=9.6, color=INK, ha="right", va="center", linespacing=1.6,
             bbox=dict(boxstyle="round,pad=0.45", facecolor="#f4f6f8",
                       edgecolor="#c8d0d8", linewidth=0.9),
             arrowprops=dict(arrowstyle="->", color="#8b959f", linewidth=1.2,
                             connectionstyle="arc3,rad=-0.20"), zorder=12)

axC.set_xlim(2023.58, 2028.42)
axC.set_xticks([2024, 2025, 2026, 2027, 2028])
axC.set_xticklabels(["2024", "2025", "2026E", "2027E", "2028E"], fontsize=11,
                    color=MUTE)

lgC = axC.legend(loc="lower left", fontsize=9.8, frameon=True, framealpha=0.96,
                 edgecolor=GRID, borderpad=0.7)
lgC.get_frame().set_facecolor("white")

header(axC, "③ 缺口的「边」由互补品中较紧的一方决定 —— 而它会在两者之间切换",
       "HBM 2025 及以前无同源基数（交银口径自 2025 起），故不绘制；"
       "浅色大圆点 = 当年较紧约束（即真正决定缺口宽度的那一个）。")

# ==================== footer ====================
fig.text(0.076, 0.100,
         "三条读图规则",
         fontsize=10.0, fontweight="bold", color=INK, ha="left", va="top")
fig.text(0.076, 0.078,
         "① 只能比增速，不能比水平 —— 需求单位是百万美元、供给单位是千片/月与 bn Gb，纵向距离没有量纲意义；\n"
         "② 缺口 = 需求增速 - 有效供给增速，有效供给取互补品中较紧者（CoWoS 与 HBM 是互补品，缺一个都出不了 GPU）；\n"
         "③ 读符号，不读绝对值 —— 缺口为负说明当年供给扩张更快，与「供给是加法」相反。",
         fontsize=9.0, color=MUTE, ha="left", va="top", linespacing=1.75)
fig.text(0.076, 0.028,
         "数据源：需求 = SEC XBRL 四大云厂 CAPEX（2026E* 为 H1 vs H1 实测，非年化）；"
         "供给 = Jefferies / JPMorgan / UBS / Bernstein / 交银国际（2026E 及以后为预测）。"
         "BofA 的「2027 供给 +68% vs 需求 +54%」为独立口径（晶圆片数），未并入本图序列。",
         fontsize=8.4, color=FAINT, ha="left", va="top", linespacing=1.6)

fig.savefig(OUT, facecolor="white")
print(f"written: {OUT}")

# 控制台复核
print("\n== 缺口复核 ==")
for y in sorted(GAP):
    print(f"  {y}: 需求 +{DEM[y]:.1f}%  -  有效供给 +{SUP[y]:.1f}%  =  {GAP[y]:+.1f}pp")
print(f"\n  2026 替代口径（以 HBM 为约束）: {DEM[2026] - HBM[2026]:+.1f}pp")
print(f"  2026 CoWoS vs HBM 差值: {HBM[2026] - COWOS[2026]:.1f}pp")
print(f"  2027 CoWoS vs HBM 差值: {COWOS[2027] - HBM[2027]:.1f}pp")
print(f"  2028 CoWoS vs HBM 差值: {HBM[2028] - COWOS[2028]:.1f}pp")
