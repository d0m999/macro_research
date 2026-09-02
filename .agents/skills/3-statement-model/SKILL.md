---
name: 3-statement-model
description: "完成或填充三表联动财务模型模板，建立利润表、资产负债表和现金流量表的公式、滚动与勾稽。用于 3-statement model 或三表模型任务。"
---

# 3-Statement Model

在用户提供的模板中完成三表模型；没有模板且用户允许自建时，才建立标准结构。完整任务连续执行，内部校验后进入下一段，不要求用户逐表重复授权。

## 必读契约

- 填入事实或假设前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 创建或修改 `.xlsx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 只有需要 SEC 取数时读取 [`references/sec-filings.md`](references/sec-filings.md)。
- 需要补建公式和 schedule 时读取 [`references/formulas.md`](references/formulas.md)。
- 用户没有模板样式或要求统一格式时读取 [`references/formatting.md`](references/formatting.md)。

## 输入与来源

确认模板、币种、单位、历史期间、预测期间和会计口径。历史事实来自已打开的 filing/发行人材料或标为 `USER_PROVIDED` 的文件；预测只使用已注明日期的公司 guidance、用户输入，或明确标为 `MODEL_DERIVED` 的情景。缺失事实写入审计轨迹为 `SOURCE_UNAVAILABLE`，不伪造硬编码。

金融假设不得采用无来源“行业常见值”。每个增长率、利润率、税率、营运资本、CapEx、融资或退出假设必须对应公司历史、可引用公开同业数据、用户输入，或 `MODEL_DERIVED` 情景及推导说明。

## 工作流

1. **复制并映射模板**：保留原文件；识别 tabs、命名区域、实际/预测列、单位、现有公式和保护区域。记录映射及计划修改范围。
2. **填充历史数据**：逐项记录 source record、期间、单位和符号；调节 filing 口径与模板口径，不覆盖无法可靠映射的项目。
3. **建立驱动与利润表**：把假设集中在输入区；投影、subtotal 和 margin 使用公式引用，不粘贴预计算结果。
4. **建立 schedules 与资产负债表**：按模板需要完成营运资本、PP&E/D&A、债务、税项和权益滚动；保持期初、变动、期末可追踪。
5. **建立现金流量表与循环处理**：连接净利润、非现金项目、营运资本、投资和融资现金流。若存在利息/现金循环，使用模板现有机制；新机制必须有 circuit breaker 和明确说明。
6. **校验并交付副本**：检查资产等式、现金 tie-out、retained earnings、债务、税项、符号、期间、错误公式和来源完整性。运行统一 artifact 验证器并披露其限制。

## 模型不变量

- 历史事实和假设可以硬编码，但必须有来源/状态；所有派生、链接、subtotal、滚动和敏感性单元格使用可追踪公式。
- `Assets = Liabilities + Equity`；现金流期末现金等于资产负债表现金；retained earnings、PP&E、debt 和 share count roll-forward 前后相接。
- 任何手工 plug 必须显式命名、说明原因，并进入 checks；不得用隐藏硬编码消除不平衡。
- 公式错误、单位混用、期间错位或 source gap 不得被格式化掩盖。

## 完成条件

- 用户原文件保留，交付路径清晰；模板结构和既有公式未被无关改写。
- 所有修改单元格可追踪到事实、假设或公式；每个金融经验参数有来源/用户输入或 `MODEL_DERIVED` 标记。
- 三表及相关 schedules 的勾稽结果已记录；未能验证的项目明确列出。
- 统一验证器返回 `pass` 或 `pass_with_limitations`；本地回退披露 `FORMULA_EVALUATION_UNVERIFIED`。
