#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 相关发行人 5Y 单名 CDS 利差走势图
—— SOLVE 月度中价（IG / HY）+ 媒体转述点位

数据源
------
1) SOLVE Fixed Income 月度《Investment Grade CDS Market Summary》与
   《High Yield CDS Market Summary》（2025-08 ~ 2026-08）。
   口径：5Y 单名 CDS 中价（mid spread, bp），月末快照。
   URL 形如 https://solvefixedincome.com/resources/investment-grade-cds-market-summary-<month>-<year>/
   每期榜单同时给出「上月值」(SPRD-1 MONTH)，可链式回补前一月点位。
2) Oracle / CoreWeave 点位为媒体与券商转述，标注为「媒体转述」。

关键口径提醒
------------
- SOLVE 公开月报只披露当月涨跌幅前十名，故各家序列为「可观测点拼接」，
  缺月 = 该名未进前十（不是数据为 0）。
- 媒体所载「Broadcom 2025-08 = 122/130bp」经 SOLVE 2025-08 榜单反证不成立：
  当月榜单第十名的涨跌幅门槛仅 +3bp，Global IG 中价仅 47bp。

输出：research/cds-spreads-ai-issuers-2025-2026.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import datetime as dt

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB", "STHeiti", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).with_name("cds-spreads-ai-issuers-2025-2026.png")

RED, GREEN = "#c0392b", "#1f9e57"
GREY = "#2f3640"


def d(year: int, month: int, day: int = 28) -> dt.datetime:
    return dt.datetime(year, month, day)


# ---------------------------------------------------------------------------
# SOLVE 月度序列（5Y CDS 中价 bp）  name -> (color, {date: bp}, label_offset_pt)
# ---------------------------------------------------------------------------
AI_HW = {
    "AVGO（博通）": ("#e08a1e",
                     {d(2025, 11): 37, d(2025, 12): 41, d(2026, 5): 44,
                      d(2026, 6): 65, d(2026, 7): 97}, (11, 12)),
    "AMD": ("#c0392b",
            {d(2026, 5): 36, d(2026, 6): 46, d(2026, 7): 87, d(2026, 8): 94}, (11, -14)),
    "NVDA（英伟达）": ("#1f9e57",
                       {d(2026, 5): 39, d(2026, 6): 47, d(2026, 7): 77, d(2026, 8): 82}, (11, 9)),
    "DELL（戴尔）": ("#2d7ff9",
                     {d(2026, 4): 59, d(2026, 5): 49, d(2026, 6): 58, d(2026, 7): 75}, (11, -30)),
}

CLOUD = {  # 参考组，不直接标注，走图例
    "META": ("#9b51e0", {d(2026, 3): 68, d(2026, 4): 75, d(2026, 6): 71, d(2026, 7): 94, d(2026, 8): 94}),
    "AMZN（亚马逊）": ("#00a0a0", {d(2026, 7): 59, d(2026, 8): 66}),
    "MSFT（微软）": ("#6c7a89", {d(2025, 11): 33, d(2025, 12): 36}),
    "INTC（英特尔）": ("#c96a9b", {d(2025, 7): 75, d(2025, 8): 58, d(2026, 3): 82,
                                   d(2026, 4): 62, d(2026, 6): 65, d(2026, 7): 81}),
}

GLOBAL_IG = {
    d(2025, 8): 47, d(2025, 11): 48, d(2025, 12): 45, d(2026, 1): 45, d(2026, 2): 47,
    d(2026, 3): 56, d(2026, 4): 52, d(2026, 5): 50, d(2026, 6): 50, d(2026, 7): 50,
    d(2026, 8): 49,
}

# 尾部 / 非 IG 宇宙
TAIL = {
    "CoreWeave（媒体转述）": ("#b0553c", {d(2025, 10, 13): 555, d(2025, 11, 28): 675,
                                          d(2025, 12, 10): 715}, (11, 10)),
    "SoftBank（HY 级 · SOLVE）": ("#6b6b6b", {d(2026, 6): 294, d(2026, 7): 366}, (11, 8)),
}

# Oracle：SOLVE 仅 1 个可观测点（2025-08），其后为媒体点位
ORCL_SOLVE = {d(2025, 7, 15): 39, d(2025, 8, 28): 43}
ORCL_MEDIA = {d(2025, 11, 14): 102.97, d(2025, 11, 19): 111, d(2025, 12, 5): 128,
              d(2025, 12, 10): 141, d(2025, 12, 12): 126, d(2026, 7, 31): 215}
ORCL_COLOR = "#7d5a3c"

# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(14.8, 13.2), dpi=165)
gs = fig.add_gridspec(3, 1, height_ratios=[2.45, 1.30, 0.85], hspace=0.44,
                      left=0.062, right=0.862, top=0.874, bottom=0.128)

X0, X1 = d(2025, 6, 1), d(2026, 9, 25)
SPIKE0, SPIKE1 = d(2026, 7, 1), d(2026, 8, 1)


def style(ax, ylabel, ylim, yticks):
    ax.set_yscale("log")
    ax.set_ylim(*ylim)
    ax.set_yticks(yticks)
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_ylabel(ylabel, fontsize=10.8, labelpad=7)
    ax.grid(True, which="major", axis="y", color="#d8dde3", linewidth=0.8)
    ax.grid(True, which="major", axis="x", color="#eef1f4", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9c2cb")
    ax.set_xlim(X0, X1)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m"))
    plt.setp(ax.get_xticklabels(), fontsize=9.0, color="#5b6570")


def label(ax, name, color, series, off, weight="bold", size=10.3, style_="normal"):
    xs = sorted(series)
    ax.annotate(name, xy=(xs[-1], series[xs[-1]]), xytext=off,
                textcoords="offset points", fontsize=size, color=color,
                fontweight=weight, style=style_, va="center", zorder=14)


LEAD_X = d(2026, 9, 18)  # 引线终点（无数据月）
TXT_X = d(2026, 9, 26)   # 文字起点，落在轴外留白


def leader_label(ax, name, color, series, y_text, size=10.2):
    """把末点引到右侧固定高度再写标签，避免年末密集区互相压线"""
    xs = sorted(series)
    x0, y0 = xs[-1], series[xs[-1]]
    ax.plot([x0, LEAD_X], [y0, y_text], color="#9aa4ae", linewidth=0.9,
            linestyle=(0, (2, 2)), zorder=6, clip_on=False)
    ax.text(TXT_X, y_text, name, fontsize=size, color=color, fontweight="bold",
            va="center", ha="left", zorder=14, clip_on=False)


# ========================== Panel A：IG 宇宙 ==========================
axA = fig.add_subplot(gs[0])
style(axA, "5Y 单名 CDS 中价（bp，对数轴）\n　", (26, 250),
      [30, 40, 50, 60, 80, 100, 150, 200])
axA.axvspan(SPIKE0, SPIKE1, color=RED, alpha=0.055, zorder=0)

gd = sorted(GLOBAL_IG)
axA.plot(gd, [GLOBAL_IG[x] for x in gd], color=GREY, linewidth=2.5,
         linestyle=(0, (5, 3)), marker="s", markersize=4.6,
         markerfacecolor=GREY, markeredgecolor="white", markeredgewidth=0.8, zorder=4)
label(axA, "SOLVE Global IG 大盘基准", GREY, GLOBAL_IG, (11, 0), size=10.2)

for name, (color, series) in CLOUD.items():
    xs = sorted(series)
    axA.plot(xs, [series[x] for x in xs], color=color, linewidth=1.6, alpha=0.92,
             marker="o", markersize=4.4, markerfacecolor="white",
             markeredgecolor=color, markeredgewidth=1.4, zorder=5)

for name, (color, series, off) in AI_HW.items():
    xs = sorted(series)
    axA.plot(xs, [series[x] for x in xs], color=color, linewidth=3.5, zorder=8,
             marker="o", markersize=6.8, markerfacecolor="white",
             markeredgecolor=color, markeredgewidth=2.5)

for name, y_text in (("AVGO（博通）", 116), ("AMD", 100),
                     ("NVDA（英伟达）", 87), ("DELL（戴尔）", 76)):
    color, series, _ = AI_HW[name]
    leader_label(axA, name, color, series, y_text)

axA.text(d(2026, 7, 15), 163, "2026-07\n集体走阔", fontsize=9.4, color="#a03020",
         fontweight="bold", ha="center", va="center", zorder=12)

leg = axA.legend(handles=[Line2D([], [], color=c, linewidth=1.6, marker="o",
                                 markersize=4.2, markerfacecolor="white",
                                 markeredgecolor=c, markeredgewidth=1.3, label=n)
                          for n, (c, _) in CLOUD.items()],
                 loc="upper left", ncol=2, fontsize=9.3, frameon=True,
                 framealpha=0.94, edgecolor="#ccd3da", borderpad=0.6,
                 handlelength=1.7, columnspacing=1.3, labelspacing=0.45,
                 title="参考：一线云厂与英特尔（细线）")
leg.get_title().set_fontsize(9.3)
leg.get_title().set_color("#5b6570")

# ==================== Panel B：尾部 / 非 IG 宇宙 + Oracle ====================
axB = fig.add_subplot(gs[1])
style(axB, "bp（对数轴）", (34, 950), [40, 60, 100, 150, 200, 300, 500, 800])
for name, (color, series, off) in TAIL.items():
    xs = sorted(series)
    dashed = "媒体" in name
    axB.plot(xs, [series[x] for x in xs], color=color, linewidth=2.0 if not dashed else 1.7,
             linestyle=(0, (2, 3)) if dashed else "solid", marker="D" if dashed else "o",
             markersize=5.4, markerfacecolor="white", markeredgecolor=color,
             markeredgewidth=1.6, alpha=0.95, zorder=6)
    label(axB, name, color, series, off, weight="bold", size=9.8,
          style_="italic" if dashed else "normal")

# Oracle：SOLVE 段（实线实心点）+ 媒体段（虚线空心菱形）+ 缺档连接
xs = sorted(ORCL_SOLVE)
axB.plot(xs, [ORCL_SOLVE[x] for x in xs], color=ORCL_COLOR, linewidth=2.6, zorder=8,
         marker="o", markersize=6.4, markerfacecolor="white",
         markeredgecolor=ORCL_COLOR, markeredgewidth=2.2)
xm = sorted(ORCL_MEDIA)
axB.plot(xm, [ORCL_MEDIA[x] for x in xm], color=ORCL_COLOR, linewidth=1.8, zorder=7,
         linestyle=(0, (2, 3)), marker="D", markersize=5.4,
         markerfacecolor="white", markeredgecolor=ORCL_COLOR, markeredgewidth=1.5)
axB.plot([xs[-1], xm[0]], [ORCL_SOLVE[xs[-1]], ORCL_MEDIA[xm[0]]], color="#9aa4ae",
         linewidth=1.1, linestyle=(0, (1, 2)), zorder=5)
axB.annotate("2025-09/10/11 SOLVE 缺档",
             xy=(d(2025, 10, 2), 87), xytext=(d(2025, 8, 20), 122),
             fontsize=9.0, color="#7d5a3c", fontweight="bold", ha="left", va="center",
             arrowprops=dict(arrowstyle="->", color="#7d5a3c", linewidth=1.2,
                             connectionstyle="arc3,rad=-0.25"),
             zorder=13)
label(axB, "Oracle（SOLVE 点 · 媒体点）", ORCL_COLOR, ORCL_MEDIA, (11, 0),
      weight="bold", size=9.8)
axB.text(d(2025, 6, 5), 880,
         "Oracle：SOLVE 全库 14 期\nIG / HY 报告中，ORCL\n仅出现 1 次\n（2025-08 = 43bp）\n"
         "2025-09/10/11 三期缺档，\n2025-12 与 2026 各月均未进前十\n"
         "-> 月环比 < 当月榜单门槛\n   （+2.4 ~ +38bp）\n"
         "   故 43 -> 103bp 的跳升\n   无法从月报回补",
         fontsize=8.7, color="#5b6570", ha="left", va="top", linespacing=1.45,
         bbox=dict(boxstyle="round,pad=0.42", facecolor="#f4f6f8",
                   edgecolor="#c8d0d8", linewidth=0.9), zorder=13)
axB.set_title("尾部与 Oracle：CoreWeave / SoftBank 与 IG 宇宙量级不同，单列一轴",
              fontsize=11.0, fontweight="bold", color="#1a1f24", pad=8, loc="left")
axB.text(0.995, 0.97, "斜体虚线点 = 媒体转述点位，点与点之间以虚线直连，仅示区间，不代表连续行情",
         transform=axB.transAxes, fontsize=8.9, color="#7b858f", ha="right", va="top")
axB.set_title("尾部与 Oracle：CoreWeave / SoftBank 与 IG 宇宙不同量级，单列一轴；Oracle 因缺档 + 未上榜而点位稀疏",
              fontsize=11.0, fontweight="bold", color="#1a1f24", pad=8, loc="left")

# ==================== Panel C：脱钩检验 ====================
axC = fig.add_subplot(gs[2])
months = [d(2026, 5, 15), d(2026, 6, 15), d(2026, 7, 15), d(2026, 8, 15)]
vals = [((AI_HW["AMD"][1][x] + AI_HW["NVDA（英伟达）"][1][x]) / 2) - GLOBAL_IG[x]
        for x in [d(2026, 5), d(2026, 6), d(2026, 7), d(2026, 8)]]
colors = [RED if v > 0 else GREEN for v in vals]
bars = axC.bar(months, vals, width=17, color=colors, alpha=0.88,
               edgecolor="white", linewidth=1.0, zorder=3)
for b, v in zip(bars, vals):
    axC.text(b.get_x() + b.get_width() / 2, v + (3.4 if v > 0 else -7.6), f"{v:+.1f}",
             ha="center", fontsize=10.4, fontweight="bold",
             color=RED if v > 0 else GREEN)
axC.axhline(0, color="#5b6570", linewidth=1.2, zorder=4)
axC.axvspan(SPIKE0, SPIKE1, color=RED, alpha=0.055, zorder=0)
axC.set_ylim(-24, 54)
axC.set_xlim(d(2026, 4, 18), d(2026, 9, 4))
axC.set_ylabel("bp", fontsize=10.5)
axC.grid(True, axis="y", color="#d8dde3", linewidth=0.8)
axC.set_axisbelow(True)
for s in ("top", "right"):
    axC.spines[s].set_visible(False)
for s in ("left", "bottom"):
    axC.spines[s].set_color("#b9c2cb")
axC.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
axC.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m"))
plt.setp(axC.get_xticklabels(), fontsize=9.0, color="#5b6570")
axC.set_title("脱钩检验：（AMD + NVDA）均值 - SOLVE Global IG 中价　->　"
              "由低于大盘 12.5bp 转为高出大盘 39bp",
              fontsize=11.2, fontweight="bold", color="#1a1f24", pad=9, loc="left")
axC.text(0.995, 0.06, "红 = 相对大盘走阔（信用恶化）　绿 = 相对大盘收窄",
         transform=axC.transAxes, fontsize=9.0, color="#7b858f", ha="right")

# ============================== 标题区 ==============================
fig.text(0.062, 0.962, "AI 相关发行人 5Y 单名 CDS 利差：SOLVE 月度序列（2025-08 - 2026-08）",
         fontsize=17, fontweight="bold", color="#151a1f", va="top")
fig.text(0.062, 0.936,
         "加粗实线 = 本轮由 SOLVE 公开月报新纳入的 AI 硬件 / 服务器四家（NVDA · AMD · AVGO · DELL）"
         "　·　粗虚线 = SOLVE Global IG 大盘基准　·　细线 = 一线云厂与英特尔　·　虚线点 = 媒体转述",
         fontsize=9.9, color="#5b6570", va="top")
fig.text(0.062, 0.917,
         "2026-07 单月：AMD +41bp、AVGO +32bp、NVDA +31bp、DELL +17bp，"
         "而同期 Global IG 持平于 50bp —— AI 信用与大盘信用首次明确脱钩",
         fontsize=9.9, color="#a03020", fontweight="bold", va="top")

# ============================== 页脚 ==============================
fig.text(
    0.062, 0.020,
    "数据源：SOLVE Fixed Income 月度《Investment Grade / High Yield CDS Market Summary》2025-08 - 2026-08，"
    "5Y 单名 CDS 中价（bp，月末快照）；Oracle 与 CoreWeave 为媒体 / 券商转述。\n"
    "口径提醒：SOLVE 公开月报仅披露当月涨跌幅前十名，故各家序列为「可观测点拼接」而非连续序列；"
    "缺月 = 该名未进前十，不是取值为 0。月报另给出「上月值」列，用于链式回补前一月点位。\n"
    "反证记录：媒体所载「Broadcom 2025-08 5Y CDS = 122 / 130bp」不成立 —— SOLVE 2025-08 榜单第十名的涨跌幅门槛仅 +3bp，"
    "当月 Global IG 中价仅 47bp，AVGO 若达 122bp 必居榜首。\n"
    "Oracle 说明：SOLVE 全库可得的 14 期 IG / HY 报告中，ORCL 仅出现 1 次（2025-08 = 43bp）；"
    "2025-09 / 10 / 11 三期缺档，2025-12 及 2026 各月均未进前十，"
    "说明其月环比变化小于当月榜单门槛（门槛区间 +2.4 ~ +38bp）。",
    fontsize=8.4, color="#7b858f", va="bottom", linespacing=1.5,
)

fig.savefig(OUT, facecolor="white")
print("saved:", OUT)
