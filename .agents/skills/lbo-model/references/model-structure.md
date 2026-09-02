# LBO Model Structure

只在用户没有模板或需要补建 schedule 时读取。

## Sources & Uses

```text
Uses = Purchase Equity Value + Refinance Debt + Fees + Other Uses
Sources = New Debt + Rollover Equity + Sponsor Equity + Other Sources
Check = Sources - Uses
```

每个输入记录公开来源、`USER_PROVIDED` 或 `MODEL_DERIVED` 状态。Sponsor equity 是 balancing source 时必须显示公式，不隐藏为 plug。

## Debt schedule

每个 tranche 分列：opening balance、draw、mandatory amortization、optional repayment/cash sweep、PIK、cash interest、ending balance、rate/base rate/spread、maturity 和 covenant source。Interest 与平均/期初/期末 balance 的选择写在 assumptions。

## Returns

```text
Exit Enterprise Value = Exit Metric x Exit Multiple
Exit Equity Value = Exit Enterprise Value - Exit Net Debt - Other Claims + Non-operating Assets
Sponsor Proceeds = Exit Equity Value x Sponsor Ownership + Other Sponsor Cash Flows
MOIC = Sponsor Proceeds / Invested Sponsor Equity
IRR = Date-aware return over sponsor cash flows
```

Sensitivity axes 以主模型 base case 为中心，范围来自交易输入、公开对照、用户要求或 `MODEL_DERIVED` 情景。中心 cell 必须等于主模型回报。
