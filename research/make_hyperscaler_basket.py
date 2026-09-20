#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperscaler 等权 CDS 篮子（由 SOLVE 月度单名点拼接）
=====================================================

对齐标的口径
------------
Herman Jin 2026-07-14：「Hyper Scaler 的 CDS 往上跑的幅度速度，整體的 CDS 的 widen
大概在 20 個 BIP 左右」——窗口是「過去一個月」（约 2026-06 中 → 07 中），
触发事件是 Amazon 融资。本脚本据此把可核成员在该窗口的走阔量与 20bp 做对照。

数据源
------
1) SOLVE Fixed Income 月度《Investment Grade CDS Market Summary》
   （2025-08 ~ 2026-08，公开免费；2025-09/10/11 三期站上 404）。
   每期只披露当月涨跌幅 Top-10，每行含 5Y 中价 SPRD 与上月值 SPRD-1 MONTH。
2) 成员自述点位：Herman Jin 2026-06-09 自述 Amazon 入场成本「30 幾個點」。

关键方法论
----------
「未上榜」= 该名当月 |Δ| 小于两个榜单的**较小门槛**，因此**不是缺失**，而是一条约束：
    -紧门槛_abs < Δ_m < +宽门槛_10th
据此可给未上榜月份一个有界区间；门槛越小，约束越紧（如 2026-03 仅 ±1bp）。

篮子成员定义
------------
MSFT / AMZN / GOOGL / META（云厂核心四家）。
ORCL 单列**不计入篮子**——其本人 2025-12-16 明确把 Oracle 归为 idiosyncratic
（「主要是對它 specific 的認為它可能要出問題，08 年的時候是整個市場」），
且其量级（媒体值 215bp）会把等权均值完全带偏。

输出：research/cds-hyperscaler-basket-2026.png
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

OUT = Path(__file__).with_name("cds-hyperscaler-basket-2026.png")

INK = "#1a1f24"
MUTE = "#5b6570"
FAINT = "#8b959f"
GRID = "#dde2e7"
GRIDX = "#eef1f4"

BASKET_C = "#b3261e"
BENCH_C = "#9aa4ae"

C_MSFT = "#5a6b7b"
C_AMZN = "#00857a"
C_META = "#7b3fb5"
C_GOOG = "#2f6fd0"
C_ORCL = "#a96a2a"


def m(year: int, month: int, day: int = 28) -> dt.datetime:
    return dt.datetime(year, month, day)


# ---------------------------------------------------------------------------
# 1. 成员可观测点（SOLVE 5Y 中价，bp；月末）
# ---------------------------------------------------------------------------
MEMBERS = {
    "MSFT": (C_MSFT, {m(2025, 11): 33, m(2025, 12): 36}),
    "AMZN": (C_AMZN, {m(2026, 7): 59, m(2026, 8): 66}),
    "META": (C_META, {m(2026, 3): 68, m(2026, 4): 75, m(2026, 6): 71, m(2026, 7): 94}),
    "GOOGL": (C_GOOG, {}),  # SOLVE 全库 0 点
}

# ORCL：SOLVE 仅 2025-07/08 两点，其后只有媒体点（不计入篮子）
ORCL_SOLVE = {m(2025, 7): 39, m(2025, 8): 43}
ORCL_MEDIA = {m(2025, 11, 14): 102.97, m(2025, 11, 19): 111, m(2025, 12, 5): 128,
              m(2025, 12, 10): 141, m(2025, 12, 12): 126, m(2026, 7, 31): 215}

# 2. 未上榜约束（Δ 的可行区间半宽 = min(紧门槛_abs, 宽门槛_10th)）
GATE = {  # 月份 -> (紧门槛_abs, 宽门槛_10th, 半宽)
    m(2025, 8): (6.0, 3.0, 3.0),
    m(2025, 12): (9.0, 3.7, 3.7),
    m(2026, 1): (8.0, 5.3, 5.3),
    m(2026, 2): (3.0, 9.1, 3.0),
    m(2026, 3): (1.0, 16.5, 1.0),
    m(2026, 4): (14.0, 5.5, 5.5),
    m(2026, 5): (13.0, 1.7, 1.7),
    m(2026, 6): (11.0, 11.3, 11.0),
    m(2026, 7): (4.0, 15.8, 4.0),
    m(2026, 8): (10.0, 7.4, 7.4),
}

# 3. 篮子：当月可观测成员等权均值（n = 可观测成员数）
BASKET = {
    m(2025, 11): (33.0, 1),
    m(2025, 12): (36.0, 1),
    m(2026, 3): (68.0, 1),
    m(2026, 4): (75.0, 1),
    m(2026, 6): (71.0, 1),      # 仅 META 可观测；AMZN 由缺位约束推得 55~63
    m(2026, 7): (76.5, 2),      # META 94 + AMZN 59
    m(2026, 8): (66.0, 1),      # 仅 AMZN；META 缺位约束 86.6~101.4
}

# 由缺位约束导出的篮子区间（仅列出上下界成立的月份）
BASKET_BAND = {
    m(2026, 5): (73.3, 76.7),   # 仅 META ∈ 75 ± 1.7
    m(2026, 8): (76.3, 83.7),   # AMZN 66 + META ∈ 94 ± 7.4
}

# 4. 基准
GLOBAL_IG = {
    m(2025, 8): 47, m(2025, 12): 45, m(2026, 1): 45, m(2026, 2): 47,
    m(2026, 3): 56, m(2026, 4): 52, m(2026, 5): 50, m(2026, 6): 50,
    m(2026, 7): 50, m(2026, 8): 49,
}

# 5. 2026-06 → 2026-07 单月走阔归因（月末口径）
MOM = [
    ("AMD", 41, "hw"),
    ("AVGO（博通）", 32, "hw"),
    ("NVDA（英伟达）", 31, "hw"),
    ("META", 23, "hyp"),
    ("DELL（戴尔）", 17, "hw"),
    ("INTC（英特尔）", 16, "hw"),
    ("AMZN（自述入场基 ~35bp → 59bp）", 24, "hyp"),
    ("AMZN（月末口径，缺位约束 ±4bp）", 0, "hyp"),
    ("Global IG 大盘", 0, "idx"),
]

# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(15.0, 13.6), dpi=165)
gs = fig.add_gridspec(3, 1, height_ratios=[2.45, 1.30, 0.78], hspace=0.52,
                      left=0.075, right=0.845, top=0.878, bottom=0.075)

X0, X1 = m(2025, 6, 1), m(2026, 10, 5)


def style(ax, ylabel, ylim, yticks, log=True):
    if log:
        ax.set_yscale("log")
    ax.set_ylim(*ylim)
    ax.set_yticks(yticks)
    ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    ax.set_ylabel(ylabel, fontsize=10.8, labelpad=7)
    ax.grid(True, which="major", axis="y", color=GRID, linewidth=0.8)
    ax.grid(True, which="major", axis="x", color=GRIDX, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#b9c2cb")
    ax.set_xlim(X0, X1)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m"))
    plt.setp(ax.get_xticklabels(), fontsize=9.0, color=MUTE)


# ==================== Panel A：篮子与成员 ====================
axA = fig.add_subplot(gs[0])
style(axA, "5Y CDS 中价（bp，对数轴）", (26, 300), [30, 40, 50, 70, 100, 150, 215])

# 基准
gx = sorted(GLOBAL_IG)
axA.plot(gx, [GLOBAL_IG[x] for x in gx], color=BENCH_C, linewidth=2.4,
         linestyle=(0, (5, 3)), marker="s", markersize=5.0,
         markerfacecolor="white", markeredgecolor=BENCH_C, markeredgewidth=1.6,
         zorder=4, label="SOLVE Global IG 大盘（基准）")

# 成员细线
for name, (color, series) in MEMBERS.items():
    if not series:
        continue
    xs = sorted(series)
    axA.plot(xs, [series[x] for x in xs], color=color, linewidth=1.9, alpha=0.85,
             marker="o", markersize=5.4, markerfacecolor="white",
             markeredgecolor=color, markeredgewidth=1.8, zorder=5)
    axA.annotate(name, xy=(xs[-1], series[xs[-1]]), xytext=(9, 0),
                 textcoords="offset points", fontsize=10.0, color=color,
                 fontweight="bold", va="center", zorder=12)

# ORCL：SOLVE 实心点 + 媒体空心菱形（不计入篮子）
ox = sorted(ORCL_SOLVE)
axA.plot(ox, [ORCL_SOLVE[x] for x in ox], color=C_ORCL, linewidth=1.6,
         linestyle=(0, (1.5, 2.5)), marker="o", markersize=4.8,
         markerfacecolor="white", markeredgecolor=C_ORCL, markeredgewidth=1.6,
         zorder=5, alpha=0.9)
om = sorted(ORCL_MEDIA)
axA.plot(om, [ORCL_MEDIA[x] for x in om], color=C_ORCL, linewidth=1.3,
         linestyle=(0, (1.5, 2.5)), marker="D", markersize=5.0,
         markerfacecolor="white", markeredgecolor=C_ORCL, markeredgewidth=1.4,
         alpha=0.75, zorder=4)
axA.annotate("ORCL\n（媒体点）", xy=(om[-1], ORCL_MEDIA[om[-1]]), xytext=(9, 0),
             textcoords="offset points", fontsize=9.6, color=C_ORCL,
             fontweight="bold", va="center", zorder=12)
axA.text(m(2025, 6, 5), 138,
         "ORCL：SOLVE 全库仅 2025-07/08 两点（39 → 43bp），\n"
         "其后全为媒体点；本人视其为 idiosyncratic，\n"
         "故不计入篮子（否则 215bp 会带偏等权均值）",
         fontsize=8.8, color=C_ORCL, ha="left", va="top", linespacing=1.5,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#fbf6ef",
                   edgecolor="#e2d0b8", linewidth=0.9), zorder=13)

# 篮子区间带
for dt_, (lo, hi) in BASKET_BAND.items():
    axA.plot([dt_, dt_], [lo, hi], color=BASKET_C, linewidth=5.0, alpha=0.22,
             solid_capstyle="butt", zorder=6)

# 篮子主线
bx = sorted(BASKET)
by = [BASKET[x][0] for x in bx]
axA.plot(bx, by, color=BASKET_C, linewidth=3.4, zorder=9,
         linestyle=(0, (6, 3)), alpha=0.95)

# 篮子窗口带（他说的「過去一個月」）
axA.axvspan(m(2026, 6, 9), m(2026, 7, 14), color="#b3261e", alpha=0.06, zorder=1)
axA.annotate("他說「過去一個月」的窗口\n2026-06-09 → 07-14",
             xy=(m(2026, 6, 25), 150), xytext=(m(2026, 6, 14), 275),
             fontsize=9.0, color=BASKET_C, ha="left", va="top", linespacing=1.5,
             fontweight="bold", zorder=13,
             arrowprops=dict(arrowstyle="->", color=BASKET_C, linewidth=1.1,
                             connectionstyle="arc3,rad=0.2"))

for x, (v, n) in BASKET.items():
    filled = n >= 2
    axA.plot([x], [v], marker="o", markersize=9.6 if filled else 8.2,
             markerfacecolor=BASKET_C if filled else "white",
             markeredgecolor=BASKET_C, markeredgewidth=2.2, zorder=11)
    axA.annotate(f"n={n}", xy=(x, v), xytext=(0, -15 if n < 2 else 13),
                 textcoords="offset points", fontsize=8.6, color=BASKET_C,
                 fontweight="bold", ha="center", zorder=12,
                 bbox=dict(boxstyle="round,pad=0.16", facecolor="white",
                           edgecolor="none", alpha=0.85))

axA.set_title("① Hyperscaler 等权篮子（MSFT+AMZN+GOOGL+META）——由 SOLVE 单名点拼接",
              fontsize=12.2, fontweight="bold", color=INK, pad=12, loc="left")
axA.text(m(2025, 6, 5), 28.4,
         "GOOGL：SOLVE 全库 0 个点位（全 9 期榜单均未出现）",
         fontsize=8.8, color=C_GOOG, ha="left", va="bottom", fontweight="bold", zorder=13)

axA.legend(handles=[
    Line2D([], [], color=BENCH_C, lw=2.4, ls=(0, (5, 3)), marker="s", ms=5,
           mfc="white", mec=BENCH_C, label="SOLVE Global IG 大盘（基准）"),
    Line2D([], [], color=BASKET_C, lw=0, marker="o", ms=9, mfc=BASKET_C,
           mec=BASKET_C, label="篮子点（n≥2，真等权 / 唯一月：2026-07）"),
    Line2D([], [], color=BASKET_C, lw=0, marker="o", ms=8, mfc="white",
           mec=BASKET_C, mew=2.0, label="篮子点（n=1，等同单名，不可直接拼接）"),
    Line2D([], [], color=BASKET_C, lw=0, marker="|", ms=14, mew=6, alpha=0.35,
           label="缺位约束区间（由榜单门槛反推，非观测点）"),
    Line2D([], [], color=BASKET_C, lw=2.6, ls=(0, (6, 3)), label="篮子连线（跨缺口，非连续行情）"),
], loc="upper left", fontsize=8.8, frameon=True, framealpha=0.96,
    edgecolor="#d8dde3", borderpad=0.65, labelspacing=0.55,
    handletextpad=0.75, borderaxespad=0.9).get_frame().set_facecolor("white")

# ==================== Panel B：2026-06 → 07 单月走阔归因 ====================
axB = fig.add_subplot(gs[1])
axB.set_xlim(-3, 47)
axB.set_ylim(-0.7, len(MOM) + 1.1)
axB.axvline(0, color="#8b959f", linewidth=1.5, zorder=3)
axB.set_yticks(range(len(MOM)))
axB.set_yticklabels([r[0] for r in MOM], fontsize=9.8, color=INK)
axB.invert_yaxis()
axB.set_xlabel("2026-06 月末 → 2026-07 月末的 5Y CDS 变动（bp）", fontsize=10.2,
               color=MUTE, labelpad=6)
axB.grid(True, axis="x", color=GRIDX, linewidth=0.8)
axB.set_axisbelow(True)
for s in ("top", "right", "left"):
    axB.spines[s].set_visible(False)
axB.spines["bottom"].set_color("#b9c2cb")
axB.tick_params(axis="y", length=0)

BAR_C = {"hw": "#e08a1e", "hyp": BASKET_C, "idx": BENCH_C}
for i, (name, val, kind) in enumerate(MOM):
    axB.barh(i, val, height=0.58, color=BAR_C[kind], alpha=0.92, zorder=4)
    axB.text(val + 1.0, i, f"+{val}" if val else "0（持平）", fontsize=9.8,
             color=INK, fontweight="bold", va="center", zorder=5)

axB.text(46, 9.45,
         "红色 = Hyperscaler（篮子成员）　橙色 = AI 硬件 / 服务器（非篮子）　灰色 = 大盘基准\n"
         "本人所称「Hyper Scaler 整體 widen 大概 20 個 BIP」= 红色两条（META +23、AMZN +24）的量级 → 量级吻合",
         fontsize=9.2, color=BASKET_C, fontweight="bold", ha="right",
         va="center", linespacing=1.6,
         bbox=dict(boxstyle="round,pad=0.45", facecolor="#fdf3f2",
                   edgecolor="#e8bcb8", linewidth=0.9), zorder=6)

axB.set_title("② 同窗口归因：hyperscaler 的走阔由成员自身驱动，同期大盘零变动",
              fontsize=12.2, fontweight="bold", color=INK, pad=10, loc="left")

# ==================== Panel C：缺位约束半宽 ====================
axC = fig.add_subplot(gs[2])
gx2 = sorted(GATE)
labels = [x.strftime("%y-%m") for x in gx2]
vals = [GATE[x][2] for x in gx2]
cols = ["#b3261e" if v < 2.5 else "#c9b18a" for v in vals]
bars = axC.bar(range(len(gx2)), vals, width=0.58, color=cols, alpha=0.9, zorder=4)
for i, v in enumerate(vals):
    axC.text(i, v + 0.28, f"{v:g}", ha="center", fontsize=9.0, color=INK,
             fontweight="bold", zorder=5)
axC.set_xticks(range(len(gx2)))
axC.set_xticklabels(labels, fontsize=9.2, color=MUTE)
axC.set_ylabel("未上榜 → |Δ| 上限（bp）", fontsize=10.0, labelpad=6)
axC.set_ylim(0, 12.6)
axC.grid(True, axis="y", color=GRIDX, linewidth=0.8)
axC.set_axisbelow(True)
for s in ("top", "right"):
    axC.spines[s].set_visible(False)
for s in ("left", "bottom"):
    axC.spines[s].set_color("#b9c2cb")
axC.set_title("③ 为什么篮子拼不齐：SOLVE 只发 Top-10，未上榜只给出一条区间约束",
              fontsize=11.4, fontweight="bold", color=INK, pad=9, loc="left")
axC.text(-0.42, 12.2,
         "红色柱 = 门槛极低（2026-03 仅 ±1bp）→ 缺位 ≈ 已知点位\n"
         "米色柱 = 门槛高，缺位几乎不提供信息",
         fontsize=8.9, color=MUTE, ha="left", va="top", linespacing=1.5)

fig.suptitle("Hyperscaler CDS 等权篮子：SOLVE 单名点能拼到什么程度  "
             "（2025-08 ~ 2026-08，5Y 中价 bp）",
             fontsize=15.0, fontweight="bold", color=INK, x=0.075, ha="left", y=0.955)

fig.text(0.075, 0.026,
         "数据：SOLVE Fixed Income 月度《Investment Grade CDS Market Summary》公开榜单（免费）" 
         "；AMZN 自述入场基与 ORCL 媒体点见 Herman Jin 语料（2026-06-09 / 2025-12-16）。\n"
         "口径提醒：「n=1」的篮子点等于单一发行人利差，与「n≥2」的等权均值不同质；"
         "2025-09/10/11 三期原站缺失。本图仅作数据可得性研究，不构成投资建议。",
         fontsize=8.4, color=FAINT, ha="left", va="bottom", linespacing=1.6)

fig.savefig(OUT, facecolor="white", bbox_inches="tight")
print("saved:", OUT)
