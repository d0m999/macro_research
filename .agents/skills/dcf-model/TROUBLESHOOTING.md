# DCF Troubleshooting

只在结构检查失败、公式出现错误或主模型与敏感性不一致时读取。

- `#REF!`：定位被移动/删除的 range 或 sheet，恢复到正确输入；不要用 hardcode 覆盖错误。
- `#DIV/0!`：检查缺失 driver、无经济意义的分母或无效终值组合；无效组合应明确显示 invalid。
- `#VALUE!`：检查单位、文本数字、日期和 array/range 维度。
- 中心敏感性不等于主模型：确认 axis center 引用 base assumptions，且每个 cell 使用相同 EV-to-equity bridge。
- 估值异常：先查期间、单位、share count、net debt 符号、stub discounting 和 terminal formula，再审查假设来源。不得用无来源“合理范围”强行校准结果。
