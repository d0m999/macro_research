# Three-Statement Formatting

只在用户没有模板样式或要求统一格式时读取。

- 显示币种、单位、财政期间和 Actual/Estimate。
- 视觉区分 hardcoded inputs、same-sheet formulas、cross-sheet links 和 checks；具体颜色可覆盖。
- Sections、subtotals 和 key outputs 使用一致的层级、border、number format 和缩进。
- 历史与预测之间使用清晰分隔；冻结 labels/header；隐藏列或行必须有理由。
- 负数、零、百分比、per-share、multiples 和 dates 在全 workbook 保持一致格式。
- Error/check cells 显示明确文字状态；不得只靠颜色表达失败。

金融健康阈值、covenant 和 warning bands 必须来自合同、公司披露、用户输入或标为 `MODEL_DERIVED` 的分析规则，不在版式参考中设置默认值。
