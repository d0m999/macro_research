---
name: initiating-coverage
description: "顺序完成上市公司首次覆盖：公司研究、财务模型、估值、图表和正式报告。用于 initiating coverage、首次覆盖、深度个股研究或完整研究报告请求。"
---

# Initiating Coverage

生成首次覆盖研究包。用户要求完整报告时，按依赖顺序连续执行全部五项任务；每项通过内部完成条件后进入下一项，不要求逐项再次授权。只有缺少会改变研究对象、估值或交付格式的必需输入时暂停。

## 全程契约

- Task 1 前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)，此后全程沿用同一 source manifest。
- 具体数据源路由以 [`../../data-sources.jsonl`](../../data-sources.jsonl) 为准（本项目 skill 数据源路由的单一事实来源）：按 `data_types` × `markets` 过滤，经 `policy_status`/`auth`/`cost` 校验；无匹配时 fail-closed。
- 创建或修改 `.xlsx`/`.docx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 用户只要求其中一项时，仅执行该项及其真正必需的前置工作，不扩大为完整报告。
- 金融假设、估值区间和权重必须来自公司历史、公开同业数据、用户输入，或带推导的 `MODEL_DERIVED` 情景。

## 五项任务

### Task 1：公司与行业研究

读取 [`references/task1-company-research.md`](references/task1-company-research.md)。定义公司、ticker、估值日期、受众和研究问题；建立 source manifest；完成商业模式、行业、竞争、管理层、风险、催化剂和历史财务事实底稿。

完成条件：关键事实对应已打开来源；不可获得的私营、共识、transcript 或市场事实保持 `SOURCE_UNAVAILABLE`；研究问题与模型驱动已对齐。

### Task 2：财务模型

读取 [`references/task2-financial-modeling.md`](references/task2-financial-modeling.md)。建立历史数据、经营驱动、三表/FCF、情景和审计轨迹。派生值使用公式；预测来自 guidance、用户输入或 `MODEL_DERIVED`。

完成条件：期间、单位、会计口径和公式勾稽清晰；资产负债、现金及关键 roll-forward 已检查；缺失输入未被猜测填充。

### Task 3：估值

读取 [`references/task3-valuation.md`](references/task3-valuation.md)。根据可用输入选择 DCF、trading comps 或其他适用方法；方法权重表达分析判断，不使用固定默认。估值时点、market inputs、EV bridge 和 sensitivity 均可追踪。

完成条件：估值方法输入有来源/状态；数学硬错误为零；每个区间和权重有本案理由。

### Task 4：图表

读取 [`references/task4-chart-generation.md`](references/task4-chart-generation.md)。只制作支持论点且数据完整的图表；每张图带来源、期间、单位和必要限制。不以图表数量作为完成标准。

完成条件：图表与底稿数值一致，不存在误导轴、错期或无法追溯的数据系列。

### Task 5：报告组装

读取 [`references/task5-report-assembly.md`](references/task5-report-assembly.md)。按用户受众组织 thesis、估值、催化剂、风险、财务和来源；区分事实、管理层陈述与分析推断。版式服从用户模板或明确可覆盖的排版默认。

完成条件：报告与模型/图表关键数字一致；所有引用可点击或可定位；artifact 验证状态和限制已披露。

## 最终交付

- 列出所有产物路径及 Task 1–5 的完成状态。
- 汇总 `SOURCE_UNAVAILABLE`、`USER_PROVIDED` 和关键 `MODEL_DERIVED` 项。
- 报告结构/公式/渲染验证结果；本地回退保留 `FORMULA_EVALUATION_UNVERIFIED` 或 `FULL_RENDER_UNVERIFIED`。
