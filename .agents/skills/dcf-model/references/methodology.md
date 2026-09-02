# DCF Methodology

只在选择现金流定义、预测方法或终值方法时读取。

## Cash flow definition

FCFF 适合从 enterprise value 推到 equity value；FCFE 直接估计 equity value。全模型必须使用同一口径：现金流、discount rate、capital structure 和 terminal value 不得混用。

```text
NOPAT = EBIT x (1 - Cash Tax Rate)
FCFF = NOPAT + D&A - CapEx - Change in NWC
PV(FCF_t) = FCF_t / (1 + WACC)^t
Terminal Value (Gordon Growth) = FCF_(n+1) / (WACC - g)
Terminal Value (Exit Multiple) = Terminal Metric x Selected Multiple
```

若 fiscal year end 与估值日不重合，明确 stub period 与 discount timing。现金税、SBC、leases、capitalized R&D、NOL、minority interest 或养老金只在公司事实和估值口径需要时调整。

## Forecasts

按业务驱动而非无来源 top-down percentage 建模。每个 driver 对应历史、dated guidance、公开 peer evidence、`USER_PROVIDED` input 或 `MODEL_DERIVED` scenario。Bear/Base/Bull 是分析情景，不是外部事实。

## Terminal value

Gordon Growth 要求 `g < discount rate`。`g` 与成熟期经济、通胀、行业和公司再投资一致；exit multiple 与终期 metric、peer date 和口径一致。两种方法可以交叉检查，但不得以固定权重机械平均。
