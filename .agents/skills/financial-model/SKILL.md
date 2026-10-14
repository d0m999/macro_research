---
name: financial-model
description: "在用户模板中完成或新建三表联动财务模型，并用新财报、公司 guidance、宏观数据或修订假设刷新模型、估计与估值变动桥。用于三表模型、3-statement model、model update、plug earnings、刷新预测、更新估值或变动桥请求。"
---

# Financial Model

三表模型的建立与刷新是同一个工件的两个生命周期。新建时建历史、驱动、勾稽和情景；刷新时 plug actuals、修订 forward、出 old-to-new 桥和估值影响。两者共用同一套输入规则和模型不变量；完整任务连续执行，内部校验后进入下一段，不要求用户逐表重复授权。

## 必读契约

- 来源合规与数据源路由遵循 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)（含路由登记表 [`../../data-sources.jsonl`](../../data-sources.jsonl)，无匹配时 fail-closed）。
- 创建或修改 Office 产物前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)；验证器状态与限制按其口径披露。
- 只有需要 SEC 取数时读取 [`references/sec-filings.md`](references/sec-filings.md)。
- 需要补建公式和 schedule 时读取 [`references/formulas.md`](references/formulas.md)。
- 用户没有模板样式或要求统一格式时读取 [`references/formatting.md`](references/formatting.md)。
- 刷新已有模型时读取 [`references/update-playbook.md`](references/update-playbook.md)。

## 模式判别

- **新建**：没有可用模型，或用户给了模板要填满。产出完整三表、schedules 和审计轨迹。
- **刷新**：已有模型，用户给了新财报、guidance、宏观数据或要求修订假设。产出更新后的副本、estimate change 桥和 valuation impact。
- 刷新时模型不存在，先按新建模式补齐历史与结构再进入刷新；不把缺失历史当零值填入。

## 输入与来源

确认模板、币种、单位、历史期间、预测期间和会计口径。历史事实来自已打开的 filing/发行人材料或标为 `USER_PROVIDED` 的文件；预测只使用已注明日期的公司 guidance、用户输入，或明确标为 `MODEL_DERIVED` 的情景。缺失事实写入审计轨迹为 `SOURCE_UNAVAILABLE`，不伪造硬编码。

金融假设不得采用无来源“行业常见值”。每个增长率、利润率、税率、营运资本、CapEx、融资或退出假设必须对应公司历史、可引用公开同业数据、用户输入，或 `MODEL_DERIVED` 情景及推导说明。

## 模型不变量

- 历史事实和假设可以硬编码，但必须有来源/状态；所有派生、链接、subtotal、滚动和敏感性单元格使用可追踪公式。
- `Assets = Liabilities + Equity`；现金流期末现金等于资产负债表现金；retained earnings、PP&E、debt 和 share count roll-forward 前后相接。
- 任何手工 plug 必须显式命名、说明原因，并进入 checks；不得用隐藏硬编码消除不平衡。
- 公式错误、单位混用、期间错位或 source gap 不得被格式化掩盖。
- 逐项勾稽核对表以 [`../audit-xls/SKILL.md`](../audit-xls/SKILL.md) 的 Step 3（模型完整性检查）为正本，新建与刷新交付前都按该表执行；本节不变量是该表的构建期表述。

## 工作流

### 新建模式

1. **复制并映射模板**：保留原文件；识别 tabs、命名区域、实际/预测列、单位、现有公式和保护区域。记录映射及计划修改范围。
2. **填充历史数据**：逐项记录 source record、期间、单位和符号；调节 filing 口径与模板口径，不覆盖无法可靠映射的项目。
3. **建立驱动与利润表**：把假设集中在输入区；投影、subtotal 和 margin 使用公式引用，不粘贴预计算结果。
4. **建立 schedules 与资产负债表**：按模板需要完成营运资本、PP&E/D&A、债务、税项和权益滚动；保持期初、变动、期末可追踪。
5. **建立现金流量表与循环处理**：连接净利润、非现金项目、营运资本、投资和融资现金流。若存在利息/现金循环，使用模板现有机制；新机制必须有 circuit breaker 和明确说明。
6. **校验并交付副本**：按模型不变量一节指向的 audit-xls Step 3 检查表逐项核对，并检查来源完整性。运行统一 artifact 验证器并披露其限制。

### 刷新模式

读取 [`references/update-playbook.md`](references/update-playbook.md) 并按其六步执行：识别触发因素 → plug actuals（含 segment 与资产负债/现金流项）→ 修订 forward 估计（逐项给理由）→ 重算估值影响 → 汇总与行动 → 交付副本。刷新不改变原模型的方法、倍数、share count 和估值日；改变方法属于另一次估值，不属于本模式。

## 完成条件

- 用户原文件保留，交付路径清晰；模板结构和既有公式未被无关改写。
- 所有修改单元格可追踪到事实、假设或公式；每个金融经验参数有来源、用户输入或 `MODEL_DERIVED` 标记。
- 三表及相关 schedules 的勾稽结果已记录；不平衡由显式 plug 说明，不用隐藏硬编码消除；未能验证的项目明确列出。
- 刷新时 plug 的 actuals、估计修订和估值影响都对应已打开的 filing/guidance 或 `USER_PROVIDED` 输入；无基线的比较项标 `SOURCE_UNAVAILABLE`，旧估计保持原值或省略。
- old-to-new 桥每一项有理由；估值重算的方法、倍数、share count 与估值日一致；非经常项目单独标注，GAAP/adjusted 口径不混用。
- 交付 estimate change summary（刷新）或审计轨迹（新建）；缺失输入未被猜测填充。
- 统一验证器返回 `pass` 或 `pass_with_limitations`；本地回退披露 `FORMULA_EVALUATION_UNVERIFIED`。
