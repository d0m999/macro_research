# DCF Sensitivity

只在构建 DCF sensitivity 时读取。

- 每张 grid 明确两个变量、固定的其他变量和输出单位。
- 中心行/列精确引用主模型 base assumptions；中心 cell 必须等于主模型相同输出。
- 轴范围与步长来自本案历史波动、公开 peer evidence、用户输入，或标为 `MODEL_DERIVED` 的压力情景。
- 每个 cell 使用完整、同口径的估值公式；不要用手工插值冒充重算。
- 若某组合使 `g >= WACC`、分母为零/负数或其他数学关系无效，显示明确的 invalid 状态而不是伪造价格。
- 至少检查单调性预期；不符合时调查公式或经济逻辑，而非直接覆盖结果。
