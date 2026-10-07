# Public Source Policy

本文件是包内数据来源合规裁决的单一事实来源。所有研究、建模、估值和尽调 skill 都必须遵守它；具体 skill 只补充任务步骤，不得重新引入另一套来源优先级。

> 机器可读的数据源路由登记表：[`.agents/data-sources.jsonl`](data-sources.jsonl)（固定字段，一行一条）。**本表是本项目 skill 数据源路由的单一事实来源（2026-10-04 起）：所有 skill 确定与引用具体数据来源时必须先从本表路由（按 `data_types` × `markets` 过滤，经 `policy_status`/`auth`/`cost` 校验；无匹配时 fail-closed）。** `policy_status` 语义以本文件为准，登记表不改变本文件的裁决。

## 数据源核验补充

- [13FInsight 上游、字段与限制（2026-10-07）](../docs/data-sources/13finsight-2026-10-07.md)：已确认 SEC 上游并入登记表既有 `sec-edgar`，保持 free-only 收录规则；13FInsight 分层订阅产品本身仅作核验说明，不新增可路由来源。

## 来源状态

| 状态 | 含义 | 可否作为公共数据源 |
|---|---|---|
| `PUBLIC_NO_AUTH` | 当前不要求购买、登录、API key 或数据 entitlement，且可以直接打开官方页面或公开接口 | 可以 |
| `PUBLIC_PAGE_VALIDATE` | 页面原则上公开，但可见性、地区、限速或页面结构会变化；本次任务必须实际打开并记录 URL | 条件可以 |
| `USER_PROVIDED` | 用户上传或本地提供的文件、模型、导出数据或访谈材料 | 不是公共来源，只能单独标注 |
| `MODEL_DERIVED` | 由已引用事实、公式或明确假设计算得到 | 不是外部来源，必须标为计算/假设 |
| `SOURCE_UNAVAILABLE` | 没有满足公开可核验条件的来源，或当前页面访问失败 | 不得填入猜测值 |

`PUBLIC_NO_AUTH` 仍须遵守来源网站的使用政策、速率限制和引用要求。公开不等于稳定、不等于一手，也不等于允许批量抓取。

## 允许的来源与用途

### 公司历史财务和披露

- 美国上市公司：SEC EDGAR 的 10-K、10-Q、8-K、DEF 14A、Form 3/4/5、13D/13G、13F、S-4、注册文件，以及 `data.sec.gov/submissions/` 和 `data.sec.gov/api/xbrl/companyfacts/`。
- 公司官网/Investor Relations：正式 earnings release、投资者演示、公开电话会材料、公开 webcast/transcript、产品和管理层页面。
- 非美国公司：对应国家的官方披露监管机构和发行人官网；如果无法确认官方披露入口，标记 `SOURCE_UNAVAILABLE`。

SEC XBRL 不是一个“标签名等于会计科目”的接口。抽取时必须校验 taxonomy tag、单位、期间、`form`、`filed`、`accn`、重复披露和重述；找不到可靠映射时保留缺失状态。

### 市场价格、股本和估值输入

- 股份数、债务、现金、租赁负债和其他资产负债项目：优先使用最新官方 filing 及其附注。
- 股价时间序列：优先使用已实际打开的官方交易所/发行人公开页面；也可以使用本次实测可访问的公开历史数据页面，或用户提供的 TradingView/交易所导出文件，并记录其非一手属性。
- 市值、Enterprise Value、倍数、Beta 和目标价：尽量由已引用的价格、股份数和 filing 事实计算，标为 `MODEL_DERIVED`；价格序列或关键输入缺失时标记 `SOURCE_UNAVAILABLE`。
- 不保证公开页面提供实时价格、历史估值倍数或完整 corporate actions。没有输入就不生成这些图表或倍数。

### 预测、共识和财报事件

- Actuals：公司 earnings release、10-Q/10-K、8-K 及官方补充材料。
- Guidance：当前及前一季度公司正式 guidance，逐项记录发布日期和期间。
- Forward estimates：只能使用公司公开 guidance、用户提供的估计，或本包生成并明确标为 `MODEL_DERIVED` 的 Bull/Base/Bear 情景。
- Analyst consensus、whisper number、机构调查和付费研究：在严格 public-only 模式下没有默认来源；缺失时输出 `SOURCE_UNAVAILABLE`。
- 财报日期、投资者日、产品发布和监管事件：优先使用公司 IR、监管机构或政府官方日历；网页只在本次实际验证后使用。

### 宏观、行业和上下游

- 宏观指标：政府、央行、监管机构和官方统计站点，例如 Treasury、Federal Reserve、BLS、BEA、EIA、CFTC、FDIC 等。
- 行业规模、产量、贸易流、价格和监管：优先使用官方统计、监管文件、交易所公开资料、行业协会公开资料和上市公司 filings。
- 商业新闻和第三方 transcript：只作为已实际打开且可合法引用的补充；如果页面需要登录、订阅、地区权限或无法稳定取得，标记 `SOURCE_UNAVAILABLE`。
- 付费行业报告、机构数据库、企业 CRM/数据室和私有关系数据不进入公共来源集合。

## 任务执行协议

1. 先列出任务需要的指标和期间，再为每个指标指定来源类型。
2. 用搜索只发现候选页面；打开最终页面或 filing，记录实际 URL、标题、发布日期和访问日期。
3. 每个输入保存一个 source record，至少包含：

   ```yaml
   source_id: SEC-2025-10K-0000320193-25-000079
   source_type: SEC_FILING
   publisher: U.S. Securities and Exchange Commission
   url: https://www.sec.gov/Archives/edgar/data/...
   document_title: Form 10-K
   published_at: 2025-10-31
   accessed_at: YYYY-MM-DD
   period_end: YYYY-MM-DD
   status: PUBLIC_NO_AUTH
   fact_or_assumption: fact
   citation_locator: filing page, table, item, or XBRL tag
   notes: units, taxonomy mapping, restatement or limitations
   ```

4. 在模型和报告中区分 `fact`、`MODEL_DERIVED`、`USER_PROVIDED` 和 `SOURCE_UNAVAILABLE`；不把计算结果写成外部来源事实。
5. 发现付费、登录、授权、私有、无法访问或不确定的来源时，立即替换为允许的官方公开路径；没有替代路径就停止该指标并输出 `SOURCE_UNAVAILABLE`。

## SEC 与公开接口操作要求

- 给 SEC 请求设置包含项目标识和联系信息的 `User-Agent`；这不是 API key，但必须遵守 SEC 的 fair-access 规则。
- 控制请求速率，优先下载单个公司所需文件；不做无界面全站爬取。
- `data.sec.gov` 返回成功只证明接口响应，不证明会计映射正确；必须做期间、单位、表单和 accession 校验。
- 若当前环境对官方页面返回 403、429 或其他访问错误，记录实际错误并降低来源状态；不要通过绕过访问控制来“修复”数据。

## 失败关闭

以下情形必须使用 `SOURCE_UNAVAILABLE` 或 `USER_PROVIDED`，不允许猜测：

- forward consensus、whisper number、历史估值倍数或 Beta 没有可公开核验的输入；
- 私营公司经营数据、融资历史、客户集中度或管理层履历没有公司/监管公开材料；
- 公开 transcript、新闻或行业报告需要登录、订阅、机构权限，或无法确认当前文本；
- SEC XBRL 多个 tag/期间/单位冲突且无法通过 filing 原文解决；
- 当前价格、期权隐含波动或市场份额缺少可引用的公开观察值。
