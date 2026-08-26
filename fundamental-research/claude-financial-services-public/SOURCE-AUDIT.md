# Skill Source Audit

审计对象：Anthropic `financial-services` 上游 `69cbc81467a5dced793eee03dec4658aa24ef856`。

导入策略：保留四个与 fundamental research、估值、建模和交易尽调直接相关的 vertical source，共 41 个 `SKILL.md`；不导入 Claude marketplace、远程 MCP 配置、partner-built 插件或 agent bundled 副本。每一行都对应一个已导入的 skill，`source treatment` 是该 skill 在 public-only 模式下可使用的输入边界。

## 分类

- `PUBLIC_RESEARCH`：主动数据来自 SEC/官方发行人/政府监管公开资料或实际验证的公开市场页面。
- `USER_MATERIAL_PROCESSING`：skill 主要处理用户提供的模型、文档或交易材料；这些输入不是公共来源。
- `MODEL_ONLY`：主要是计算、格式化、质量检查或输出编排，不主动寻找金融数据。
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
| `clean-data-xls` | financial-analysis | `USER_MATERIAL_PROCESSING` | 只清理用户提供的表格；清理不改变来源状态 |
| `competitive-analysis` | financial-analysis | `PUBLIC_RESEARCH` | 公司 filings、官网、政府/监管/协会资料和可核验公开市场页面 |
| `comps-analysis` | financial-analysis | `PUBLIC_RESEARCH` | actual comps 用 filings + 公开价格计算；forward comps 没有公开输入则省略/标缺失 |
| `dcf-model` | financial-analysis | `PUBLIC_RESEARCH` | 历史输入用 filings；Treasury/官方宏观页面用于利率；beta/价格缺失则停止对应输出 |
| `deck-refresh` | financial-analysis | `USER_MATERIAL_PROCESSING` | 只刷新用户提供 deck 中已有且可追溯的数字 |
| `ib-check-deck` | financial-analysis | `USER_MATERIAL_PROCESSING` | 只检查用户提供的 presentation 和其内部引用 |
| `lbo-model` | financial-analysis | `MIXED_FAIL_CLOSED` | 模型输入来自用户材料或公开 filings；债务条款/交易假设无公开依据就标 `USER_PROVIDED` |
| `ppt-template-creator` | financial-analysis | `USER_MATERIAL_PROCESSING` | 只处理用户提供的 PowerPoint template |
| `pptx-author` | financial-analysis | `MODEL_ONLY` | 只负责 Codex 文件产出，不声明数据连接器 |
| `skill-creator` | financial-analysis | `MODEL_ONLY` | 只负责 skill 文档编写，不提供金融数据 |
| `xlsx-author` | financial-analysis | `MODEL_ONLY` | 只负责 Codex 文件产出，不声明数据连接器 |
| `buyer-list` | investment-banking | `MIXED_FAIL_CLOSED` | 公司官网、SEC/监管 filings 和公开并购公告；私有 sponsor 数据不进入默认来源 |
| `cim-builder` | investment-banking | `USER_MATERIAL_PROCESSING` | CIM 和管理层材料只能作为 `USER_PROVIDED` 输入 |
| `datapack-builder` | investment-banking | `MIXED_FAIL_CLOSED` | public company 用 filings/官方页面；CIM、预算和内部包只能标 `USER_PROVIDED` |
| `deal-tracker` | investment-banking | `USER_MATERIAL_PROCESSING` | 只处理用户提供的交易状态，不连接私有 CRM |
| `merger-model` | investment-banking | `MIXED_FAIL_CLOSED` | 公开交易事实用 SEC/公司公告/监管文件；未公开条款必须由用户提供 |
| `pitch-deck` | investment-banking | `USER_MATERIAL_PROCESSING` | 只处理用户提供的模板和数据 |
| `process-letter` | investment-banking | `USER_MATERIAL_PROCESSING` | 只根据用户提供的流程事实起草 |
| `strip-profile` | investment-banking | `PUBLIC_RESEARCH` | filings、发行人官网/IR、官方公告；市场价和 forward data 缺失则不补齐 |
| `teaser` | investment-banking | `USER_MATERIAL_PROCESSING` | 只重组用户批准的交易材料，不生成未来源支持的数字 |
| `ai-readiness` | private-equity | `MIXED_FAIL_CLOSED` | 公开公司可用公开 filings；portfolio package/data room 必须标 `USER_PROVIDED` |
| `dd-checklist` | private-equity | `MIXED_FAIL_CLOSED` | 公开事实用官方来源；商业、合同、客户和供应链内部事实只来自用户材料 |
| `dd-meeting-prep` | private-equity | `USER_MATERIAL_PROCESSING` | 会议问题基于用户提供的 context，不声称拥有专家网络或数据室 |
| `deal-screening` | private-equity | `MIXED_FAIL_CLOSED` | public target 用公开材料；CIM/teaser 只作 `USER_PROVIDED` |
| `deal-sourcing` | private-equity | `PUBLIC_RESEARCH` | 只发现有官方公开页面的公司；不访问 CRM、Gmail、Slack 或私有数据库 |
| `ic-memo` | private-equity | `MIXED_FAIL_CLOSED` | memo 事实必须回链公开来源或标 `USER_PROVIDED`，不凭空补全回报数据 |
| `portfolio-monitoring` | private-equity | `USER_MATERIAL_PROCESSING` | 只处理用户提供的 portfolio package；没有材料则 `SOURCE_UNAVAILABLE` |
| `returns-analysis` | private-equity | `MODEL_ONLY` | 只计算用户/公开来源提供的输入，结果标 `MODEL_DERIVED` |
| `unit-economics` | private-equity | `MIXED_FAIL_CLOSED` | 经营指标来自公开 filing 或用户材料；缺失不使用行业数据库补齐 |
| `value-creation-plan` | private-equity | `USER_MATERIAL_PROCESSING` | 只使用用户提供的运营基线和明确假设 |

## 移除的上游来源类别

以下类别不被 active skill instructions、Codex manifest 或包内连接器作为默认数据入口或连接：机构金融数据商、研究终端、私有企业文档连接器、partner-built entitlement 插件、默认 analyst consensus/whisper、登录或订阅限制的第三方 transcript/新闻/行业数据库，以及私有 CRM、邮件、聊天和 data room。

具体上游 provider 名称、endpoint 和 partner 权限证据保留在仓库根目录的[上游刷新审计](../anthropic-financial-services-upstream-refresh-20260826.md)中，不复制到可调用 skill 文档中。

## 审计完成条件

- 41/41 个 source `SKILL.md` 已导入并在上表分类。
- active skill 文本不再把付费/授权 provider 作为数据入口或优先级。
- 所有数据敏感 skill 指向 [`PUBLIC-SOURCE-POLICY.md`](PUBLIC-SOURCE-POLICY.md)。
- 包不包含 `.mcp.json`，不声明远程金融数据连接器。

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

## 包结构校验（2026-08-26）

- Codex plugin validator：通过。
- `.codex-plugin/plugin.json` JSON：通过。
- 41/41 个 `SKILL.md` frontmatter：通过 `quick_validate.py`。
- 选定上游 skill inventory：与包内目录精确匹配，41/41。
- bundled Python scripts：语法编译检查通过。
- 相对 Markdown links：全部解析到包内实际文件。
- 付费 provider、endpoint 和 `mcp__` 反向扫描：0 命中；`.mcp.json`：0 个。
- 包及本次刷新审计的 trailing whitespace：无。
