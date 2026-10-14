# Earnings Preview (Pre-Release Workflow)

只在财报期间尚未发布、需要建立前瞻时读取。复盘模式不要读本文件。

## 1. Establish Context

- 确认公司与报告季度，以及 fiscal calendar 与 calendar quarter 的对应关系。
- 取得 earnings date 和时段（盘前/盘后）；口径以发行人 IR 或公告为准，不可得时标 `SOURCE_UNAVAILABLE`。
- 收集上一季度正式 guidance（记录发布日期）与上一季度 earnings call 中与前瞻相关的表述。
- 用户提供了 prior model/estimates 时作为 `USER_PROVIDED` 基线；没提供则明确列为缺失基线。

## 2. Key Metrics Framework

建立针对本公司的「看什么」清单，按重要性排序。指标必须与本公司披露口径一致，不与公司实际披露的 KPI 不符地自造指标。

**财务指标**

- Revenue：总量与分部，相对公开 guidance 或 `USER_PROVIDED` estimate。
- EPS：GAAP 与 adjusted 口径分开。
- Margins：gross / operating / net 的扩张或收缩。
- Free cash flow。
- Forward guidance：相对 prior dated public guidance 或 `MODEL_DERIVED` 情景。

**经营指标（按行业选择）**

- Tech/SaaS：ARR、net retention、RPO、customer count。
- Retail：same-store sales、traffic、basket size。
- Industrials：backlog、book-to-bill、price vs. volume。
- Financials：NIM、credit quality、loan growth、fee income。
- Healthcare：scripts、patient volumes、pipeline updates。

## 3. Scenario Analysis

| Scenario | Revenue | EPS | Key Driver | Stock Reaction |
|---|---|---|---|---|
| Bull | | | | |
| Base | | | | |
| Bear | | | | |

每个情景写清三件事：需要发生什么经营结果、管理层怎样表述会对应这个情景、历史上类似结果的股价反应（只能用已打开的公开来源或 `USER_PROVIDED` 数据）。

情景数值只能来自公开 guidance、`USER_PROVIDED` 或带推导说明的 `MODEL_DERIVED`。Base 情景若标为 `MODEL_DERIVED` 且日期早于事件，到复盘时可直接作为比较基线。

## 4. Catalyst Checklist

列出 3–5 个决定股价反应的事项，每项写「指标/事件 — 相对哪个基线 — 为什么重要」。基线不可得时写 `SOURCE_UNAVAILABLE`，不留空。

## 5. Output

一页式预览，包含：公司、季度、财报日期/时段、公开 guidance 基线、内部情景表、按重要性排序的指标清单、催化剂清单，以及交易面观察（近期股价表现；期权隐含波动只在有已验证公开报价或 `USER_PROVIDED` 期权数据时给出，否则 `SOURCE_UNAVAILABLE`）。

## 来源规则

不使用 survey figures、whisper number、机构调查或付费研究的估计；不可获得的 transcript 不从登录/订阅页面补齐。前瞻产物只是「事件前的判断框架」，不得写成对未发布数字的断言。
