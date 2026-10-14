# Comps Formula Reference

只在实现 workbook 计算时读取。符号按模板调整，但保持公式链可追踪。

```text
Market Capitalization = Price x Diluted Shares
Enterprise Value = Market Capitalization + Debt + Preferred + NCI - Cash - Other Non-operating Assets
Revenue Growth = Current Revenue / Prior Revenue - 1
EBITDA Margin = EBITDA / Revenue
EV / Revenue = Enterprise Value / Revenue
EV / EBITDA = Enterprise Value / EBITDA
P / E = Equity Value / Net Income
Implied EV = Selected Multiple x Target Metric
Implied Equity Value = Implied EV - Debt - Preferred - NCI + Cash + Other Non-operating Assets
Implied Price = Implied Equity Value / Target Diluted Shares
```

只使用与指标期间一致的 EV/equity value。负值或经济意义不成立的分母显示 `NM`，并从对应统计量中排除；不要把 `NM` 当零。

分位数、median、mean、min/max 直接引用可见 peer rows。Selected multiple 来自本次 peer distribution、用户输入或 `MODEL_DERIVED` 情景，并在旁边记录选择理由。
