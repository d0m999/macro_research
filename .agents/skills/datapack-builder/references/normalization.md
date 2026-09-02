# Datapack Normalization

只在存在跨期、跨实体、跨币种或会计口径转换时读取。

- 期间：区分 instant、quarter、YTD、LTM 和 fiscal year；不得把 YTD 当单季。
- 单位：保留 reported unit，再用透明公式换算；百分比和 basis points 分开。
- 币种：记录 FX rate、日期、方向和来源；transaction-date、period-average 与 period-end rate 按用途选择并说明。
- 符号：收入/资产/现金流出等符号规则在 workbook 顶部统一声明。
- Restatement：保留原披露与重述版本，报告使用版本和理由。
- Non-GAAP：必须能回链到 issuer reconciliation；无法 reconciliation 时与 GAAP 分列。
- Entity：母公司、segment、continuing operations、discontinued operations 和 acquisition perimeter 分开。

无法可靠转换时保持 `SOURCE_UNAVAILABLE` 或原始口径，不用模型猜测制造可比性。
