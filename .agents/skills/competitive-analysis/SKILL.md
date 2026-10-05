---
name: competitive-analysis
description: "研究公司竞争格局、同行定位、市场地图与战略差异，并生成可追溯的分析或演示文稿。用于竞争分析、竞品对比、市场定位、competitive landscape 等请求。"
---

# Competitive Analysis

用可核验事实比较竞争者，并把差异转化为投资或战略含义。输出可以是研究 memo、表格或 deck，以用户指定格式为准。

## 必读契约

- 研究前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 具体数据源路由以 [`../../data-sources.jsonl`](../../data-sources.jsonl) 为准（本项目 skill 数据源路由的单一事实来源）：按 `data_types` × `markets` 过滤，经 `policy_status`/`auth`/`cost` 校验；无匹配时 fail-closed。
- 输出 `.pptx`、`.xlsx` 或 `.docx` 时读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 需要市场地图或框架选择时读取 [`references/frameworks.md`](references/frameworks.md)。
- 需要交易表、情景表或 slide schema 时读取 [`references/schemas.md`](references/schemas.md)。

## 工作流

1. **定义问题**：确认目标公司、行业边界、地区、期间、受众、决策问题和输出格式。用户要求完整任务时直接形成合理结构；只有这些选择会实质改变结论且无法推断时才暂停。
2. **建立 peer universe**：从发行人 filings/IR、监管、政府、交易所和可公开核验协会资料识别直接、邻近与潜在竞争者。记录纳入/排除理由。
3. **建立证据矩阵**：按产品、客户、地域、渠道、规模、增长、盈利、技术、监管或其他相关维度收集同口径事实。每个数字带 source record；缺失保持 `SOURCE_UNAVAILABLE`。
4. **分析定位**：区分事实、管理层陈述和分析推断；识别可持续优势、弱点、白空间、替代风险与可能反应。
5. **形成输出**：用少量清晰图表表达一项主要结论；所有矩阵轴、权重或评分说明选择理由。金融阈值和权重来自公开同业数据、用户输入或标为 `MODEL_DERIVED` 的情景。
6. **验证**：核对公司/期间/单位、事实与叙事一致性、图表来源、关键数字跨页一致性及 artifact 限制。

## 完成条件

- peer universe、比较口径和排除规则透明；不存在把不可访问来源或模型记忆写成事实的项目。
- 每个关键结论可以回链到证据矩阵；推断与事实分开标注。
- 产物结构有效，关键数字一致；未完整渲染时披露 `FULL_RENDER_UNVERIFIED`。
