# Task 3: Valuation

只在执行 initiating coverage 的估值任务时读取。

## 方法选择

- DCF：有足够可解释经营驱动和资本成本输入时使用。
- Trading comps：有可比 peer、同口径 actual/forward 指标和估值时点市场输入时使用。
- Precedent transactions：只有官方交易事实和可比口径足够时使用。
- 其他方法：只有商业模式确实需要且输入可核验时使用。

方法可以并列交叉检查；权重必须解释本案数据质量和相关性，不采用固定默认。

## 验证

- DCF 保持 cash flow/discount rate 口径一致，Gordon Growth 满足 `g < discount rate`，EV-to-equity bridge 完整。
- Comps 记录 peer 纳入/排除、估值日期、EV adjustments、NM 处理和 selected multiple 来源。
- Precedents 记录 announce date、deal value、metric period、control/status 和 adjustments。
- Target price 的 share count、currency 和 valuation date 与 equity value 一致。
- 敏感性轴来自本案数据、用户输入或 `MODEL_DERIVED` 情景；中心值等于 base case。

完成时输出方法结果、输入状态、区间/权重理由、敏感性和限制。任何经验区间只作为明确的 `MODEL_DERIVED` 情景。
