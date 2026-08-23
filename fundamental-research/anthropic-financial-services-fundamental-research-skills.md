# Anthropic Claude Financial Services 基本面研究 Skills 评估报告

> 核查日期：2026-08-19
> 研究对象：[anthropics/financial-services](https://github.com/anthropics/financial-services)
> 本次复核基线：`main` commit `38652224c10610fa52eee2acee3ac712dcff01f2`
> 原仓库路径：[anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) 已重定向到当前仓库。

## 结论摘要

行业/主题研究最适合从 `market-researcher` agent 进入。它组合调用 `sector-overview`、`competitive-analysis`、`comps-analysis` 和 `idea-generation`，覆盖行业概览、价值链、竞争格局、同业估值和投资标的筛选。

如果研究对象是单家公司，优先使用 `initiating-coverage`；它将公司研究、财务建模、估值分析、图表和报告组装拆成五个有依赖关系的任务。若有数据权限，可再叠加 LSEG 的 `equity-research` 或 S&P Global 的 `tear-sheet`，直接获取共识、财务、估值和公司关系数据。财报跟踪则使用 `earnings-reviewer` agent，或单独使用 `earnings-analysis` 和 `model-update`。

复核后需要修正一个边界表述：仓库没有单独命名为 `supply-chain`、`upstream-downstream` 或“产业链研究”的通用 skill，但并非完全没有上下游内容。除 `sector-overview`、`competitive-analysis` 和 `initiating-coverage` 外，`idea-generation`、`dd-checklist`、`cim-builder` 和 `buyer-list` 也分别覆盖直接/间接受益者、供应链依赖、供应商关系和纵向整合。S&P Global `tear-sheet` 还能读取 customers、suppliers、partners 和 competitors 关系数据。涉及产能、库存、价格传导、贸易流和原材料供需时，仍需补充专门数据源；只有需要将这些环节固化为重复的端到端自动化流程时，才需要自定义 skill。

## 1. 仓库结构

核心基本面内容集中在两个 vertical plugin 中，但完整官方库还包括相邻的私募/投行工作流和 partner-built 数据插件：

- [`financial-analysis/skills/`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills)：建模、估值、竞争分析和 Excel 工作流。
- [`equity-research/skills/`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills)：行业研究、公司覆盖、财报和投资观点跟踪。
- [`private-equity/skills/`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/private-equity/skills)：尽调、单位经济性、投资委员会材料和 portfolio monitoring，属于私募场景下的基本面/商业研究。
- [`investment-banking/skills/`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/investment-banking/skills)：CIM、data pack、公司 profile、并购模型和买方研究，属于交易场景下的相邻研究。
- [`partner-built/lseg/skills/`](https://github.com/anthropics/financial-services/tree/main/plugins/partner-built/lseg/skills)：LSEG 数据驱动的 equity research、宏观和市场分析。
- [`partner-built/spglobal/skills/`](https://github.com/anthropics/financial-services/tree/main/plugins/partner-built/spglobal/skills)：S&P Capital IQ 驱动的公司 tear sheet、earnings preview 和 funding digest。
- [`market-researcher` agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/market-researcher/agents/market-researcher.md)：将多个 skills 编排成行业或主题研究流程。

按当前仓库目录，官方当前有 7 个 vertical plugin、55 个 source skills：`financial-analysis`、`investment-banking`、`equity-research`、`private-equity`、`wealth-management`、`fund-admin` 和 `operations`；partner-built 集合是 `lseg` 和 `spglobal`。agent plugin 共 10 个，另有 51 个 bundled skill 目录。完整集合可对照 [README 的 Skill & Command Reference](https://github.com/anthropics/financial-services#skill--command-reference) 和 [marketplace.json](https://github.com/anthropics/financial-services/blob/main/.claude-plugin/marketplace.json)。本报告只从其中筛选基本面、行业、估值、商业尽调和上下游相关内容，不把全库每个运营 skill 都列入研究清单。

10 个 agent 为 `market-researcher`、`earnings-reviewer`、`model-builder`、`pitch-agent`、`valuation-reviewer`、`meeting-prep-agent`、`gl-reconciler`、`month-end-closer`、`statement-auditor` 和 `kyc-screener`；其中前五个与研究、建模或估值直接相关，其余主要是运营工作流。

仓库还包含 `fund-admin`、`operations` 和 `wealth-management`，它们主要是基金运营、KYC 和财富管理，不属于本报告的基本面研究主范围。仓库 README 将 `financial-analysis` 定义为共享的核心建模与数据连接插件，并将 `equity-research` 定义为覆盖研究和发布工作流插件。[官方仓库 README](https://github.com/anthropics/financial-services#vertical-plugins)

## 2. 基本面研究相关 Skills

| 研究环节 | Skill | 主要用途 | 适用判断 |
|---|---|---|---|
| 行业/赛道研究 | [`sector-overview`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/sector-overview) | 市场规模与增速、市场细分、行业结构、价值链、竞争者、行业趋势、估值和投资含义 | 最直接的行业研究 skill |
| 竞争格局研究 | [`competitive-analysis`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/competitive-analysis) | 竞争者深度分析、市场定位、行业经济性、价值流、利润层级、护城河和竞争情景 | 适合行业横向比较及产业链竞争层次 |
| 单家公司初始覆盖 | [`initiating-coverage`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage) | 公司业务、管理层、产品、客户、渠道、行业、竞争、TAM、风险、财务模型和估值 | 最完整的单公司基本面框架 |
| 财报研究 | [`earnings-analysis`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/earnings-analysis) | 季报、业绩超预期/不及预期、分部数据、利润率、指引、盈利预测和投资逻辑变化 | 已覆盖公司的季度更新 |
| 模型更新 | [`model-update`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/model-update) | 将新财报、管理层指引、宏观变化、商品价格和事件变化纳入模型并重算估值 | 研究跟踪和催化剂更新 |
| 三表与预测 | [`3-statement-model`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/3-statement-model) | 利润表、资产负债表、现金流量表、历史数据和预测 | 财务质量与现金流分析的底层模型 |
| 同业估值 | [`comps-analysis`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/comps-analysis) | 收入、增长、利润率、经营指标、P/E、EV/EBITDA 等同业比较 | 行业估值和相对价值研究 |
| 内在价值 | [`dcf-model`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/dcf-model) | 收入及利润预测、自由现金流、WACC、终值、情景和敏感性分析 | 单公司绝对估值 |
| 主题选股 | [`idea-generation`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/idea-generation) | 按行业、主题、市值、风格、估值和成长性筛选研究标的 | 从行业研究进入标的清单 |
| 财报前瞻 | [`earnings-preview`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/earnings-preview) | 财报前关键指标、预期差和情景分析 | 业绩发布前的基本面跟踪 |
| 盘前/晨会研究 | [`morning-note`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/morning-note) | 晨会摘要、市场事件和交易观点 | 研究结论的日常更新输出 |
| 投资逻辑跟踪 | [`thesis-tracker`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/thesis-tracker) | 维护投资 thesis、事实变化和逻辑修正 | 适合持续跟踪单股或主题 |
| 催化剂跟踪 | [`catalyst-calendar`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/catalyst-calendar) | 记录财报、产品、监管、并购等潜在催化剂 | 将基本面研究连接到事件时间线 |
| 公司财务数据包 | [`datapack-builder`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/investment-banking/skills/datapack-builder) | 从 CIM、发行材料、SEC filings、网页或 MCP 提取并标准化 IS/BS/CF、分部、经营指标、产能利用率和库存周转 | 交易/私募场景的财务数据整理；不是独立估值结论 |
| 公司画像与交易 profile | [`strip-profile`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/investment-banking/skills/strip-profile) | 公司业务、分部、财务、估值、股权、竞争定位和近期事件的高密度 profile | 投行 pitch/deal material 场景；可作为基本面研究输入 |
| 数据驱动的单股快照（partner-built） | [`lseg/equity-research`](https://github.com/anthropics/financial-services/tree/main/plugins/partner-built/lseg/skills/equity-research) | LSEG IBES 共识、公司基本面、历史股价、宏观背景、估值和投资观点 | 需要 LSEG MCP 凭证和数据权限；属于 partner-built |
| 公司 profile 与关系数据（partner-built） | [`spglobal/tear-sheet`](https://github.com/anthropics/financial-services/tree/main/plugins/partner-built/spglobal/skills/tear-sheet) | S&P Capital IQ 公司概况、财务、估值、共识、业绩和 customers/suppliers/partners/competitors 关系 | 需要 S&P Global / Capital IQ 订阅；属于 partner-built |
| 单公司财报前瞻（partner-built） | [`spglobal/earnings-preview-beta`](https://github.com/anthropics/financial-services/tree/main/plugins/partner-built/spglobal/skills/earnings-preview-beta) | 约 4–5 页的单公司财报前瞻，含共识、业绩会、竞争者、估值和新闻 | 目录名为 `earnings-preview-beta`，skill frontmatter 名称为 `earnings-preview-single` |
| 单位经济性 | [`unit-economics`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/private-equity/skills/unit-economics) | ARR cohort、LTV/CAC、净收入留存、回本期、收入质量和利润瀑布 | 偏 SaaS/订阅/经常性收入及私募标的 |
| 投后基本面监控 | [`portfolio-monitoring`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/private-equity/skills/portfolio-monitoring) | 收入、EBITDA、现金、债务、CapEx、营运资金及客户/流失率/订单等 KPI 的实际与计划对比 | 偏私募 portfolio company；不是公开市场通用覆盖模板 |
| 商业与运营尽调 | [`dd-checklist`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/private-equity/skills/dd-checklist) | TAM/SAM/SOM、竞争、客户集中度、定价、合同、供应链和 vendor dependencies | 适合交易尽调；上下游内容是尽调清单的一部分 |
| 尽调会议准备 | [`dd-meeting-prep`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/private-equity/skills/dd-meeting-prep) | 为管理层会、专家访谈、客户 reference 和 advisor session 生成问题、基准和红旗 | 通过一手访谈补足公开披露无法覆盖的商业基本面 |
| 投资委员会研究汇总 | [`ic-memo`](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/private-equity/skills/ic-memo) | 汇总行业、历史财务、管理层、尽调、价值创造和回报分析 | PE 投资决策输出，不是原始数据采集 skill |

上表区分了“核心 equity research / financial analysis”与“相邻或 partner-built”内容。完整仓库还包括 `fund-admin`、`operations`、`wealth-management` 等垂直插件，以及 `audit-xls`、`clean-data-xls` 等模型/数据质量支持 skill；它们对研究流程有帮助，但本身不构成行业或公司基本面结论。`datapack-builder`、`cim-builder`、`deal-screening` 和 `ic-memo` 则是交易研究的相邻工作流，可把披露材料整理成研究输入或投资委员会材料。

### 最推荐的行业研究组合

`market-researcher` 的官方定义要求输出以下内容：

1. 行业概览：市场规模、增长、行业结构、价值链和关键驱动因素。
2. 竞争格局：主要参与者、份额、定位、竞争基础和近期动作。
3. Peer comps：统一口径的同业交易倍数。
4. Ideas shortlist：最能表达主题的 3–5 个标的。

其工作流依次调用 `sector-overview`、`competitive-analysis`、`comps-analysis` 和 `idea-generation`。[market-researcher 定义文件](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/market-researcher/agents/market-researcher.md)

### 相关 Agent 的边界

- `market-researcher`：行业/主题 primer，适合本报告所说的行业研究入口。
- `earnings-reviewer`：已覆盖公司的财报事件闭环，读取 transcript/filings、更新模型并起草 post-earnings note。
- `model-builder`：编排 DCF、LBO、三表和 comps 的 Excel 建模；它是建模执行器，不是额外的数据源或行业研究结论。[model-builder agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/model-builder/agents/model-builder.md)
- `valuation-reviewer`：偏私募 portfolio valuation review，不应与公开市场首次覆盖混用。[valuation-reviewer agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/valuation-reviewer/agents/valuation-reviewer.md)

## 3. 行业、财务和上下游覆盖边界

### 3.1 行业研究

`sector-overview` 是最直接的行业研究 skill，要求研究 TAM、历史和预测增速、市场细分、集中度、商业模式、价值链、进入壁垒、趋势、监管和并购活动。它还要求输出主要公司的收入、增长、EBITDA margin、市场份额、差异化因素和估值概览。

`competitive-analysis` 更强调行业经济性和竞争机制：先定义行业关键指标，再分析市场规模、行业价值如何流动、垂直产业链各层级的典型利润，以及不同公司的定位和护城河。[competitive-analysis SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/financial-analysis/skills/competitive-analysis/SKILL.md)

它并非只有通用模板，官方 references 还按 SaaS、Payments、Marketplaces、Retail、Logistics 等行业组织分析框架；`comps-analysis` 则覆盖 Technology、Industrial、Banks、Consumer、Healthcare 等同业口径。实际使用时仍需检查公司所属行业是否有可比指标，不能把模板覆盖范围当成数据已自动取得。[comps-analysis SKILL.md](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/financial-analysis/skills/comps-analysis/SKILL.md)

### 3.2 公司和财务研究

`initiating-coverage` 的 Task 1 是公司基本面研究，要求覆盖业务模式、产品和服务、客户与 go-to-market、管理层、行业、竞争格局、TAM 和风险；其 Task 2 用历史财务数据建立收入、利润表、现金流、资产负债表和情景模型；Task 3 再做 DCF、可比公司和交易案例估值。[Task 1 公司研究工作流](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task1-company-research.md)

Task 2 的细则还要求关注产品/地理/渠道收入拆分、库存、产能利用率、原材料成本与价格，以及 price-volume-mix；这使它对工业、材料和制造业的财务传导分析比仅看三张表更具体。[Task 2 财务建模工作流](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task2-financial-modeling.md)

`earnings-analysis` 适合已覆盖公司的季度更新，重点是业绩 beat/miss、分部/地区/产品拆分、利润率、管理层指引和盈利预测修订。[earnings-analysis SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/equity-research/skills/earnings-analysis/SKILL.md)

`model-update` 则将新财报、指引、宏观变量、商品价格或公司事件映射为模型假设变化，并更新估值。[model-update SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/equity-research/skills/model-update/SKILL.md)

如果输入材料分散在 CIM、发行材料、SEC filings、网页或 MCP 中，投行的 `datapack-builder` 可先把利润表、资产负债表、现金流量表、分部、经营指标、产能利用率和库存周转标准化成研究/投资委员会可用的数据包；它解决“整理和标准化”，不自动等于财务质量结论。[datapack-builder SKILL.md](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/investment-banking/skills/datapack-builder/SKILL.md)

### 3.3 上游、下游和产业链

本次遍历当前 `main` 的 skill 路径后，没有发现名为 `supply-chain`、`value-chain`、`upstream` 或 `downstream` 的独立通用 skill。因此，原报告若把“没有独立 skill”理解成“完全没有上下游能力”是不完整的；官方库实际把这类内容分散在行业研究、竞争分析、交易尽调和公司关系数据中：

- `sector-overview` 明确要求输出 `value chain map`，说明价值在哪些环节产生和沉淀。
- `competitive-analysis` 要求在垂直产业中拆分价值链层级，并分析各层级的价值流和典型利润率。
- `initiating-coverage` 的公司研究工作流要求识别相关/相邻行业、供应商议价能力、买方议价能力、客户集中度、分销渠道和关键合作伙伴。[Task 1 研究细则](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task1-company-research.md)
- `idea-generation` 对主题投资要求绘制价值链，区分直接受益者、间接受益者、纯标的和多元化公司。[idea-generation SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/equity-research/skills/idea-generation/SKILL.md)
- 私募 `dd-checklist` 的运营尽调明确列出 `Supply chain and vendor dependencies`，同时覆盖客户集中度、定价和合同；这是真正面向供应链风险核查的内容，但场景是交易尽调。[dd-checklist SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/private-equity/skills/dd-checklist/SKILL.md)
- 投行 `cim-builder` 要求整理客户/销售、客户集中度、运营、供应链/供应商关系，以及按分部、地区和客户类型拆分收入；`buyer-list` 还会识别可能通过纵向整合控制供应链或获取利润的买方。[cim-builder SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/investment-banking/skills/cim-builder/SKILL.md)、[buyer-list SKILL.md](https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/investment-banking/skills/buyer-list/SKILL.md)
- partner-built 的 S&P `tear-sheet` 关系数据包含 customers、suppliers、partners 和 competitors，可作为公司关系网络的输入；它不是 Anthropic 自己提供的产业链数据库。[tear-sheet SKILL.md](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/spglobal/skills/tear-sheet/SKILL.md)

因此，这套 skills 可以完成：

- 上游—中游—下游的结构和参与者梳理；
- 各环节商业模式、竞争格局和利润池分析；
- 供应商/客户集中度、议价能力和替代品分析；
- 价格、成本、需求变化对公司收入和利润的传导假设。

但它没有一个专门保证以下数据自动获取和验证的产业链数据接口：

- 原材料价格、库存、产能、开工率和产量；
- 贸易流、运输、交付周期和区域供需；
- 各产业链环节的真实交易量、客户采购量和价格传导滞后；
- 非上市公司和细分供应商的可靠经营数据。

做铝、钢铁、半导体、能源或化工等产业链研究时，应在提示词中明确要求“分环节建链条、列参与者、标注数据日期、区分事实与推断”，并补充交易所、海关、行业协会、公司公告或专业数据库等一手数据。只有在需要把这些数据源、指标和传导模型反复串成统一自动化流程时，才有必要在现有 skills 之上自定义 skill。

## 4. 推荐的基本面研究流程

### 行业/主题研究

```text
market-researcher
  ├─ sector-overview          行业规模、结构、价值链、驱动因素
  ├─ competitive-analysis     竞争者、利润池、市场定位、护城河
  ├─ comps-analysis            同业经营指标和估值倍数
  └─ idea-generation           主题标的筛选
```

### 单家公司研究

```text
initiating-coverage Task 1    公司、管理层、产品、客户、行业、竞争、TAM、风险
        ↓
initiating-coverage Task 2    历史财务、三表、收入拆分、预测和情景
        ↓
initiating-coverage Task 3    DCF、Comps、交易案例和目标价
        ↓
earnings-analysis / model-update
                               后续财报、指引和假设更新
```

如果接入 partner-built 数据源，可在单股研究前后增加：

```text
LSEG equity-research          共识、历史基本面、股价和宏观背景快照
        或
S&P Global tear-sheet         公司财务、估值、共识、业绩及客户/供应商关系
```

财报事件的官方 agent 编排是 `earnings-reviewer`：读取业绩会和 filings，调用 `earnings-analysis`、`model-update`、`audit-xls`，再形成 post-earnings note。它适合持续覆盖，不应被误认为首次覆盖的替代品。[earnings-reviewer agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/earnings-reviewer/agents/earnings-reviewer.md)

### 私募/交易基本面研究

```text
deal-screening / deal-sourcing  初筛公司、行业、规模、客户和风险
        ↓
dd-checklist / dd-meeting-prep  商业、财务、运营、客户、合同和供应链尽调
        ↓
unit-economics / datapack-builder  单位经济性与披露数据标准化
        ↓
ic-memo / portfolio-monitoring  投资决策材料或投后实际与计划监控
```

这条路径是当前官方库补充“上下游、商业质量和运营风险”覆盖的主要来源，但其目标用户是私募和交易团队，不是标准公开市场行业报告。

### 上下游研究的建议提问框架

使用这些 skills 时，建议明确要求报告至少包含：

1. 从原材料/设备到终端需求的完整链条图。
2. 每个环节的主要参与者、市场集中度和竞争方式。
3. 每个环节的价格、成本、毛利或价值分配逻辑。
4. 供应商和客户的集中度、议价能力及替代关系。
5. 产能、库存、开工率、资本开支和需求周期等关键指标。
6. 上游变量向公司收入、毛利率、现金流和估值的传导路径。
7. 每个数字的来源、发布日期和估算/实际标记。

## 5. 最小安装组合

如果目标是基本面研究，建议先安装核心分析插件和 equity research 插件，再按需使用 agent：

```bash
claude plugin marketplace add anthropics/financial-services
claude plugin install financial-analysis@claude-for-financial-services
claude plugin install equity-research@claude-for-financial-services
claude plugin install market-researcher@claude-for-financial-services
# 如需私募尽调、单位经济性和投后监控
claude plugin install private-equity@claude-for-financial-services
```

安装命令和插件名称以仓库当前 README 为准：[Getting Started](https://github.com/anthropics/financial-services#getting-started)。LSEG 和 S&P Global 是 `partner-built` 插件，不应把它们误认为核心 Anthropic 插件；它们分别需要供应商凭证/数据 entitlement 或 Capital IQ / LLM-ready API 订阅，是否可用取决于账户和地区权限。[LSEG README](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/lseg/README.md)、[S&P Global README](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/spglobal/README.md)

## 6. 使用边界

- 这些内容是研究工作流和参考模板，不等于投资、税务、法律或审计建议。
- skill 的输出格式和分析步骤不能替代对当前数据、口径、来源和发布日期的复核。
- 对上下游的定量结论必须区分公司披露、第三方数据、估算和研究者推断。
- `market-researcher` 的 agent 定义要求对每个数字提供来源；无法可靠取得的数字应标记为未核实，而不是自行补齐。
- `market-researcher` 明确定位为 sector/theme primer，不是单一公司的 coverage update；单股更新应转向 `initiating-coverage` 或 `earnings-reviewer`。
- LSEG 和 S&P 的 skill 属于 partner-built，官方说明需要相应数据权限；S&P README 还明确要求用户自行核验模型输出和数据，不能把连接器结果当作无条件正确的事实。
- `audit-xls`、`clean-data-xls` 和 `model-builder` 能提高模型/表格处理质量，但不能替代源数据核验、公司访谈或产业链现场信息。
- 本报告是对 `main` commit `38652224c10610fa52eee2acee3ac712dcff01f2` 的仓库快照复核；官方仓库后续变更后，应重新检查目录和 skill 内容。
- 本报告只记录官方仓库和 skills 的研究用途，不表示这些 skills 已在本仓库的 TradingView/PineScript 工作流中安装或执行。

## 官方来源

1. [Anthropic 官方：Cowork and plugins for finance（背景文章，非当前仓库 SoT）](https://claude.com/blog/cowork-plugins-finance)
2. [Anthropic 官方 financial-services 仓库](https://github.com/anthropics/financial-services)
3. [financial-services 仓库 README：Vertical Plugins](https://github.com/anthropics/financial-services#vertical-plugins)
4. [完整 Skill & Command Reference](https://github.com/anthropics/financial-services#skill--command-reference)
5. [market-researcher agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/market-researcher/agents/market-researcher.md)
6. [sector-overview](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/sector-overview)
7. [competitive-analysis](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/competitive-analysis)
8. [initiating-coverage](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage)
9. [initiating-coverage Task 1](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task1-company-research.md)
10. [initiating-coverage Task 2](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/references/task2-financial-modeling.md)
11. [earnings-analysis](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/earnings-analysis)
12. [model-update](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/model-update)
13. [comps-analysis](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/comps-analysis)
14. [dcf-model](https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/financial-analysis/skills/dcf-model)
15. [investment-banking datapack-builder](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/investment-banking/skills/datapack-builder/SKILL.md)
16. [investment-banking strip-profile](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/investment-banking/skills/strip-profile/SKILL.md)
17. [LSEG equity-research skill](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/lseg/skills/equity-research/SKILL.md)
18. [LSEG partner-built README](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/lseg/README.md)
19. [S&P Global partner-built README](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/spglobal/README.md)
20. [S&P Global tear-sheet skill](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/spglobal/skills/tear-sheet/SKILL.md)
21. [S&P Global earnings-preview-beta skill](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/spglobal/skills/earnings-preview-beta/SKILL.md)
22. [private-equity unit-economics](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/private-equity/skills/unit-economics/SKILL.md)
23. [private-equity portfolio-monitoring](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/private-equity/skills/portfolio-monitoring/SKILL.md)
24. [private-equity dd-checklist](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/private-equity/skills/dd-checklist/SKILL.md)
25. [private-equity dd-meeting-prep](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/private-equity/skills/dd-meeting-prep/SKILL.md)
26. [private-equity ic-memo](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/private-equity/skills/ic-memo/SKILL.md)
27. [investment-banking cim-builder](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/investment-banking/skills/cim-builder/SKILL.md)
28. [investment-banking buyer-list](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/investment-banking/skills/buyer-list/SKILL.md)
29. [earnings-reviewer agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/earnings-reviewer/agents/earnings-reviewer.md)
30. [model-builder agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/model-builder/agents/model-builder.md)
31. [valuation-reviewer agent](https://github.com/anthropics/financial-services/blob/main/plugins/agent-plugins/valuation-reviewer/agents/valuation-reviewer.md)
