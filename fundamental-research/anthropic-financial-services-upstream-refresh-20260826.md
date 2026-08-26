# Anthropic Claude Financial Services 官方上游刷新记录

> 刷新日期：2026-08-26（Asia/Singapore）
>
> 研究对象：[anthropics/financial-services](https://github.com/anthropics/financial-services)
>
> 当前上游基线：`main` commit `69cbc81467a5dced793eee03dec4658aa24ef856`
>
> 上游提交时间：`2026-08-24T18:04:28-07:00`
>
> 对比旧审计基线：`38652224c10610fa52eee2acee3ac712dcff01f2`

## 结论

本次已将官方上游刷新到当前 `main`。旧审计基线到新基线只涉及 6 个文件，而且全部属于 `claude-for-msft-365-install`；金融研究 skills、financial-analysis 的 MCP 清单、partner-built 数据插件和相关 agent 编排没有变化。因此，之前关于“不能直接把官方包当作无权限公共数据包使用”的判断仍然有效。

当前上游仍不能整体复制为 public-only Codex 包，原因有三类：

1. `financial-analysis/.mcp.json` 声明 12 个远程金融/文档连接器，其中包含机构数据商和企业文档系统；上游 README 只保证“可能需要 subscription 或 API key”，没有给出无需授权的公共数据契约。
2. LSEG 和 S&P Global partner plugin 的 README 明确要求 credentials、data entitlements 或 subscription；多个 agent 和 skill 还直接把 CapIQ、FactSet、Daloopa、Bloomberg 等作为数据入口。
3. 上游是 Claude 插件格式（`.claude-plugin`），当前没有 `.codex-plugin`；Codex 适配必须另建包结构和数据源边界。

这次刷新先完成了版本和来源审计；随后已在 `fundamental-research/claude-financial-services-public/` 建立 Codex public-only 包。上游的 `.claude-plugin`、远程 MCP 配置、partner-built 插件和 agent bundled 副本没有复制进包内。

## 1. 相对旧基线的变化

| 项目 | 结果 |
|---|---|
| 旧基线 | `38652224c10610fa52eee2acee3ac712dcff01f2`，此前 2026-08-19 审计使用 |
| 新基线 | `69cbc81467a5dced793eee03dec4658aa24ef856` |
| 变化文件数 | 6 |
| 变化范围 | 仅 `claude-for-msft-365-install/` |
| 金融数据源配置变化 | 无 |
| 金融研究/建模 skill 内容变化 | 无 |

新提交的内容是 Microsoft 365 安装工具的文档和校验增强，包括 Azure AI Foundry keyless Entra 路径、`available_models` 和 `web_search` disabled feature。它们不改变本项目要适配的金融研究数据边界。[新旧 commit 对比](https://github.com/anthropics/financial-services/compare/38652224c10610fa52eee2acee3ac712dcff01f2...69cbc81467a5dced793eee03dec4658aa24ef856)

## 2. 当前上游 inventory

对当前 commit 的目录和 manifest 做了只读盘点：

| 类别 | 数量/内容 |
|---|---|
| Marketplace 条目 | 20 |
| Vertical plugins | 7：`equity-research`、`financial-analysis`、`fund-admin`、`investment-banking`、`operations`、`private-equity`、`wealth-management` |
| Agent plugins | 10：`earnings-reviewer`、`gl-reconciler`、`kyc-screener`、`market-researcher`、`meeting-prep-agent`、`model-builder`、`month-end-closer`、`pitch-agent`、`statement-auditor`、`valuation-reviewer` |
| Partner-built plugins | 2：`lseg`、`spglobal` |
| Vertical source skills | 55 |
| Agent bundled skills | 51 |
| `.mcp.json` 文件 | 5，其中 2 个为空 MCP 配置，核心配置声明 12 个 provider，2 个 partner 配置各声明一个 endpoint |
| `financial-analysis/.mcp.json` 核心 endpoint | 12 个 provider 条目 |
| Codex plugin manifest | 未发现 `.codex-plugin` |

上游 README 将 `financial-analysis` 描述为 “All 11 data connectors”，但该 commit 的核心 `.mcp.json` 实际列出 12 个 provider：`daloopa`、`morningstar`、`sp-global`、`factset`、`moodys`、`mtnewswire`、`aiera`、`lseg`、`pitchbook`、`chronograph`、`egnyte`、`box`。适配时以实际配置条目为准，不采用 README 中的 11 这个旧计数。[当前 marketplace](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/.claude-plugin/marketplace.json) · [当前 README](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/README.md)

## 3. public-only 数据源裁决

这里的“保留”指可以纳入 Codex 包的默认来源；“条件保留”不代表数据一定存在，而是每次必须打开真实页面、记录 URL 和 as-of 时间后才能使用。

| 当前路径/来源 | 上游实际状态 | public-only 裁决 |
|---|---|---|
| `financial-analysis/.mcp.json` 中的 12 个远程 provider | 远程 HTTP MCP；README 明确提醒可能需要 provider subscription 或 API key | **整体移除**。在没有逐一证明“无需登录、无需订阅、无需 entitlement”的情况下，默认不进入 Codex 包 |
| `lseg` partner plugin | README 要求有效 LSEG credentials 和相关 product data entitlements | **移除** |
| `spglobal` partner plugin | README 对 tearsheet、交易摘要和 earnings preview 标明 S&P Global LLM-ready API subscription，并要求 S&P credentials | **移除** |
| `Egnyte`、`Box` | 企业文档/私有租户连接器，不是公开金融数据 | **移除** |
| CapIQ、FactSet、Daloopa、Bloomberg、Refinitiv、IBES 等 skill/agent 引用 | 当前文本把它们当作机构数据或共识来源 | **从 active instructions 中洗出**；不能只删除 MCP URL 而保留“优先调用付费源”的文字 |
| SEC EDGAR 10-K/10-Q | 上游提供公开披露的手工定位和抽取指引 | **保留**，作为公开公司财务数据主来源；当前只是 workflow/reference，不是现成 downloader/parser |
| 公司官网、Investor Relations、公开 earnings release、公开 investor presentation | 上游多个研究 workflow 要求打开并核验这些材料 | **条件保留**，以官方页面为源，记录页面 URL、发布日期和访问日期 |
| 公开 transcript、新闻或行业页面 | 可见性和可访问性随页面变化；上游 workflow 也列出 Seeking Alpha、AlphaStreet、Motley Fool 等非统一来源 | **不作为保证可用的默认源**；只有实际无需登录/付费即可取得且可合法引用时才作为补充，否则标记 `SOURCE_UNAVAILABLE` |
| 用户上传文件、内部文档、私有 MCP | 能让原始 skill 工作，但不是公开数据 | **不纳入严格 public-only 核心**；如将来支持，必须作为单独的 user-input 扩展，不得伪装成公共来源 |

因此，当前 public-only 核心的最小来源集合是：

- SEC EDGAR 公开 filings；
- 公司官网和 Investor Relations 公开页面；
- 公开 earnings release、公开 investor presentation 及其他能直接打开的官方材料；
- 经过实际访问验证的政府/监管公开页面。

Web search 只能用于发现候选页面，不能本身充当数据源；每个数字都必须回链到实际页面或 filing。公开来源缺失时必须输出缺失状态，不能用模型记忆、付费源名称或未经验证的共识数字补齐。

## 4. 必须清洗的上游污染点

这次刷新确认，public-only 改造不是简单删除一个 MCP 文件，还需要清洗下列内容：

- `market-researcher` agent 的 `tools` 和工作流直接绑定 `mcp__capiq__*`、`mcp__factset__*`，并要求用 CapIQ/FactSet 做 peer multiples。
- `earnings-reviewer` agent 直接绑定 FactSet/Daloopa，并把它们作为 actuals、consensus、filings 的入口。
- `model-builder`、`pitch-agent` 及其 DCF/comps bundled skills 仍有 CapIQ、Daloopa、S&P Kensho、FactSet、Bloomberg 等优先级或示例。
- `earnings-analysis` workflow 仍要求共识估计，并列出 Bloomberg、FactSet、Refinitiv、Yahoo Finance；transcript 部分列出多个不统一的第三方页面。
- `investment-banking/strip-profile` 和 one-pager 示例仍把 Bloomberg、FactSet、CapIQ 作为 market data/estimates 来源。
- `partner-built/lseg` 与 `partner-built/spglobal` 的 README、commands、skills、connector 文件整体都是权限数据路径，不能作为保留 skill 原样复制。

本次对上游 `plugins/` 文本做 provider 名称扫描，至少 34 个文件命中这些机构数据源或权限路径。下一阶段应对复制后的 Codex 包做反向扫描，确保不会留下 endpoint、MCP tool 名、subscription、entitlement、credentials 或“优先使用付费源”的死路径。

## 5. 当前已可保留的研究能力与缺口

可以保留的是研究方法和输出结构，而不是原始数据承诺：

- `sector-overview`：行业规模、增长、结构、价值链和竞争框架；
- `competitive-analysis`：竞争格局、价值流和利润层级；
- `initiating-coverage`：公司业务、风险、财务和估值的研究框架；
- `earnings-analysis`、`earnings-preview`、`model-update`：财报事件和模型更新流程，前提是把 consensus/transcript 输入改为公开可核验材料；
- `3-statement-model`、`dcf-model`、`comps-analysis`：建模与估值方法，前提是明确数据来源和不可得状态。

当前上游没有以下现成公共数据能力：

- SEC HTTP downloader、`User-Agent`、限速/重试处理；
- SEC `submissions`/XBRL `companyfacts` 的标准化解析和会计科目映射；
- 公司 IR 页面统一抓取器；
- public-only 的共识估计、完整 earnings transcript 或实时/历史行情适配器。

所以，复制 `SKILL.md` 只能得到分析指令，不能得到完整的公开数据自动化链路。

## 6. 校验结果

在临时只读 checkout 中执行：

```text
python3 scripts/check.py
OK — 83 file(s) checked, 0 issues.
```

但独立解析当前核心 MCP 文件失败：

```text
jq: parse error: Expected separator between values at line 47, column 9
```

问题位于 `egnyte` 对象和 `box` 对象之间缺少逗号；该文件末尾在补逗号后仍缺少根对象的最后一个 `}`。因此，官方 `check.py` 的通过不等于所有 `.mcp.json` 都是合法 JSON；Codex 版本不应继承这份文件。

上游仓库标注为 Apache 2.0。若后续复制和修改官方文件，应保留相应 LICENSE/copyright notice，并在 Codex 包中注明改造来源。[官方 LICENSE](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/LICENSE)

## 7. 下一步执行边界

Codex 适配已按以下顺序执行；剩余工作仅为最终校验和后续可选的公开数据自动化：

1. 已冻结 public-only allowlist/denylist；未证明无需权限的远程源默认 deny。
2. 已只复制 `equity-research`、`financial-analysis`、`investment-banking`、`private-equity` 四个相关 vertical 的 41 个 source skills，并逐个清洗付费源、私有源、用户文件和公开网页边界。
3. 已新建 `.codex-plugin/plugin.json`、`skills/`、`PUBLIC-SOURCE-POLICY.md` 和 `SOURCE-AUDIT.md`，没有复制 `.claude-plugin` marketplace 或任何第三方 MCP 配置。
4. 已固化 SEC EDGAR、发行人/IR、政府/监管/交易所和实测公开市场页面的 source record 格式；缺失数据统一输出 `SOURCE_UNAVAILABLE`，用户材料单独标为 `USER_PROVIDED`。
5. 已完成 provider/endpoint 扫描、JSON/frontmatter/链接校验、脚本语法和 `git diff --check`；后续如需补充公开数据自动化，另行评估。

当前项目状态应记为：**上游版本已刷新；public-only allowlist 已固化为 Codex 包；41 个选定 source `SKILL.md` 已导入并完成来源边界改写；代表性 SEC/宏观/市场页面已验证；最终 manifest/frontmatter/链接、脚本和差异检查均已通过。**

## 官方来源

1. [当前 commit：`69cbc81467a5dced793eee03dec4658aa24ef856`](https://github.com/anthropics/financial-services/tree/69cbc81467a5dced793eee03dec4658aa24ef856)
2. [当前 README](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/README.md)
3. [当前 marketplace.json](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/.claude-plugin/marketplace.json)
4. [当前 financial-analysis MCP 配置](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/vertical-plugins/financial-analysis/.mcp.json)
5. [SEC filings reference](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/vertical-plugins/financial-analysis/skills/3-statement-model/references/sec-filings.md)
6. [当前 earnings workflow](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/agent-plugins/earnings-reviewer/skills/earnings-analysis/references/workflow.md)
7. [LSEG partner README](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/partner-built/lseg/README.md)
8. [S&P Global partner README](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/partner-built/spglobal/README.md)
9. [market-researcher agent](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/agent-plugins/market-researcher/agents/market-researcher.md)
10. [model-builder agent](https://github.com/anthropics/financial-services/blob/69cbc81467a5dced793eee03dec4658aa24ef856/plugins/agent-plugins/model-builder/agents/model-builder.md)
