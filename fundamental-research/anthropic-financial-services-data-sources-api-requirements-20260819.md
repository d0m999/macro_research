# Anthropic Claude for Financial Services：数据源与 API 依赖核查

> 核查日期：2026-08-19
>
> 核查对象：`anthropics/financial-services` 的 `main`，本地复核时的 commit 为 `38652224c10610fa52eee2acee3ac712dcff01f2`。
>
> 旧地址 `anthropics/financial-services-plugins` 已不作为当前仓库地址使用；本报告只把当前仓库内容作为实现依据。

## 结论

这套金融插件不是一个自带行情、财报或估值数据库的程序包。核心内容是 Markdown skills、commands、agent 配置和 MCP 连接器配置。金融数据主要通过第三方远程 MCP 服务进入 Claude 的上下文；如果没有这些连接器，skills 仍可以处理用户上传/提供的数据，并按 skill 指令使用 Web/SEC EDGAR 等公开来源，但不会因此获得机构级实时数据。

“调用 skill 是否需要 API”要拆成三层：

| 层级 | 是否需要 API | 说明 |
|---|---|---|
| 只加载/调用 Markdown skill | 不一定 | 只要运行环境支持 Claude/自定义 instructions，并有用户提供的文件或数据即可；skill 本身不是数据 API。 |
| 调用第三方金融数据 MCP | 通常需要 | Anthropic 明确提示可能需要相应供应商的 subscription、API key、OAuth/登录凭证或数据 entitlement。 |
| Claude Managed Agents headless 部署 | 需要 Anthropic API | 仓库的部署示例要求 `ANTHROPIC_API_KEY`，并通过 `/v1/agents` 部署；同时还要为实际使用的 MCP 配置供应商访问。 |

因此，最短答案是：**运行 skill 不等于必须自己申请一个 Anthropic API key；但要让它自动拉取实时/结构化金融数据，通常需要第三方数据商权限。若采用 Managed Agents API 部署，则还需要 Anthropic API key。**

## 1. 当前核心插件声明的 MCP 数据源

`plugins/vertical-plugins/financial-analysis/.mcp.json` 声明的是远程 HTTP MCP endpoint，而不是数据文件或本地 SDK：

| Provider | MCP endpoint | 典型数据/用途（以官方仓库与 partner plugin 描述为准） |
|---|---|---|
| Daloopa | `https://mcp.daloopa.com/server/mcp` | 结构化历史财务、模型取数等 |
| Morningstar | `https://mcp.morningstar.com/mcp` | Morningstar 金融数据 |
| S&P Global / Kensho | `https://kfinance.kensho.com/integrations/mcp` | Capital IQ Pro：公司、市场、估值、共识、交易和 earnings 等 |
| FactSet | `https://mcp.factset.com/mcp` | 市场数据、基本面、盈利预期、研究信息 |
| Moody's | `https://api.moodys.com/genai-ready-data/m1/mcp` | Moody's 数据服务 |
| MT Newswires | `https://vast-mcp.blueskyapi.com/mtnewswires` | 金融新闻 |
| Aiera | `https://mcp-pub.aiera.com` | 会议/earnings 等研究信息 |
| LSEG | `https://api.analytics.lseg.com/lfa/mcp` | 市场数据、曲线、估值和分析；partner plugin 进一步列出债券、FX、期权、宏观、IBES、公司基本面和历史价格等工具 |
| PitchBook | `https://premium.mcp.pitchbook.com/mcp` | 私募/交易/公司研究数据 |
| Chronograph | `https://ai.chronograph.pe/mcp` | 私募股权/组合相关数据 |
| Egnyte | `https://mcp-server.egnyte.com/mcp` | 企业文档/内部资料 |
| Box | `https://mcp.box.com` | 企业文档/内部资料 |

官方 README 当前列出上述 12 个 provider endpoint，但同一段仍把核心插件描述为 “All 11 data connectors”；这属于仓库文本计数不一致，不应据此把 11 当作精确的当前 endpoint 数量。官方 2026-02-24 博客还单独提到 FactSet 与 MSCI connector；但本次核查的当前开源仓库 `.mcp.json` 没有 MSCI 条目。MSCI 可能属于 Claude connector directory/企业配置，而不是当前这个文件内置的 endpoint，不能把它直接当作本仓库已配置数据源。

## 2. 非 MCP 的数据路径

### DCF

`dcf-model/SKILL.md` 的数据优先级是：

1. 已配置的 MCP server：结构化金融数据；
2. 用户提供的数据：历史财务、共识估计等；
3. Web Search/Fetch：需要时取得当前价格、beta、债务和现金。

这意味着 DCF skill 不保证每次都调用同一个供应商；它会根据当前会话是否有 MCP、用户是否提供文件以及运行环境是否有 Web 能力选择路径。

### 三表模型与公开披露

三表模型附带的 `references/sec-filings.md` 明确提供 SEC EDGAR 的 10-K/10-Q 手工取数方法，并要求从财务报表和附注提取收入、资产负债表、现金流、债务到期日、分部和地理信息。SEC EDGAR 是 skill 的公开数据 fallback/reference，不是 `.mcp.json` 中列出的一个 Anthropic 自营连接器。

### 用户文件与内部数据

Excel/PowerPoint/Word 工作流可以从用户打开的文档、上传的模型、企业文档连接器或内部 MCP 获取数据。`Egnyte`、`Box` 这类 endpoint 更接近企业文档数据，不等于行情数据。

## 3. 各运行方式的 API 要求

### Claude Cowork

官方安装教程的路径是 Claude Desktop → Cowork → Plugins；插件安装本身不要求用户在 shell 中设置 `ANTHROPIC_API_KEY`。但使用第三方金融 MCP 时，需要在连接器授权流程中完成相应 provider 的登录/授权；官方明确提示可能需要供应商 subscription 或 API key。S&P Global partner plugin 还明确要求 Capital IQ Pro 或 S&P Global LLM-ready API subscription，并在 Cowork 中提示用 S&P Global credentials 认证。

### Claude Code

当前 README 通过 `claude plugin marketplace add` 和 `claude plugin install` 安装 skills/connector bundle，没有把 `ANTHROPIC_API_KEY` 写成普通插件安装前置条件。实际能否调用金融数据，取决于 Claude Code 当前的模型访问方式以及 MCP server 是否被正确加载和授权；不能把“插件可安装”理解为“数据源免费可用”。

### Claude Managed Agents API

这是明确的 API 部署路径：仓库示例要求：

```bash
export ANTHROPIC_API_KEY=sk-ant-...
scripts/deploy-managed-agent.sh gl-reconciler
```

各 managed-agent cookbook 还通过环境变量传入 MCP URL，例如 `CAPIQ_MCP_URL`、`FACTSET_MCP_URL`、`DALOOPA_MCP_URL`。所以此模式至少有两类凭证/配置：

- Anthropic API：部署和运行 Managed Agents；
- 金融数据 provider：访问 Capital IQ/FactSet/Daloopa 等 MCP 的授权、subscription 或 entitlement。

## 4. Partner plugin 的硬性依赖示例

- `plugins/partner-built/spglobal/README.md` 对 tearsheet、行业交易摘要和 earnings preview 都标注 S&P Global LLM-ready API subscription；其使用说明同时接受 Capital IQ Pro 或该 API subscription。
- `plugins/partner-built/lseg/README.md` 要求有效的 LSEG MCP credentials，以及对应产品的 LSEG data entitlements。

这两个 partner plugin 比核心 `financial-analysis` 的通用提示更明确地证明：**skills 文件可以开源，但底层机构数据访问不是随仓库免费附送的。**

## 5. 当前仓库配置问题

本次在 commit `38652224c10610fa52eee2acee3ac712dcff01f2` 的原始文件上运行 `jq empty`，`plugins/vertical-plugins/financial-analysis/.mcp.json` 解析失败：`egnyte` 对象结束后，`"box"` 前缺少逗号。相关原始文件在第 46 行附近可见这一问题。

仓库自带的 `python3 scripts/check.py` 仍报告 `0 issues`，说明该校验脚本当前没有捕获这个 `.mcp.json` JSON 语法错误。因而在实际安装/加载前，应先等待上游修复或在自己的副本中修复并重新运行 JSON 校验；本次没有修改上游仓库，也没有修改 workspace 中的用户文件。

## 6. 对本仓库 TradingView/OI 研究的含义

这套 Anthropic finance skills 可以作为研究编排和 Excel/PPT 产出层，但不能自动替代 TradingView 或交易所原生数据源：

- 其默认金融数据连接器是机构数据商 MCP，不是 TradingView Pine feed；
- `request.security()`、交易所原生 OI、实时行情权限仍需由对应平台/交易所/API 单独提供；
- 如果把价格、OI、基本面、估值输入混在一起，必须在报告和模型中保留每个数字的 provider、as-of 时间、口径和权限来源。

## 7. 能否在 Codex 使用

结论是：**可以复用 skill 内容，但不是把 Anthropic 插件目录直接安装到 Codex。**

### 7.1 skill 层可以迁移

Anthropic 的核心金融 skill 是带有 `SKILL.md`、`name`、`description` 的 Markdown 指令目录，并附带 references/scripts。Codex 官方文档也使用同样的目录化 skill 模型：skill 目录包含 `SKILL.md`，可放入项目 `.agents/skills` 或用户级 skills 目录；Codex 会按描述自动发现或按显式名称调用。

因此，可以选择性复制或 symlink 这些目录，例如：

- `plugins/vertical-plugins/financial-analysis/skills/dcf-model`
- `plugins/vertical-plugins/financial-analysis/skills/3-statement-model`
- `plugins/vertical-plugins/financial-analysis/skills/comps-analysis`
- `plugins/vertical-plugins/equity-research/skills/...`

但当前 Codex 会话不会因为你拥有 Anthropic GitHub 仓库，就自动把 `plugins/vertical-plugins/.../skills` 注册成可调用 skill；需要放到 Codex 支持的 skill 位置，或做一个 Codex plugin adapter。

### 7.2 plugin/MCP 层需要适配

Anthropic 的 `.claude-plugin`/marketplace 包装是 Claude 生态的安装格式，不能直接当作 Codex plugin。Codex plugin 的最小格式是 `.codex-plugin/plugin.json` 加 `skills/` 目录；如果只需要 skill 指令，通常不必重做完整 plugin，直接安装选中的 skill 目录更简单。

数据连接器也不能直接假设可用。Anthropic 仓库的 `financial-analysis/.mcp.json` 是其插件配置格式，而且本次固定 commit 中该文件本身还存在 JSON 语法错误。Codex 的 MCP 配置应写入项目/用户的 Codex 配置，并根据 provider 的协议和认证方式重新配置、登录和授权。即便完成了配置，Daloopa、FactSet、S&P Global、LSEG 等数据仍需要各自的 subscription、API key、credentials 或 entitlement。

## 8. SEC EDGAR 自动取数能力审计

本次对当前仓库做了源代码和脚本级检查，结论如下：

| 能力 | 当前仓库状态 | 证据/说明 |
|---|---|---|
| SEC EDGAR 10-K/10-Q 手工取数指引 | 有 | `3-statement-model/references/sec-filings.md` 指导打开 EDGAR、定位 Item 8/Item 1 和报表附注 |
| 在 DCF/三表流程中把 EDGAR 作为 fallback | 有 | DCF skill 写明必要时手工从 10-K 取数 |
| 自动访问 SEC EDGAR 的 downloader/client | 未发现 | 没有 SEC HTTP 客户端、User-Agent 配置、重试/限速处理或 EDGAR API 封装 |
| XBRL `companyfacts` / `submissions` 自动解析 | 未发现 | 没有对应 endpoint、字段映射器或 XBRL parser |
| 自动把 SEC 数据填入三表/DCF | 未发现 | 现有 `validate_dcf.py` 是 Excel 结构、公式和逻辑校验器，不是 SEC 数据抓取器 |
| 通过第三方机构 MCP 自动拿结构化财务数据 | 条件性存在 | 只有在 MCP server 已配置且完成 provider 授权时成立；这不是 SEC EDGAR 专用取数 |

所以，对第二个问题的准确回答是：**库里有模拟人工查 SEC EDGAR 的工作流说明，没有“自动获取 SEC 财报并解析/填模”的现成 skill。** `earnings-analysis`、`initiating-coverage`、`comps-analysis` 等 skill 会要求模型搜索或打开最新公告、10-Q/10-K、业绩稿和电话会材料，但它们是研究流程指令，不是后台 SEC 抓取程序。

如果要在 Codex 中实现“模拟人工从 SEC EDGAR 取数”，需要另加一个独立的 SEC data skill/tool，至少处理：CIK/ticker 映射、SEC `User-Agent`、请求限速与重试、10-K/10-Q accession 定位、HTML/XBRL 选择、会计科目映射、单位/期间/重述处理、来源链接和 as-of 证据，然后再把规范化数据交给三表/DCF skill。不能仅靠复制现有 `SKILL.md` 就得到这条自动化链路。

## 官方来源

1. [Anthropic 官方财务插件公告](https://claude.com/blog/cowork-plugins-finance)
2. [Anthropic 官方 Cowork 安装教程](https://claude.com/resources/tutorials/install-financial-services-plugins-for-cowork)
3. [当前仓库 README（固定 commit）](https://github.com/anthropics/financial-services/blob/38652224c10610fa52eee2acee3ac712dcff01f2/README.md)
4. [当前核心 `.mcp.json`（固定 commit）](https://github.com/anthropics/financial-services/blob/38652224c10610fa52eee2acee3ac712dcff01f2/plugins/vertical-plugins/financial-analysis/.mcp.json)
5. [DCF skill（当前 main）](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/financial-analysis/skills/dcf-model/SKILL.md)
6. [SEC filings reference](https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/financial-analysis/skills/3-statement-model/references/sec-filings.md)
7. [S&P Global partner plugin README](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/spglobal/README.md)
8. [LSEG partner plugin README](https://github.com/anthropics/financial-services/blob/main/plugins/partner-built/lseg/README.md)
9. [OpenAI Codex 官方 skills 文档](https://developers.openai.com/codex/build-skills)
10. [OpenAI Codex 官方 plugins 文档](https://developers.openai.com/codex/build-plugins)
11. [OpenAI Codex 官方 MCP 文档](https://developers.openai.com/codex/extend/mcp)
