---
name: dcf-model
description: "建立可审计的 DCF 估值模型，包含历史财务、经营预测、WACC、终值、EV-to-equity bridge 与敏感性。用于 DCF、现金流折现、内在价值或目标价请求。"
---

# DCF Model

建立公式驱动、来源清晰且情景可复算的 DCF workbook。完整任务连续完成；阶段之间使用内部勾稽，不要求用户重复确认。

## 必读契约

- 收集数据和假设前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 创建或修改 `.xlsx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 选择 FCFF/FCFE、预测方法或终值方法时读取 [`references/methodology.md`](references/methodology.md)。
- 用户没有模板时读取 [`references/workbook-layout.md`](references/workbook-layout.md)。
- 构建敏感性表时读取 [`references/sensitivity.md`](references/sensitivity.md)。

## 输入与假设规则

历史 actuals、cash、debt、share count 和其他 bridge 项目来自已打开的 filing/IR 或 `USER_PROVIDED` 文件。价格、风险利率和其他市场输入记录估值时点与页面。没有可公开核验的 beta、forward consensus 或市场数据时标 `SOURCE_UNAVAILABLE`，不要凭记忆补齐。

增长、margin、tax、D&A、CapEx、working capital、WACC 组件、terminal growth 和估值权重必须来自：公司历史、明确引用的公开同业数据、用户输入，或有推导说明的 `MODEL_DERIVED` 情景。任何经验区间只可作为标记清晰的情景，不能成为事实或固定合格标准。

## 工作流

1. **定义估值**：确认公司、估值日期、币种、财政年度、FCFF/FCFE、预测期、终值方法和 share class。
2. **建立 source manifest**：收集历史财务、资本结构和市场输入，统一期间、单位和会计口径；记录缺口。
3. **建立驱动和预测**：从收入/经营驱动到 EBIT/NOPAT，再到 D&A、CapEx、NWC 和 FCF。事实和假设硬编码在输入区，派生值用公式。
4. **计算资本成本**：逐项展示 risk-free、beta、ERP、cost of debt、tax 和资本权重的来源或状态。若关键输入缺失，保留未完成状态，不伪造精确 WACC。
5. **终值与 bridge**：保证 Gordon Growth 分母数学有效；分别展示 PV of forecast FCF、PV of terminal value、EV adjustments、equity value、diluted shares 和 per-share value。
6. **情景与敏感性**：轴中心精确对应 base case；每个单元格完整重算。轴范围来自本模型驱动、用户输入或 `MODEL_DERIVED` 情景。
7. **验证与交付**：从仓库根目录运行 `python3 .agents/skills/dcf-model/scripts/validate_dcf.py <file>` 做数学/结构检查，再运行统一 artifact 验证器。报告数据缺口和公式求值限制。

## 模型不变量

- `FCFF = NOPAT + D&A - CapEx - Change in NWC`，除非明确采用另一种一致定义。
- Gordon Growth 仅在 `terminal growth < WACC` 时数学有效；不满足则结构失败。
- EV-to-equity bridge 的每个 adjustment 说明符号和来源；shares 与 equity value 使用同一估值时点/口径。
- 敏感性 base cell 与主模型结果相等；公式错误、空白必要输出和未解释 hardcode 均未完成。

## 完成条件

- 关键事实、假设和派生值状态分明；所有金融经验参数有来源/用户输入或 `MODEL_DERIVED` 标记。
- 预测、WACC、终值、bridge 和敏感性可沿公式追踪；硬数学错误为零。
- DCF validator 无硬错误；统一验证器状态和 `FORMULA_EVALUATION_UNVERIFIED` 限制已披露。
