# Pitch Deck Calculation Checks

只在 slide 中包含派生数字时读取。

```text
CAGR = (Ending / Beginning)^(1 / Periods) - 1
Share = Part / Total
Growth = Current / Prior - 1
Margin = Profit Metric / Revenue
Enterprise Value = Equity Value + Debt + Preferred + NCI - Cash - Other Non-operating Assets
```

确认 periods 定义、单位、币种、sign convention、GAAP/adjusted 和 Actual/Estimate。Bridge 的 components 应能回到 total；份额在相同 universe 下才检查合计。

舍入服从模板和用户要求；未指定时保持足以复核且跨页一致。任何 tolerance、异常值或估值区间来自用户规则、本案公开数据或标为 `MODEL_DERIVED` 的检查规则。
