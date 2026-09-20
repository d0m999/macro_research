from pathlib import Path
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot

setup_plot()

out = Path(__file__).with_name("hyperscaler-cloud-growth-2023-2026.png")

quarters = [
    "2023Q1", "2023Q2", "2023Q3", "2023Q4",
    "2024Q1", "2024Q2", "2024Q3", "2024Q4",
    "2025Q1", "2025Q2", "2025Q3", "2025Q4",
    "2026Q1", "2026Q2",
]

# 公司披露的同比增速（YoY），来源：SEC 8-K/6-K 附件、公司官方 IR 财报稿与电话会记录
series = {
    "AWS": [16, 12, 12, 13, 17, 19, 19, 19, 17, 17, 20, 24, 28, 37],
    "Azure（GAAP）": [27, 26, 29, 30, 31, 29, 33, 31, 33, 39, 40, 39, 40, 43],
    "Google Cloud": [28, 28, 22, 26, 28, 29, 35, 30, 28, 32, 34, 48, 63, 82],
    "Alibaba Cloud": [-2, 4, 2, 3, 3, 6, 7, 13, 18, 26, 34, 36, 38, 45],
}
colors = {
    "AWS": "#FF9900",
    "Azure（GAAP）": "#0078D4",
    "Google Cloud": "#34A853",
    "Alibaba Cloud": "#6B4EFF",
}
# 数值标注默认放在线的上方还是下方
label_side = {
    "AWS": "below",
    "Azure（GAAP）": "above",
    "Google Cloud": "above",
    "Alibaba Cloud": "below",
}

fig, ax = plt.subplots(figsize=(14, 7.2))

for name, values in series.items():
    ax.plot(quarters, values, marker="o", linewidth=2.4, markersize=5.5,
            label=name, color=colors[name])

# 防重叠标注：同一季度内，上方标注按数值升序铺开，下方标注按数值降序铺开
MIN_GAP = 4.0   # 同一侧相邻标注的最小纵向间距（纵轴单位）
OFFSET = 3.2    # 标注相对数据点的起始偏移
for i in range(len(quarters)):
    above = sorted(
        ((series[n][i], n) for n in series if label_side[n] == "above"),
        key=lambda t: t[0],
    )
    below = sorted(
        ((series[n][i], n) for n in series if label_side[n] == "below"),
        key=lambda t: t[0], reverse=True,
    )
    prev = None
    for value, name in above:
        y = value + OFFSET
        if prev is not None:
            y = max(y, prev + MIN_GAP)
        prev = y
        ax.annotate(f"{value}%", (i, y), ha="center", va="bottom",
                    fontsize=8.5, color=colors[name])
    prev = None
    for value, name in below:
        y = value - OFFSET
        if prev is not None:
            y = min(y, prev - MIN_GAP)
        prev = y
        ax.annotate(f"{value}%", (i, y), ha="center", va="top",
                    fontsize=8.5, color=colors[name])

ax.set_title("Hyperscaler 云收入同比增速（2023Q1–2026Q2）", fontsize=16, pad=16)
ax.set_ylabel("公司披露同比增速（YoY）")
ax.axhline(0, color="#999999", linewidth=0.8)
ax.set_ylim(-14, 96)
ax.grid(axis="y", alpha=0.25)
ax.legend(loc="upper left", ncols=4, frameon=False)
ax.spines[["top", "right"]].set_visible(False)
ax.tick_params(axis="x", rotation=45)
fig.text(
    0.01,
    0.005,
    "注：均为公司披露 YoY；Azure 为“Azure and other cloud services”增速；Alibaba 2023Q1 为旧 Cloud 分部口径，"
    "2023Q2 起为 Cloud Intelligence Group，2026Q2 起为 AI Cloud and Compute Services。",
    fontsize=9,
    color="#555555",
)
fig.tight_layout(rect=(0, 0.035, 1, 1))
fig.savefig(out, dpi=180, bbox_inches="tight")
print(out)
