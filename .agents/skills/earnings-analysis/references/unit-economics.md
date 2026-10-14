# Unit Economics Deep Dive

只在业务为订阅/用量制，或用户点名 ARR、cohort、NRR、CAC/LTV、payback、revenue quality 时读取。可在前瞻或复盘模式内叠加。

## 1. Identify Business Model

按收入模型裁剪分析口径：

- SaaS/Subscription：ARR、net retention、cohorts。
- Recurring services：contract value、renewal rate、upsell。
- Transaction/usage-based：revenue per transaction、volume、take rate。
- Hybrid：按收入流拆分。

## 2. Core Metrics

**ARR / Revenue Quality**

- ARR bridge：期初 ARR → New → Expansion → Contraction → Churn → 期末 ARR。
- ARR by cohort：vintage 分析，看每个年度 cohort 如何留存与扩张。
- Revenue concentration：Top 10/20/50 客户占比。
- Revenue by type：recurring / non-recurring / professional services。
- Contract structure：ACV 分布、multi-year 占比、auto-renewal 占比。

**Customer Economics**

- CAC = 总 S&M 支出 / 新增客户数。
- LTV =（ARPU × Gross Margin）/ Churn Rate。
- LTV:CAC：给出计算结果，只与有来源的同业集、用户目标或标 `MODEL_DERIVED` 的情景比较。
- CAC payback：回收月数。
- Blended vs. segmented：按企业级/中端/SMB 拆分。

**Retention & Expansion**

- Gross retention：期初 ARR 的留存比例（不含扩张）。
- Net retention（NDR）：含扩张的期初 ARR 留存比例。
- Logo churn 与 dollar churn 分开呈现，两者常不同。
- Expansion rate：upsell + cross-sell 占期初 ARR 比例。

**Cohort Matrix**

| Cohort | Year 0 | Year 1 | Year 2 | Year 3 | Year 4 |
|---|---|---|---|---|---|
| 2020 | $1.0M | $1.1M | $1.2M | $1.1M | |
| 2021 | $1.5M | $1.7M | $1.8M | | |
| 2022 | $2.0M | $2.3M | | | |
| 2023 | $3.0M | | | | |

同时给绝对值与指数化（Year 0 = 100%）两个视图。

**Margin Waterfall**

Revenue → Gross Profit → Contribution Margin → EBITDA，按收入流拆分 gross margin，并计算 acquire/serve/retain 一个客户的完全负荷成本。

## 3. Benchmarking

只与已打开的公开基准或 `USER_PROVIDED` 基准比较；两者都没有时用明确标注的 `MODEL_DERIVED` 情景，不得把阈值表述成事实。

- Rule of 40：只在用户点名该框架时计算，并标注为分析框架而非公司事实。
- Magic Number = 净新增 ARR / 上期 S&M 支出；目标值需有来源、用户输入或 `MODEL_DERIVED` 标注。
- LTV:CAC、gross retention、NDR、CAC payback：给出公司结果与有来源的比较分布，不套用固定 best/good/concerning 档位。

## 4. Revenue Quality Score

| Factor | Score (1-5) | Notes |
|---|---|---|
| Recurring % | | |
| Net retention | | |
| Customer concentration | | |
| Cohort stability | | |
| Growth durability | | |
| Margin profile | | |
| **Overall** | | |

评分理由必须指回上面的具体指标；不要把评分当成结论替代 cohort 视图。

## 5. Output

- Excel workbook：ARR bridge、cohort matrix、单位经济 dashboard。
- Summary slide：关键指标与基准。
- Red flags 与下一步尽调清单。

## 来源规则

客户级数据、ARR bridge、cohort、合同条款和 retention 指标必须有用户提供文件或已打开的发行人 filing/IR 披露，并标注状态。不从私有数据库或不可达的基准报告推断客户经济性；NDR 高于 100% 时必须同时展示 gross retention；contracted ARR 与确认收入分开；professional services 单独评估。
