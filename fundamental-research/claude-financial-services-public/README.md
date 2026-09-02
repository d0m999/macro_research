# Financial Services Public for Codex

这是从 Anthropic `financial-services` 官方仓库筛选并改写的项目级 Codex skill 集合。它保留研究、估值、建模、交易尽调和材料整理的方法，但把主动数据来源收窄为可以公开核验的来源。

## 上游与范围

- 上游仓库：<https://github.com/anthropics/financial-services>
- 固定上游 commit：`69cbc81467a5dced793eee03dec4658aa24ef856`
- 导入范围：`equity-research`、`financial-analysis`、`investment-banking`、`private-equity` 四个 vertical 的 38 个金融 source `SKILL.md`
- 未导入：上游 Claude marketplace、远程连接器配置、partner-built 插件和 agent bundled 副本
- 原有通用 `skill-creator`、`xlsx-author`、`pptx-author` 已由 Codex 官方 skill/artifact capability 替代，不计入 active financial skills
- 项目另有 1 个本地显式目录路由 `$financial-services`；active skills 合计 39 个
- 许可：Apache License 2.0，见 [`LICENSE`](LICENSE)

逐 skill 的来源分类、替换和保留理由见 [`SOURCE-AUDIT.md`](SOURCE-AUDIT.md)。

## 项目级加载

- 技能源文件和 Codex 发现目录：仓库根目录 [`.agents/skills/`](../../.agents/skills/)
- 公共数据源规则：[`.agents/PUBLIC-SOURCE-POLICY.md`](../../.agents/PUBLIC-SOURCE-POLICY.md)
- Artifact 执行契约：[`.agents/CODEX-EXECUTION-POLICY.md`](../../.agents/CODEX-EXECUTION-POLICY.md)
- 生效范围：仅当前仓库；不安装到用户级或系统级 skills 目录
- 目录组织：技能直接存放，不使用软链接或文件副本

本目录只保留上游版本、许可、改造说明和来源审计，不再作为独立 Codex plugin 包。

## 调用分层

以下 12 个研究与估值入口允许自动发现：`catalyst-calendar`、`earnings-analysis`、`earnings-preview`、`idea-generation`、`initiating-coverage`、`model-update`、`morning-note`、`sector-overview`、`thesis-tracker`、`competitive-analysis`、`comps-analysis`、`dcf-model`。

其余 27 个 skill 只在用户显式输入 `$skill-name` 时调用。记不住具体名称时使用 `$financial-services`；它只推荐一个主 skill 和最多两个后续 skill，不自动执行或创建新的总研究工作流。

每个 active skill 的 `agents/openai.yaml` 只维护 UI 名称、短说明和调用 policy；入口使用条件化 reference 指针做渐进披露。

## Artifact 执行

`.xlsx`、`.pptx`、`.docx` 分别优先路由到 Codex Spreadsheets、Presentations、Documents。只有对应 capability 不可用时，才使用本机 `python3` 与受限 OOXML 库回退，并运行：

```bash
python3 .agents/scripts/validate_financial_artifact.py <file>
```

本地 Excel 回退标记 `FORMULA_EVALUATION_UNVERIFIED`；未完整逐页渲染的 PPTX/DOCX 标记 `FULL_RENDER_UNVERIFIED`。结构成功不能被表述为公式或视觉的无保留通过。

## 可用来源

默认优先使用：

1. SEC EDGAR filings、`data.sec.gov` submissions/XBRL 数据；自动访问必须声明 `User-Agent`、限速并只下载所需内容。
2. 公司官网和 Investor Relations 页面上的 earnings release、10-K/10-Q 链接、investor presentation、公开 webcast/transcript 和其他正式材料。
3. 政府、监管机构和官方交易所公开页面，例如 Treasury、Federal Reserve、BLS、BEA、EIA、FDA、FTC、DOJ、CFTC、FDIC 等；每次使用前验证页面实际可访问性。
4. 每次实测可访问的公开市场历史页面或用户提供的 TradingView/交易所导出文件；它们只能作为价格时间序列输入，不能替代财务披露。

`web search` 只用于发现候选页面；报告中的数字必须链接到实际打开过的 filing、页面或用户明确提供的文件。来源缺失时使用 `SOURCE_UNAVAILABLE`，不使用模型记忆补齐。

## 明确不提供

本项目级 skill 集合不含任何付费数据商、数据 entitlement、机构终端、企业数据室、私有 CRM、私有邮件/聊天、远程金融 MCP 或默认的 analyst consensus/whisper 数据。Forward estimates 只能来自公司公开 guidance、用户提供的估计，或模型明确标注的内部情景假设。

用户上传的 CIM、内部财务包、Excel、PDF 和其他文件可以作为 `USER_PROVIDED` 输入处理，但它们不是公共数据源，也不能在输出中标作公开来源。

## 使用前置规则

处理任何研究或估值任务前，先读取 [`.agents/PUBLIC-SOURCE-POLICY.md`](../../.agents/PUBLIC-SOURCE-POLICY.md)。它定义来源状态、source record、缺失处理和各类指标的替代路径。

这些项目级 skills 是研究指令和文档模板，不是行情数据库、SEC 自动化下载器，也不构成投资、法律、税务或会计建议。
