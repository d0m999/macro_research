# Herman Jin 自 2025 年以来的数据源引用统计

> 独立报告；统计截止 2026-09-02
>
> 覆盖 2025-01-07 至 2026-08-25，共 56 期、49,683 个带时间戳的转录片段、751 张归档幻灯片
>
> 本报告统计 Herman Jin **实际拿来论证的材料**，不评价来源本身是否正确，也不构成投资建议

## 一、核心结论

Herman Jin 的信息框架不是“读新闻后猜涨跌”，而是把四层材料叠在一起：

```text
政策与官方宏观数据
  → 利率、汇率、信用与流动性
  → CTA / gamma / Prime Book 等仓位和市场结构
  → 公司财报、CAPEX、供应链与产品采用
  → 形成行业或股票判断
```

最值得注意的统计结果：

1. **Goldman Sachs 是最常出现的可归因机构来源。** 口述明确引用其研究、图表、预测、FCI、Prime Book、Momentum Factor 或 Trading Desk 数据的有 **32/56 期**；幻灯片可辨认 Goldman/GS 来源的有 **25/56 期**；两者合并去重后覆盖 **38/56 期**。
2. **行情是全覆盖底座。** 56/56 期都会用股票、指数、利率、汇率、商品、信用或估值序列，但绝大多数时候没有交代数据终端、复权方式和截点。
3. **政策信息与仓位数据几乎同等重要。** 未具名政策/法律/监管材料覆盖 50 期；未具名仓位/资金流/技术面覆盖 48 期。命名指标中，CTA/波控仓位覆盖 30 期，dealer gamma 覆盖 16 期，Prime Book 覆盖 8 期。
4. **公司与产业层材料是 AI 主线的关键。** 财报、指引与 CAPEX 覆盖 47 期，供应链/产能/渠道检查覆盖 35 期，但经常没有具体报告链接，因此只能判定材料类型，不能确定上游出处。
5. **官方宏观数据使用广，但经常只报指标名。** CPI 21 期、非农 17 期、失业率 14 期、PCE 12 期；这能确认数据族，却未必能从转录确认发布表格、季调版本或修订值。
6. **新闻媒体不是主轴。** 可明确识别的 Bloomberg 画面/终端为 5 期，TradingView 为 5 期，Wall Street Journal 为 1 期。媒体更像补充材料，核心推理仍由宏观、市场结构和公司/产业数据完成。

## 二、统计口径

### 2.1 四层证据等级

- **A：明确归因。** 口述明确说出机构、平台、报告所有者、官员讲话或正式文件。
- **B：命名指标。** 明确说出 CPI、CTA、VIX、CDS 等指标，但没有说明本次数据的上游供应商。
- **V：画面可见。** 口述未点名，但归档幻灯片能清楚看到 source、版权、logo 或平台水印。
- **C：只能推断材料类型。** 能判断用了行情、财报、供应链或私人渠道，却不能追溯具体文件或数据提供者。

### 2.2 “引用次数”如何计算

主口径是 **来源 × 节目期**：同一期对同一来源无论反复讲多少次，只算 1 次。因此“Goldman 口述 32 次”表示 32 期用过，不是只说了 32 句话。

报告不把公司名、股票代码或“市场认为”本身算作来源。只有公司财报/指引被用于论证时，才计入公司披露类型；只有 Trump、Powell 或银行的讲话、帖子、报告、模型被使用时，才计入命名来源。

自动转录对专名有明显误识别：Goldman 常被写成“狗门、拱门、国门”，Powell 常被写成 `J-PAL/JPAL`，Nonfarm Payrolls 常被写成“能防配肉/飞龙就业”，VIX 常被写成 `Volvix`。本报告先检索词形，再结合前后文和幻灯片人工归一。

## 三、数据材料类型排名

这是最适合回答“他的推理主要依靠哪类数据”的排名。一次节目可以同时属于多类，不能把各行相加当作节目总数。

| 排名 | 数据材料类型 | 覆盖期数 | 占 56 期 | 可确认到什么程度 |
|---:|---|---:|---:|---|
| 1 | 市场价格、利率与估值序列 | 56 | 100.0% | 可确认使用行情；通常无法确认终端、复权与截点 |
| 2 | 政策、法律与监管材料 | 50 | 89.3% | 常能确认事件，未必有文件版本或原始链接 |
| 3 | 仓位、资金流与技术面 | 48 | 85.7% | 常见 CTA、gamma、Prime Book；不少仓位图未注明模型 |
| 4 | 公司财报、业绩指引与 CAPEX | 47 | 83.9% | 能确认公司层数据；较少报具体财报页码 |
| 5 | 供应链、产能与渠道检查 | 35 | 62.5% | 常见缺货、良率、排产、库存；上游出处最不透明 |
| 6 | 产品使用、用户与采用率 | 25 | 44.6% | 常用于 AI/Token 需求；样本与统计口径较少披露 |
| 7 | 未具名一致预期/卖方估计 | 21 | 37.5% | 只说“市场/华尔街预期”时不归给具体机构 |
| 8 | 私人渠道、轶事或“情报” | 12 | 21.4% | 无法独立复现，证据等级最低 |

## 四、具体发布者、机构与平台排名

下表按“合并覆盖期数”排序。口述和画面可能在同一期重叠，因此合并数不等于两列简单相加。

| 排名 | 具体来源 | 口述明确 A | 画面可见 V | 合并覆盖期数 | 主要用途 |
|---:|---|---:|---:|---:|---|
| 1 | Goldman Sachs / GS | 32 | 25 | **38** | 宏观预测、Prime Book、CTA/Trading Desk、FCI、Momentum Factor、盈利与 CAPEX |
| 2 | Trump 公开讲话/帖子 | 31 | 2 个 Truth Social 画面 | **31** | 关税、财政、监管、地缘政治与政策尾险 |
| 3 | Federal Reserve / FOMC | 19 | 多期会议/点阵图画面已含在口述 | **19** | 利率路径、通胀反应函数、流动性与政策约束 |
| 4 | Bloomberg | 0 | 5 | **5** | Bloomberg 终端行情、CRIC 图表、Bloomberg AI 新闻摘要 |
| 5 | TradingView | 1 | 4 | **5** | VIX、加密资产与价格图表 |
| 6 | Morgan Stanley | 2 | 2 | **4** | 标普目标、中国消费/通缩、hyperscaler 折旧 |
| 7 | Polymarket | 3 | 2 | **4** | 政府关门、Fed 主席与选举概率 |
| 8 | UBS | 2 | 1 | **3** | 中国消费/通缩、估值测算、系统化资金评论 |
| 9 | Truth Social（作为平台） | 1 | 2 | **3** | Trump 原帖；它是上表“Trump 公开讲话/帖子”的子集 |
| 10 | JPMorgan 研究/交易数据 | 2 | 0 | **2** | 利率判断与仓位观点；讨论 JPM 财报不算来源 |
| 11 | Bank of America / BofA | 1 | 2 | **2** | Momentum/去杠杆与长端利率观点 |
| 12 | IEA | 2 | 0 | **2** | 释储与油价情景 |
| 13 | Alex Younger / 前 MI6 负责人 | 2 | 0 | **2** | Goldman 活动中的地缘政治判断 |
| 14 | Wall Street Journal | 1 | 0 | **1** | Kevin Warsh 访谈与报道 |
| 15 | FRED | 0 | 1 | **1** | 宏观/利率图表 |
| 16 | CRIC | 0 | 1 | **1** | 中国房地产销售图表，经 Bloomberg 展示 |
| 17 | ARD/Infratest dimap | 0 | 1 | **1** | 德国选举民调 |
| 18 | U.S. Department of Labor | 0 | 1 | **1** | 通胀/劳动力图表 |
| 19 | CME | 1 | 0 | **1** | 与 Binance 对照的期货/OI 数据 |
| 20 | LME | 1 | 0 | **1** | 贵金属库存/交易讨论 |
| 21 | OPEC | 1 | 0 | **1** | 供给决定与油价判断 |
| 22 | University of Michigan | 1 | 0 | **1** | 通胀预期调查 |
| 23 | Citadel Securities | 0 | 1 | **1** | 2026-06-30 系统化资金/交易台材料 |

几个边界需要特别说明：

- 2025-05-20、2025-07-22、2026-07-14 中 Goldman/JPMorgan 主要作为公司、交易对手或历史案例出现，已从“研究来源”中剔除。
- 2026-01-20 的 Bank of America/Citi 是银行名单，不计卖方来源。
- CME 在 3 期被提到，但只有 2025-06-10 可明确确认其交易/OI 数据用于论证，所以只计 1 期。
- Binance 在 7 期出现；可明确确认拿持仓/期货数据作论证的核心场景是 2025-06-10，2025-09-23 另有数据观察但 Herman 同时弱化了其对主流币定价的解释力，因此不把 7 次平台出现等同于 7 次数据引用。

## 五、命名指标与数据族排名

指标名不等于数据供应商。以下统计说明 Herman 实际反复观察什么。

| 排名 | 命名指标/数据族 | 覆盖期数 | 说明 |
|---:|---|---:|---|
| 1 | CTA / volatility-control 仓位 | **30** | 系统化买卖压力；同一期多次更新仍只计 1 |
| 2 | CPI | **21** | 美国与中国通胀、关税传导 |
| 3 | CDS / credit spread | **18** | 公司融资与系统性信用风险 |
| 4 | Nonfarm Payrolls | **17** | 就业强弱及 Fed 反应函数 |
| 5 | Options / dealer gamma | **16** | 对冲方向、负 gamma 与加速波动 |
| 6 | 美债发行、拍卖或收益率曲线 | **14** | 财政供给、期限溢价、长端利率 |
| 7 | 失业率 | **14** | 衰退与 Fed put 的触发条件 |
| 8 | PCE inflation | **12** | Fed 更关注的通胀口径 |
| 9 | VIX | **11** | 恐慌、波动率与被动去杠杆 |
| 10 | Goldman/Global Prime Book | **8** | 对冲基金净/总敞口、行业拥挤度 |
| 11 | SLR / eSLR 规则 | **8** | 银行资本释放与国债承接能力 |
| 12 | ETF / fund flows | **7** | 跨地区、风格和被动资金流 |
| 13 | TGA / RRP / SOFR / repo / reserves | **7** | 美元流动性与银行准备金 |
| 14 | ADP Employment Report | **5** | 政府数据缺口期的私营就业替代指标 |
| 15 | 正式 GDP 数据 | **5** | 仅统计明确引用已公布数据，不含所有“GDP”讨论 |
| 16 | ISM / PMI | **4** | 制造业与服务业景气 |
| 17 | Consumer Confidence / Sentiment（不含 Michigan） | **3** | 消费与就业预期 |
| 18 | Retail Sales | **4** | 私营消费和增长路径 |
| 19 | PPI | **3** | 上游通胀与关税/能源传导 |
| 20 | Polymarket 概率 | **3** | 仅口述；加入画面证据后平台合并覆盖 4 期 |
| 21 | Initial Jobless Claims | **2** | 就业转弱的高频指标 |
| 22 | IEA 行动/数据 | **2** | 原油供给与释储 |
| 23 | Michigan inflation expectations | **1** | 家庭通胀预期调查 |

## 六、代表性证据定位

| 来源 | 代表时间戳 | 本地证据 | 为什么算引用 |
|---|---|---|---|
| Goldman 图表 | 2025-01-21 04:03 | [L18](../market-overview/market-overview-2025-01-21/transcript.jsonl#L18) | 明说“这两个是高盛的图” |
| CTA | 2025-01-07 08:45 | [L217](../market-overview/market-overview-2025-01-07/transcript.jsonl#L217) | 用 CTA 回补推导市场买盘 |
| Fed/FOMC | 2025-01-14 02:22 | [L50](../market-overview/market-overview-2025-01-14/transcript.jsonl#L50) | 用 FOMC 反应函数解释利率重定价 |
| 非农 | 2025-01-14 01:41 | [L36](../market-overview/market-overview-2025-01-14/transcript.jsonl#L36) | 明确把 Nonfarm Payrolls 当就业数据 |
| CPI | 2025-01-14 26:56 | [L706](../market-overview/market-overview-2025-01-14/transcript.jsonl#L706) | 用基数/滞后因素判断通胀路径 |
| dealer gamma | 2025-03-18 13:08 | [L390](../market-overview/market-overview-2025-03-18/transcript.jsonl#L390) | 用 gamma 对冲方向解释跌势加速 |
| Prime Book | 2025-02-25 05:29 | [L123](../market-overview/market-overview-2025-02-25/transcript.jsonl#L123) | 用 prime-broker 仓位判断小盘/TMT 拥挤度 |
| ADP | 2025-12-16 02:39 | [L50](../market-overview/market-overview-2025-12-16/transcript.jsonl#L50) | 明说政府关门期间就业数据依靠 ADP |
| CDS | 2025-11-18 06:21 | [L238](../market-overview/market-overview-2025-11-18/transcript.jsonl#L238) | 用 Oracle CDS 判断债务与融资担忧 |
| IEA | 2026-03-17 04:52 | [L95](../market-overview/market-overview-2026-03-17/transcript.jsonl#L95) | 用 IEA 释储/行动修正油价情景 |
| Polymarket | 2025-09-30 16:24 | [L385](../market-overview/market-overview-2025-09-30/transcript.jsonl#L385) | 用预测概率判断政府关门 |
| Wall Street Journal | 2026-04-21 21:41 | [L597](../market-overview/market-overview-2026-04-21/transcript.jsonl#L597) | 明说采用其 Kevin Warsh 专访/报道 |
| Bloomberg/CRIC 画面 | 2025-03-04 06:19 | [slide-004](../market-overview/market-overview-2025-03-04/slides/slide-004.png) | 图中清楚显示 `Source: CRIC` 与 Bloomberg 标识 |
| ARD/Infratest 画面 | 2025-03-11 09:40 | [slide-007](../market-overview/market-overview-2025-03-11/slides/slide-007.png) | 德国选举图明确标注来源 |
| FRED 画面 | 2025-05-20 25:40 | [slide-021](../market-overview/market-overview-2025-05-20/slides/slide-021.png) | 图表画面显示 FRED |
| TradingView 画面 | 2025-06-24 19:00 | [slide-005](../market-overview/market-overview-2025-06-24/slides/slide-005.png) | 图表带 TradingView 水印 |

## 七、56 期逐期数据源清单

缩写：`A`=口述明确归因，`B`=口述命名指标但上游未说明，`V`=幻灯片可见来源。最后一列只列无法继续归因的材料类型：行情、政策、仓位、公司、供应链、采用、一致预期、私人渠道。

### 2025 年

| 日期 | 显式来源、平台与命名指标 | 无法继续归因的材料类型 |
|---|---|---|
| [01-07](../market-overview/market-overview-2025-01-07/manifest.json) | X/社媒情绪(A)；TGA/RRP/SOFR(B)；CTA(B)；dealer gamma(B) | 政策、仓位、行情、一致预期 |
| [01-14](../market-overview/market-overview-2025-01-14/manifest.json) | ADP(A)；Fed/FOMC(A)；失业率(B)；Trump讲话(A)；基金流(B)；CPI(B)；Goldman(A/V)；非农(B)；Bloomberg(V) | 行情、公司、政策、仓位 |
| [01-21](../market-overview/market-overview-2025-01-21/manifest.json) | Trump讲话(A)；Goldman(A)；非农(B) | 政策、行情、私人渠道、供应链、公司 |
| [02-11](../market-overview/market-overview-2025-02-11/manifest.json) | 失业率(B)；CPI(B)；美债发行/曲线(B)；Trump讲话(A)；Goldman(V) | 仓位、一致预期、政策、供应链、公司、采用、行情 |
| [02-18](../market-overview/market-overview-2025-02-18/manifest.json) | PCE/CPI/PPI/失业率(B)；Fed/FOMC(A)；Goldman(A/V)；U.S. Department of Labor(V) | 仓位、政策、公司、行情、采用、一致预期 |
| [02-25](../market-overview/market-overview-2025-02-25/manifest.json) | Prime Book(B)；Michigan调查(A)；Trump讲话(A)；Goldman(A/V)；CTA/gamma/VIX(B)；Truth Social(V) | 一致预期、仓位、公司、行情 |
| [03-04](../market-overview/market-overview-2025-03-04/manifest.json) | ISM/PMI、消费者信心、PCE、初请、非农(B)；Trump讲话(A)；Bloomberg/CRIC(V) | 私人渠道、行情、政策、供应链、公司 |
| [03-11](../market-overview/market-overview-2025-03-11/manifest.json) | Fed/FOMC、Trump讲话、Goldman(A)；ISM/PMI、CPI、CTA、gamma、非农、VIX(B)；Bloomberg、ARD/Infratest(V) | 行情、仓位、公司、政策、供应链 |
| [03-18](../market-overview/market-overview-2025-03-18/manifest.json) | PPI、零售、美债曲线、CPI、CTA、gamma、非农、VIX(B)；Goldman(A/V)；Bloomberg(V) | 政策、仓位、行情 |
| [04-01](../market-overview/market-overview-2025-04-01/manifest.json) | Trump讲话、Goldman(A/V)；CTA、CDS/信用利差(B) | 仓位、一致预期、行情、政策 |
| [04-08](../market-overview/market-overview-2025-04-08/manifest.json) | Prime Book、基金流、非农(B)；Trump讲话(A)；Goldman(V) | 政策、仓位、一致预期、行情 |
| [04-15](../market-overview/market-overview-2025-04-15/manifest.json) | Trump讲话、Goldman(A/V)；PCE、TGA/repo、CDS(B) | 政策、一致预期、仓位、行情 |
| [04-22](../market-overview/market-overview-2025-04-22/manifest.json) | Trump/Fed/FOMC/Goldman(A)；失业率、零售、consumer sentiment、美债曲线、基金流(B)；Truth Social(V) | 行情、政策、仓位 |
| [04-29](../market-overview/market-overview-2025-04-29/manifest.json) | Trump讲话、IEEPA/Sections 232/301/338(A)；美债曲线、CTA、VIX(B) | 政策、行情、仓位、公司 |
| [05-13](../market-overview/market-overview-2025-05-13/manifest.json) | Trump、Goldman、Morgan Stanley(A)；CTA(B) | 私人渠道、仓位、政策、一致预期、行情、公司 |
| [05-20](../market-overview/market-overview-2025-05-20/manifest.json) | Bessent/财政部、正式GDP(A/B)；美债曲线、CTA、VIX(B)；FRED(V) | 仓位、行情、政策、供应链 |
| [06-03](../market-overview/market-overview-2025-06-03/manifest.json) | Trump、Goldman(A)；美债曲线、CTA、非农(B) | 仓位、公司、行情、采用、政策、一致预期、供应链 |
| [06-10](../market-overview/market-overview-2025-06-10/manifest.json) | OBBB/Section 899、Goldman、CME、UBS、Morgan Stanley(A)；消费者信心、Prime Book、GDP、基金流、加密基差、CTA、非农(B) | 政策、一致预期、公司、行情、私人渠道、仓位 |
| [06-24](../market-overview/market-overview-2025-06-24/manifest.json) | OBBB/Section 899、Goldman(A)；TradingView(V) | 政策、行情、供应链、公司 |
| [07-02](../market-overview/market-overview-2025-07-02/manifest.json) | OPEC、Fed/FOMC、OBBB、Elon Musk、Trump(A)；失业率、CTA、CDS(B) | 公司、仓位、政策、行情、供应链 |
| [07-08](../market-overview/market-overview-2025-07-08/manifest.json) | OBBB、SLR/eSLR、Trump、Fed/FOMC、ADP、Goldman(A)；TGA/RRP、失业率、ISM/PMI、非农(B) | 政策、一致预期、行情、公司、采用、供应链 |
| [07-22](../market-overview/market-overview-2025-07-22/manifest.json) | Trump、Fed/FOMC、SLR/eSLR(A)；CPI、CTA(B) | 政策、仓位、行情、公司、采用、供应链 |
| [08-05](../market-overview/market-overview-2025-08-05/manifest.json) | OBBB、Trump(A)；失业率、PCE、CDS、非农(B) | 采用、仓位、政策、公司、行情 |
| [08-12](../market-overview/market-overview-2025-08-12/manifest.json) | OBBB、Fed/FOMC、Trump、Goldman(A)；CPI、CTA、非农(B) | 公司、一致预期、行情、政策、采用、供应链、仓位 |
| [09-02](../market-overview/market-overview-2025-09-02/manifest.json) | 法院判决(B)；Trump、Fed/FOMC、Goldman(A)；GDP、美债曲线、CTA、gamma(B) | 政策、仓位、行情、供应链、私人渠道 |
| [09-09](../market-overview/market-overview-2025-09-09/manifest.json) | Fed/FOMC、Trump、Goldman(A) | 政策、仓位、行情、公司、一致预期、采用 |
| [09-23](../market-overview/market-overview-2025-09-23/manifest.json) | Fed/FOMC、OBBB(A)；失业率、PCE、零售、CPI、非农(B)；TradingView(V) | 采用、政策、仓位、行情、供应链、私人渠道、公司 |
| [09-30](../market-overview/market-overview-2025-09-30/manifest.json) | Fed/FOMC、Trump、Polymarket(A)；GDP、非农(B) | 一致预期、行情、公司、私人渠道、政策 |
| [10-14](../market-overview/market-overview-2025-10-14/manifest.json) | Trump(A)；美债曲线、CPI(B) | 政策、公司、行情、一致预期、采用、仓位 |
| [10-28](../market-overview/market-overview-2025-10-28/manifest.json) | Fed/FOMC(A)；CPI、PCE、CDS、VIX(B) | 政策、行情、公司、仓位、供应链 |
| [11-18](../market-overview/market-overview-2025-11-18/manifest.json) | SLR/eSLR、Goldman(A)；失业率、CTA、CDS(B) | 供应链、政策、公司、采用、仓位、行情 |
| [11-25](../market-overview/market-overview-2025-11-25/manifest.json) | Fed/FOMC、ADP、Bessent、SLR/eSLR、IEEPA/Sections、Goldman(A)；初请、失业率、CPI、PCE、美债曲线、CTA、gamma、CDS、非农(B) | 公司、政策、一致预期、行情、仓位 |
| [12-09](../market-overview/market-overview-2025-12-09/manifest.json) | X/社媒情绪、UBS(A)；美债曲线、PCE、CTA(B) | 政策、仓位、行情、公司、供应链、私人渠道 |
| [12-16](../market-overview/market-overview-2025-12-16/manifest.json) | ADP、Fed/FOMC、SLR/eSLR、Trump(A)；失业率、CDS、非农(B) | 采用、政策、行情、公司、供应链、仓位 |
| [12-30](../market-overview/market-overview-2025-12-30/manifest.json) | Goldman(A)；GDP、美债曲线、PCE、CPI、失业率、CDS(B) | 采用、政策、供应链、行情、仓位 |

### 2026 年

| 日期 | 显式来源、平台与命名指标 | 无法继续归因的材料类型 |
|---|---|---|
| [01-06](../market-overview/market-overview-2026-01-06/manifest.json) | Trump(A)；基金流(B) | 供应链、私人渠道、政策、行情、仓位、采用、公司 |
| [01-20](../market-overview/market-overview-2026-01-20/manifest.json) | Trump、Goldman(A)；CPI、美债曲线(B) | 行情、采用、供应链、公司、政策 |
| [01-27](../market-overview/market-overview-2026-01-27/manifest.json) | TradingView(V) | 采用、仓位、政策、行情、公司、私人渠道、供应链 |
| [02-03](../market-overview/market-overview-2026-02-03/manifest.json) | Kevin Warsh、Trump、LME、Polymarket(A)；Goldman(V) | 仓位、政策、供应链、行情、公司 |
| [02-10](../market-overview/market-overview-2026-02-10/manifest.json) | ADP、Goldman(A/V)；零售、CPI、ISM/PMI、CDS、非农(B) | 行情、政策、供应链、公司、仓位 |
| [03-03](../market-overview/market-overview-2026-03-03/manifest.json) | Trump、SLR/eSLR、Goldman(A/V)；基金流、CTA、gamma(B) | 公司、政策、仓位、采用、行情 |
| [03-10](../market-overview/market-overview-2026-03-10/manifest.json) | Goldman(A)；CPI、PCE、失业率、CTA、gamma(B)；TradingView(V) | 政策、仓位、行情、供应链、公司 |
| [03-17](../market-overview/market-overview-2026-03-17/manifest.json) | IEA、Goldman、JPMorgan(A/V)；CPI、CTA、gamma、CDS(B) | 仓位、供应链、行情、政策、公司、采用 |
| [03-24](../market-overview/market-overview-2026-03-24/manifest.json) | Fed/FOMC、Trump、IEA、Goldman(A/V)；Morgan Stanley、BofA(V)；PCE、失业率、CTA、gamma(B) | 行情、政策、供应链、公司、采用、仓位 |
| [04-14](../market-overview/market-overview-2026-04-14/manifest.json) | X/社媒情绪、Polymarket(A)；Prime Book、CPI、TGA/RRP、CTA(B)；Goldman(V) | 仓位、行情、公司、供应链、采用、政策 |
| [04-21](../market-overview/market-overview-2026-04-21/manifest.json) | Trump、WSJ、Goldman(A/V)；Prime Book、TGA/RRP、CTA、gamma(B)；Polymarket(V) | 仓位、采用、行情、公司、一致预期、供应链 |
| [05-05](../market-overview/market-overview-2026-05-05/manifest.json) | Fed/FOMC、Goldman(A/V)；PCE、Prime Book、TGA/SOFR、CTA、CDS(B) | 行情、公司、采用、仓位、政策 |
| [05-19](../market-overview/market-overview-2026-05-19/manifest.json) | Trump、Goldman(A/V)；CPI、PPI、CTA、CDS(B) | 供应链、仓位、采用、公司、行情、一致预期 |
| [06-02](../market-overview/market-overview-2026-06-02/manifest.json) | SLR/eSLR(A)；TGA/SOFR、CDS(B) | 仓位、供应链、私人渠道、政策、行情、公司、一致预期、采用 |
| [06-09](../market-overview/market-overview-2026-06-09/manifest.json) | Goldman(V)；TradingView(A)；基金流、CPI、CTA、gamma、CDS、VIX(B) | 私人渠道、公司、仓位、供应链、行情、一致预期 |
| [06-23](../market-overview/market-overview-2026-06-23/manifest.json) | Fed/FOMC(A) | 公司、行情、供应链、政策 |
| [06-30](../market-overview/market-overview-2026-06-30/manifest.json) | SLR/eSLR(A)；CTA、gamma、VIX(B)；Goldman、Bloomberg、UBS、Citadel Securities(V) | 公司、政策、行情、供应链 |
| [07-14](../market-overview/market-overview-2026-07-14/manifest.json) | CTA、gamma、CDS、VIX(B) | 公司、供应链、政策、仓位、行情 |
| [07-21](../market-overview/market-overview-2026-07-21/manifest.json) | Trump、Goldman(A/V)；CPI、CTA、gamma、CDS、VIX(B) | 一致预期、行情、仓位、公司、供应链 |
| [08-04](../market-overview/market-overview-2026-08-04/manifest.json) | Fed/FOMC、Goldman、JPMorgan、BofA(A/V)；Prime Book、CPI、美债曲线、CTA、gamma、CDS、非农、VIX(B) | 仓位、政策、行情、公司 |
| [08-25](../market-overview/market-overview-2026-08-25/manifest.json) | Goldman(A/V)；Morgan Stanley(V)；Prime Book、美债曲线(B) | 采用、仓位、公司、行情 |

## 八、如何理解他的多维数据链

从来源结构看，Herman 最常用的不是“多个观点重复证明同一句话”，而是不同层的数据互相约束：

- **宏观层**：CPI/PCE/就业决定增长与 Fed 空间。
- **跨资产层**：长端利率、美元、油价、信用利差验证宏观压力是否进入定价。
- **市场结构层**：CTA、gamma、VIX、Prime Book 判断短期买卖压力和拥挤度。
- **公司/产业层**：财报、CAPEX、供应链和产品采用决定中期盈利能否兑现。
- **政策层**：Trump/Fed/财政部/监管文件改变前四层的情景概率。

因此，后续使用本报告时，最有价值的做法不是问“某个数据源准不准”，而是检查一项结论是否同时得到至少三个相对独立层次的支持。例如半导体观点如果只有股价和 CTA，只是战术信号；若再有 hyperscaler CAPEX、存储缺货和公司毛利率，才形成完整产业链论证。

## 九、局限与复核边界

1. 这是“他使用了什么”的审计，不是对 Goldman、Bloomberg、官方数据或私人渠道真实性的背书。
2. A 类也可能只是机构预测；“来源明确”不等于“预测正确”。
3. B 类只确认指标族，不能自动推定供应商。例如 CPI 通常有官方发布者，但转录未说明具体表格时，本报告不补写。
4. V 类来自 OCR 与画面复核。2026-06-30 的归档幻灯片没有原始时间范围，保留为“画面可见”，不伪造时间戳。
5. C 类的 47 期“公司披露”包含财报、指引、CAPEX 或经营指标中的至少一种，不代表每期都有完整的一手财报。
6. 2025-03-04、2025-07-02、2025-12-30、2026-05-05、2026-05-19 存在标题日期与上传日期冲突；本报告按 manifest 的上传日期排序。
7. 逐期表是保守下限：无法从口述或画面确认上游的材料只留在 C 类，不事后猜测来源。
