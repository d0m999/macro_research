# research/_agent/ — Agent 读取索引

> **目录约定**：`research/` 根目录**只放人类读的汇总研报** `../Herman-Jin 观点 rollup.md`；本目录收纳 agent 过程文档、数据、脚本、图件与独立题材附件。日期型语料增量包按 `corpus-updates/YYYY-MM-DD/` 归档，其余保留现有路径以维护已建立的文档和复现引用。
> **入口**：结论只认 `../Herman-Jin 观点 rollup.md`；agent 从本 README 进入过程材料。勿把过程稿当主结论。
> 更新：2026-09-26（新增观点蒸馏、INTC / CPU 与 post-training 独立研究）；此前：2026-09-23 根目录拆分、删过期/快照、改口径、CDS 归档。

## 0. 30 秒导航

| 你要… | 只读这些 |
|---|---|
| Herman Jin 的观点与证据 | `../Herman-Jin 观点 rollup.md`（人类主文档，在 research/ 根） |
| 2026-10-02 的语料增量与导入校验 | [corpus-updates/2026-10-02/README.md](corpus-updates/2026-10-02/README.md)（Herman Jin + Serenity） |
| 数字是否可靠 / 修订了什么 | `Herman-Jin 观点 rollup 数据复核 2026-09-18.md` |
| 社媒逐字引文、持仓时间线 | `herman-jin-社媒推荐标的与言论-2026-09-17.md` |
| 观点 2 供需图的数 | `data-hyperscaler-capex-quarterly.csv` + 三张 `*.png`（脚本可复现） |
| 观点 4 Intel 财务底稿 | `intel-ps-work/*.csv` |
| 目录历史清理记录 | `research-目录时效盘点-2026-09-18.md`（含第 8/9 节） |
| trade-the-news / Jev 工作流 | `jev-ling-trade-the-news-2026-09-20.md` + `jev-ling-repro/`（独立题材） |
| SNPS 快速调研 | `herman-jin-逻辑下的SNPS快速调研-2026-09-21.md`（rollup 框架的下游，非支撑） |
| Herman Jin / Serenity 首轮方法蒸馏 | [55 个案例、方法卡与观点变化](kol-distillation-2026-09-26/README.md)（独立研究，2026-09-26） |
| INTC 与 CPU 行业条件分析 | [需求、产品利润、外部代工及两人方法的应用](intc-cpu-analysis-2026-09-26/README.md)（独立研究，2026-09-26） |
| Post-training 推理报告 | [从模型改进到算力、CPU 与股东收益的条件链](post-training-inference-2026-09-26/README.md)（独立研究，2026-09-26） |

## 1. 主文档与支撑（rollup 生态）

| 文件 | 角色 | 支撑 rollup 何处 | 约定 |
|---|---|---|---|
| `../Herman-Jin 观点 rollup.md` | **主汇总研报（唯一结论入口，在 research/ 根）** | — | 改观点先改这里；文末有「数据修订记录」 |
| `Herman-Jin 观点 rollup 数据复核 2026-09-18.md` | 对 rollup 的逐条复核 | 元信息「数据复核」、全部修订依据 | rollup 直链；与 rollup 修订表应同步 |
| `herman-jin-社媒推荐标的与言论-2026-09-17.md` | 上游社媒引文库 | 观点 3 点名/持仓；元信息「社媒信源」 | 逐字摘录；语料≠推荐，社媒=买卖动作 |
| `intel-ps-work/intc_revenue.csv` | Intel 收入序列 | 观点 4 估值校准底稿 | 数据资产，勿手改结构 |
| `intel-ps-work/intc_shares.csv` | Intel 股本序列 | 同上 | 同上 |

rollup 还链到 `../../Herman Jin/research/` 下的价格验证、推理链、转录审计等（不在本目录）。

## 2. 数据真源（观点 2 / CAPEX）

| 文件 | 主从 | 说明 |
|---|---|---|
| `data-hyperscaler-capex-quarterly.csv` | **表格真源** | agent 读数**优先用 csv**；46 行，2015Q1→2026Q2，单位百万美元 |
| `data-hyperscaler-capex-quarterly.json` | **派生 + 长历史** | 仅由 `fetch_hyperscaler_capex.py` 写入，**勿手改**；含 `unit`/`note` 元信息，且 `series` 历史可长于 csv（按财年差分生成）。需要元信息或 2015 年前序列时再用 json |
| `fetch_hyperscaler_capex.py` | 取数脚本 | SEC XBRL 一手；差分自检；同时写 csv+json |

**勿删其一**：绘图脚本双读互为 fallback；删前必须改 `fetch_*` 与 `make_demand_capex_chart.py`。

## 3. 图件 + 复现脚本（观点 1/2；均被 rollup 引用）

| 图 | 脚本 | rollup |
|---|---|---|
| `supply-capacity-cowos-hbm-2023-2028.png` | `make_supply_capacity_chart.py` | 观点 2 图 1 |
| `demand-capex-vs-supply-2023-2026.png` | `make_demand_capex_chart.py` | 观点 2 图 2 |
| `supply-demand-gap-2024-2027.png` | `make_supply_demand_gap_chart.py` | 观点 2 图 3 |

- 观点 1 云增速原配图已于 2026-09-22 删除；数值在 rollup 正文，可依正文重绘。
- 改口径：**先改 rollup 正文，再改脚本并重跑**，图以脚本输出为准。

## 4. 独立题材（与 rollup 无支撑关系）

| 路径 | 说明 |
|---|---|
| `jev-ling-trade-the-news-2026-09-20.md` | Jev×Ling 工作流拆解（方法） |
| `jev-ling-repro/` | 同上主题的**本地复刻**实现与产物（README 在子目录） |
| `trade-the-news-demo.mp4` + `trade-the-news-frame-{start,final}.png` | 原版推文视频与抽帧；**被 jev-ling md 直引**，与 repro 产物不是重复 |
| `herman-jin-逻辑下的SNPS快速调研-2026-09-21.md` | 用 rollup 框架做的下游推导，**不支撑 rollup 结论** |
| [kol-distillation-2026-09-26/](kol-distillation-2026-09-26/README.md) | Herman Jin 与 Serenity 的首轮观点、推理案例、方法卡及证据审阅；独立于既有 rollup |
| [intc-cpu-analysis-2026-09-26/](intc-cpu-analysis-2026-09-26/README.md) | INTC 与 CPU 行业的条件分析；应用两人方法卡并核验 Intel、AMD、Arm 等一手披露，含 [Intel 一手核验底稿](intc-cpu-analysis-2026-09-26/intel-primary.md) |
| [post-training-inference-2026-09-26/](post-training-inference-2026-09-26/README.md) | 后训练需求与供应链推理，承接 INTC / CPU 分析；含[一手资料与资源归因底稿](post-training-inference-2026-09-26/primary-evidence.md) |

## 5. 元文档与归档

| 路径 | 说明 |
|---|---|
| `research-目录时效盘点-2026-09-18.md` | 时效盘点 + 第 8/9 节删除与改口径执行记录；被复核报告引用 |
| `_archive/cds-sidecar/` | CDS 旁证图与脚本（原支撑文档 09-22 已删）；**观点 9 以 rollup 正文 + 复核英文来源为准**。详见该目录 README |

## 6. 已移除（勿找回为「缺失」）

2026-09-18 / 09-22 分批入 `~/.Trash/`：三份 `*-notes-2026-09-17.md`、CDS 可得性与映射 md、Azure 标签云增速图及脚本、若干过期/快照报告。SHA 与明细见盘点第九节。原 notes 口径已并入 rollup 观点 2 正文。
