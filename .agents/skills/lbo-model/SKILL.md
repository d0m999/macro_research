---
name: lbo-model
description: "在用户模板或标准结构中建立 LBO 模型，覆盖 Sources & Uses、经营模型、债务滚动、cash sweep、IRR/MOIC 与敏感性。"
---

# LBO Model

优先复制并填充用户提供的模板。没有模板时，若用户已授权完整模型，则采用标准的 Sources & Uses、Operating Model、Debt Schedule 和 Returns 结构继续执行，无需因缺少模板单独暂停。

## 必读契约

- 填入公开或用户数据前读取 [`../../PUBLIC-SOURCE-POLICY.md`](../../PUBLIC-SOURCE-POLICY.md)。
- 创建或修改 `.xlsx` 前读取 [`../../CODEX-EXECUTION-POLICY.md`](../../CODEX-EXECUTION-POLICY.md)。
- 模板是结构事实来源；保留用户原文件并输出副本。原地覆盖仅在用户明确要求时进行。
- 用户没有模板或需要补建 schedule 时读取 [`references/model-structure.md`](references/model-structure.md)。

## 输入状态

历史财务和公开交易事实使用 filings/官方交易文件；未公开 purchase price、fees、leverage、debt terms、management rollover、growth、margin、exit multiple 和 hold period 来自 `USER_PROVIDED` 或标为 `MODEL_DERIVED`。不得把“市场常见”范围当事实默认值。

## 工作流

1. **映射模板和交易时点**：确认币种、单位、entry date、LTM/NTM 口径、purchase price、capitalization 和已有 formulas。
2. **Sources & Uses**：建立 purchase equity value 到 transaction uses 的 bridge，并确保 sources = uses。每个 fee、financing 和 equity rollover 有来源/状态。
3. **经营模型**：连接历史 actuals 与收入、margin、tax、CapEx、D&A、NWC 和 cash flow 驱动；派生值使用 formulas。
4. **债务 schedule**：逐 tranche 建立 opening、draw、mandatory amortization、optional repayment/cash sweep、PIK、interest 和 ending balance。明确 cash minimum 和 revolver 逻辑。
5. **退出与回报**：从 exit operating metric 和 exit multiple 推导 EV，扣除 net debt 和其他 adjustment，计算 sponsor proceeds、MOIC 和按实际日期/期间的 IRR。
6. **敏感性**：轴来自本案输入、用户要求或 `MODEL_DERIVED` 情景；base cell 与主模型完全一致。
7. **内部校验后交付**：连续检查 sources/uses、现金、债务、利息、circularity、exit bridge、MOIC/IRR 和公式错误；无需逐段用户确认。

## 完成条件

- Sources = Uses；现金和每笔债务 roll-forward 连续；exit EV-to-equity bridge 与 sponsor proceeds 可重算。
- 所有交易/经验参数有公开来源、用户输入或 `MODEL_DERIVED` 标记；关键缺口明确列出。
- 统一 artifact 验证器返回成功或受限成功，并披露公式求值限制。
