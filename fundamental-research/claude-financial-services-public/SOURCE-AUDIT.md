# Skill Source Audit

审计对象：Anthropic `financial-services` 上游 `69cbc81467a5dced793eee03dec4658aa24ef856`。

导入策略：面向二级市场基本面研究，从四个 vertical source 中保留 15 个金融 `SKILL.md`；不导入 Claude marketplace、远程 MCP 配置、partner-built 插件或 agent bundled 副本。每一行都对应一个已导入的金融 skill，`source treatment` 是该 skill 在 public-only 模式下可使用的输入边界。

Active skills 直接维护在仓库根目录 [`.agents/skills/`](../../.agents/skills/)，仅由当前项目发现，不使用全局安装或软链接。

## 分类

- `PUBLIC_RESEARCH`：主动数据来自 SEC/官方发行人/政府监管公开资料或实际验证的公开市场页面。
- `USER_MATERIAL_PROCESSING`：skill 主要处理用户提供的模型、文档或交易材料；这些输入不是公共来源。
- `MIXED_FAIL_CLOSED`：同时有公开研究和非公开输入；非公开部分必须标为 `USER_PROVIDED`，没有公开替代路径时标记 `SOURCE_UNAVAILABLE`。

## 逐 skill 结果

| Skill | 上游 vertical | 分类 | public-only 处理 |
|---|---|---|---|
| `catalyst-calendar` | equity-research | `PUBLIC_RESEARCH` | 公司 IR、监管/政府日历、公开交易所页面；事件日期必须实测并记录 |
| `earnings-analysis` | equity-research | `PUBLIC_RESEARCH` | earnings release、10-Q/10-K、8-K、公司公开材料；共识和第三方 transcript 缺失则显式缺失 |
| `earnings-preview` | equity-research | `PUBLIC_RESEARCH` | 公司 guidance 和公开历史 actuals；不生成未有来源的 consensus/whisper |
| `idea-generation` | equity-research | `PUBLIC_RESEARCH` | SEC、公司官网、官方监管/统计资料和验证过的公开市场页面；筛选输入缺失则停止 |
| `initiating-coverage` | equity-research | `MIXED_FAIL_CLOSED` | 公司/行业事实使用公开来源；管理层、历史价格、交易案例和 forward 数据分别核验或标缺失 |
| `model-update` | equity-research | `PUBLIC_RESEARCH` | 新财报、正式 guidance、官方宏观数据；内部预测标 `MODEL_DERIVED` |
| `morning-note` | equity-research | `PUBLIC_RESEARCH` | 公司 IR、监管/政府公告和实测公开市场页面；不依赖新闻终端 |
| `sector-overview` | equity-research | `PUBLIC_RESEARCH` | 政府统计、监管/交易所资料、公开行业协会和公司 filings；付费行业报告移除 |
| `thesis-tracker` | equity-research | `MIXED_FAIL_CLOSED` | 事实变化引用公开来源；持仓/内部 thesis 只作为用户输入 |
| `3-statement-model` | financial-analysis | `PUBLIC_RESEARCH` | SEC filings/XBRL 和发行人材料；tag 映射失败时不填数字 |
| `audit-xls` | financial-analysis | `USER_MATERIAL_PROCESSING` | 只审计用户提供的 workbook；不主动寻找数据商或远程数据 |
| `competitive-analysis` | financial-analysis | `PUBLIC_RESEARCH` | 公司 filings、官网、政府/监管/协会资料和可核验公开市场页面 |
| `comps-analysis` | financial-analysis | `PUBLIC_RESEARCH` | actual comps 用 filings + 公开价格计算；forward comps 没有公开输入则省略/标缺失 |
| `datapack-builder` | investment-banking | `MIXED_FAIL_CLOSED` | public company 用 filings/官方页面；CIM、预算和内部包只能标 `USER_PROVIDED` |
| `unit-economics` | private-equity | `MIXED_FAIL_CLOSED` | 经营指标来自公开 filing 或用户材料；缺失不使用行业数据库补齐 |

## 原生能力与调用方式

- 上游选择中的通用 `skill-creator`、`xlsx-author`、`pptx-author` 不再维护项目副本。Skill 创建使用当前 Codex 官方 `skill-creator`；Office artifact 按 [Codex 执行契约](../../.agents/CODEX-EXECUTION-POLICY.md)路由到 Spreadsheets、Presentations、Documents，并在能力不可用时受限回退。
- Active inventory 为 15 个上游金融 skill；其中 11 个允许隐式调用，4 个只允许显式调用。

## 移除的上游来源类别

以下类别不被 active skill instructions 或项目内连接器作为默认数据入口或连接：机构金融数据商、研究终端、私有企业文档连接器、partner-built entitlement 插件、默认 analyst consensus/whisper、登录或订阅限制的第三方 transcript/新闻/行业数据库，以及私有 CRM、邮件、聊天和 data room。

具体上游 provider 名称、endpoint 和 partner 权限证据保留在仓库根目录的[上游刷新审计](../anthropic-financial-services-upstream-refresh-20260826.md)中，不复制到可调用 skill 文档中。

## 审计完成条件

- 当前保留的 15/15 个上游金融 `SKILL.md` 已在上表分类。
- active skill 文本不再把付费/授权 provider 作为数据入口或优先级。
- 所有数据敏感 skill 指向 [`.agents/PUBLIC-SOURCE-POLICY.md`](../../.agents/PUBLIC-SOURCE-POLICY.md)。
- 项目级 skill 集合不包含 `.mcp.json`，不声明远程金融数据连接器。

## 代表性公开来源验证（2026-08-26）

以下是本次环境的实际访问结果。`200` 只证明页面或接口响应成功；仍须按 policy 校验期间、单位、来源层级和引用位置。`403`/`429` 不通过绕过访问控制解决，当前任务直接降级为 `SOURCE_UNAVAILABLE`。

| 来源 | 本次检查 | 结论 | 包内用法 |
|---|---|---|---|
| SEC `data.sec.gov` submissions | 带项目标识 `User-Agent` 的 GET，HTTP `200` | `PUBLIC_NO_AUTH` | 可用于公司 filing 索引和 accession 定位 |
| SEC `data.sec.gov` Company Facts | 带项目标识 `User-Agent` 的 GET，HTTP `200` | `PUBLIC_NO_AUTH` | 可用于 XBRL 候选值，但必须回到 filing 原文核验 |
| SEC filing archive | 带项目标识 `User-Agent` 的 GET，HTTP `200` | `PUBLIC_NO_AUTH` | 可作为最终引用的 10-K/10-Q/8-K 原文 |
| U.S. Treasury Daily Rates | 公开页面 GET，HTTP `200` | `PUBLIC_NO_AUTH` | 风险利率等宏观输入 |
| BLS public API | 公开 v1 endpoint GET，HTTP `403` | 本环境本次 `SOURCE_UNAVAILABLE` | 不绕过限制；可在未来实际打开后按 `PUBLIC_PAGE_VALIDATE` 使用 |
| Apple Investor Relations | 公开入口 GET，HTTP `403` | 本环境本次 `SOURCE_UNAVAILABLE` | 不把搜索摘要或其他页面当作 IR 财务披露替代 |
| Stooq daily CSV | 公开日线 CSV GET，HTTP `200` | `PUBLIC_PAGE_VALIDATE` | 仅作已验证的非一手价格时间序列，并标注来源属性 |
| Yahoo chart API | 公开 endpoint GET，HTTP `429` | 不作为本次默认来源 | 当前任务不依赖该 endpoint |

### 代表性 SEC 任务

对 Apple（CIK `0000320193`）读取 2025-09-27 结束的 10-K（accession `0000320193-25-000079`）时，先用 Company Facts 找候选 tag，再回到 filing 验证 `form`、`filed`、`accn`、期间和单位。直接使用泛化的 `Revenues` tag 会误取较旧期间；修正为 `RevenueFromContractWithCustomerExcludingAssessedTax` 后，得到可复核的 2025 财年收入 `416,161,000,000 USD`。这验证了 SEC 路径可用，也验证了包内“不把 XBRL tag 名直接当会计科目”的约束。

## 结构校验

- Codex 项目发现目录：仓库根目录 `.agents/skills/`。
- 独立 plugin manifest：已移除；不进行用户级或系统级安装。
- 15/15 个 active `SKILL.md` frontmatter 通过官方 `quick_validate.py`。
- 来源审计中的 15 个上游金融 skill 与项目级 active inventory 精确匹配。
- 15/15 个 `agents/openai.yaml` 可解析；调用 policy 精确为 11 个 `true`、4 个 `false`。
- 公共 artifact 验证脚本：语法检查通过。
- 相对 Markdown links：全部解析到项目内实际文件。
- 付费 provider、endpoint 和 `mcp__` 反向扫描：0 命中；`.mcp.json`：0 个。
- skills 及本次刷新审计的 trailing whitespace：无。
