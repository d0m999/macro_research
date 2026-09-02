# DCF Workbook Layout

只在用户没有现成模板时读取。

建议最小结构：

1. `Summary`：估值日期、情景、key drivers、implied EV/equity/per-share、market comparison、limitations。
2. `DCF`：历史与预测 operating model、FCF、discounting、terminal value、EV-to-equity bridge。
3. `WACC`：risk-free、beta、ERP、cost of debt、tax、market weights 及来源状态。
4. `Sensitivity`：base-centered grids 与情景输出。
5. `Sources`：每个 hardcode 的 source record、期间、单位、状态和 notes。

历史事实和假设放在可见 input 区；派生值使用 workbook formulas；跨 sheet link 与 same-sheet formula 在格式上可区分。所有输出标明币种、单位和 per-share denominator。
