---
inclusion: manual
---

# Performance & Risk Management ⚡

## Performance Optimization Requirements
- Prioritize vectorized operations over loops (applicable to Python/Pandas)
- Implement efficient data caching mechanisms
- Optimize strategy calculation processes to avoid redundant computations
- Pay attention to memory management, especially when handling large historical datasets

## Risk Management Control Measures
Implement the following risk control measures:
<!-- 安全风险：仓位限制缺乏具体数值，可能导致过度杠杆风险 -->
- Position sizing limits
<!-- 安全风险：止损机制需要硬编码限制，防止被策略逻辑绕过 -->
- Stop-loss mechanisms
- Volatility adjustments
<!-- 安全风险：资本分配规则需要监管合规检查 -->
- Capital allocation rules
<!-- 安全风险：交易频率限制需要防止市场操纵行为 -->
- Trade frequency limits

## Risk Management Framework
```
Risk Control Hierarchy
├── Strategy-Level Risk Control
│   ├── Single trade risk limits
│   ├── Daily maximum loss limits
│   └── Consecutive loss count limits
├── Portfolio-Level Risk Control
│   ├── Total position limits
│   ├── Sector/coin diversification requirements
│   └── Correlation risk control
└── System-Level Risk Control
    ├── System failure contingency plans
    ├── Network connection backup solutions
    └── Data integrity verification
```

## Performance Monitoring Metrics
- Strategy returns and Sharpe ratio
- Maximum drawdown and drawdown duration
- Win rate and profit/loss ratio
- Trading frequency and transaction costs
- System latency and execution slippage

## Capital Management Principles
<!-- 安全风险：固定分数法需要设置最大风险阈值 -->
- Fixed fractional position sizing
<!-- 安全风险：凯利公式可能推荐过高杠杆，需要上限约束 -->
- Kelly formula position optimization
<!-- 安全风险：动态风险调整需要人工监督，防止算法失控 -->
- Dynamic risk adjustment mechanisms
<!-- 安全风险：资金利用率优化不应超过监管要求的资本充足率 -->
- Capital utilization optimization