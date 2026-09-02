---
name: financial-services
description: "金融 skill 显式目录路由：按研究、建模、投行、PE 和文件处理选择具体入口；只推荐，不执行子 skill。"
---

# Financial Services Router

这是显式调用的目录路由。它只帮助用户选择具体 skill，不执行被推荐的 skill，也不把多个 skill 自动串成新的上市公司总研究工作流。

## 路由规则

1. 识别用户的主要产物、现有输入、决策对象和工作阶段。
2. 推荐一个最直接完成当前任务的主 skill；只有真实存在的后续依赖时，再列最多两个后续 skill。
3. 简要解释为何选择、哪些近似 skill 未选，以及当前还缺什么关键输入。
4. 给出可直接复制的显式调用示例：`$skill-name <任务和输入>`。
5. 到此停止；提醒用户复制主调用以开始执行。

## Equity research

- `$catalyst-calendar`：公司/覆盖组合事件与催化剂日历。
- `$earnings-analysis`：指定或最新季度的财报复盘。
- `$earnings-preview`：财报前指标、guidance 和情景准备。
- `$idea-generation`：公开来源的系统性选股与主题候选。
- `$initiating-coverage`：公司研究、模型、估值、图表和首次覆盖报告。
- `$model-update`：用新财报/guidance 更新模型与估值。
- `$morning-note`：隔夜信息和覆盖公司晨会笔记。
- `$sector-overview`：行业、价值链、竞争和主题研究。
- `$thesis-tracker`：维护 thesis、证据、催化剂和失效条件。

## Modeling and financial analysis

- `$3-statement-model`：完成三表联动模型。
- `$competitive-analysis`：竞争格局、peer positioning 和市场地图。
- `$comps-analysis`：上市公司可比估值。
- `$dcf-model`：现金流折现估值。
- `$lbo-model`：LBO、债务和 sponsor returns 模型。
- `$audit-xls`：审计 spreadsheet 公式与勾稽。
- `$clean-data-xls`：清洗 spreadsheet 数据并保留原件。
- `$deck-refresh`：刷新既有 presentation 数字。
- `$ib-check-deck`：投资银行 deck 数字、叙事和视觉 QC。
- `$ppt-template-creator`：把用户 PPT 模板蒸馏为可复用 skill。

## Investment banking

- `$buyer-list`：战略/财务买家 universe。
- `$cim-builder`：卖方 CIM。
- `$datapack-builder`：尽调/IC data pack workbook。
- `$deal-tracker`：交易 pipeline、里程碑和行动项。
- `$merger-model`：accretion/dilution 与 merger consequences。
- `$pitch-deck`：填充用户提供的 pitch deck 模板。
- `$process-letter`：IOI/final bid 等流程信。
- `$strip-profile`：公司 strip profile。
- `$teaser`：匿名一页卖方 teaser。

## Private equity

- `$ai-readiness`：组合公司 AI 机会优先级。
- `$dd-checklist`：尽调请求和状态清单。
- `$dd-meeting-prep`：尽调会议背景与问题。
- `$deal-screening`：CIM/teaser 初筛 memo。
- `$deal-sourcing`：公开目标发现和 outreach 草稿。
- `$ic-memo`：投资委员会 memo。
- `$portfolio-monitoring`：组合公司 KPI、预算和 covenant 监控。
- `$returns-analysis`：IRR/MOIC 和敏感性。
- `$unit-economics`：cohort、LTV/CAC、retention 和 revenue quality。
- `$value-creation-plan`：并购后价值创造与 EBITDA bridge。

## File processing shortcuts

- 清洗 workbook：`$clean-data-xls`
- 审计 workbook：`$audit-xls`
- 标准化 data pack：`$datapack-builder`
- 填充 PowerPoint 模板：`$pitch-deck`
- 刷新已有 deck：`$deck-refresh`
- QC 已有 deck：`$ib-check-deck`
- 把 PPT 模板变成 skill：`$ppt-template-creator`

## 返回格式

```text
主 skill：$skill-name
选择理由：<一句话>
后续 skill（可选）：$skill-name、$skill-name
直接调用：$skill-name <保留用户对象、期间、输入文件和产物要求的提示>
```
