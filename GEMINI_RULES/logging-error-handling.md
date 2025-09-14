# Logging & Error Handling 📋

## Logging Standards
<!-- 中文注释: 切换到 Python 内置的 logging 模块，以减少外部依赖并与标准库保持一致，确保稳定性和性能。 -->
- Use Python's built-in `logging` module for logging. There should be a modular logging configuration file that is referenced.
- Use structured logging (e.g., JSON format) to ensure logs are machine-readable and easy to parse. <!-- 中文注释: 新增规则。结构化日志是实现自动化监控和分析的基础。 -->
- In Production, logs MUST be sent to a secure, remote, and access-controlled logging service. Avoid storing sensitive logs on the trading server itself. <!-- 中文注释: 新增规则。将日志与服务器分离，是关键的安全措施，可防范服务器入侵后日志被篡改或窃取。 -->
- Ensure a variety of different logging levels (e.g., DEBUG, INFO, WARNING, ERROR) are used to categorize events. <!-- 中文注释: 规则优化。强调日志分级的目的在于分类事件。 -->

## Core Logging Principles by Environment
- **Backtesting & Dry-Run Environments**: The goal is maximum detail for debugging. Log extensively, including full financial details, indicator values, and complete API responses (for dry-run). <!-- 中文注释: 新增原则。明确非生产环境的目标是详尽记录，用于分析和调试。 -->
- **Production Environment**: The goal is maximum security and essential traceability. Log minimal, event-driven, and non-sensitive information. Focus on WHAT happened, not HOW MUCH you have. <!-- 中文注释: 新增原则。明确生产环境的核心是安全，禁止记录敏感财务信息。 -->

## Production Environment Mandatory Logging
<!-- 中文注释: 本节内容根据安全原则被完全重写，以明确生产环境中应该记录什么。 -->
- **Order Execution Events**: Must include pair, side, quantity, price, and the exchange-provided orderID.
- **Realized PnL for individual closed trades**: Log relative changes (e.g., +$25.50 or +0.5%), NOT absolute account balances. <!-- 中文注释: 风险更新。禁止记录绝对余额，只记录单次交易的相对盈亏，保护核心财务隐私。 -->
- **API Call Status & Error Responses ONLY**: Log the status of API calls (success/failure) and the content of ERROR responses. Do NOT log the content of successful responses. <!-- 中文注释: 风险更新。禁止记录成功的API响应，因为其中通常包含完整的账户状态和仓位信息。 -->
- **Strategy Signal Events**: Log the signal event itself (e.g., 'StrategyX v1.2 triggered BUY'), not the underlying indicator values that led to it. <!-- 中文注释: 风险更新。只记录“信号”这个结果，不记录产生信号的计算过程，减少信息暴露。 -->
- **System Health & Security Events**: Log critical events like application start/stop, connection loss, configuration errors, and potential security issues. <!-- 中文注释: 新增规则。系统健康和安全日志对于线上问题排查至关重要。 -->

## Error Handling Mechanisms
Implement comprehensive error handling mechanisms, especially for:
- Exchange API connection disruptions
- Order execution failures
- Insufficient funds situations
- Price slippage exceeding expectations
- Insufficient liquidity warnings

## Error Handling Best Practices
- Define clear handling strategies for each error type
- Implement retry mechanisms and fallback solutions
- Log all error events and recovery operations
- Set appropriate timeouts and limits
- Ensure graceful system degradation under error conditions

## 代码示例 (Code Examples)

#### 1. 基础配置 (Basic Configuration)
*此示例展示了如何进行基础的日志配置，包括格式化和输出到文件/控制台。*
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s:%(funcName)s - %(message)s',
    handlers=[logging.FileHandler('trading.log'), logging.StreamHandler()]
)
```

#### 2. 日志轮转 (Log Rotation)
*此示例展示了如何配置日志文件按大小轮转，这是生产环境防止日志文件过大的关键实践。*
```python
from logging.handlers import RotatingFileHandler

# 创建一个在10MB时轮转的处理器，保留5个备份
handler = RotatingFileHandler('trading.log', maxBytes=10*1024*1024, backupCount=5)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
```

#### 3. 记录订单事件 (Logging Order Events)
*此示例对应“Order Execution Events”规则，展示了如何记录一笔完整的订单信息。*
```python
def log_order_event(order_id, symbol, action, price, quantity, status):
    logger.info("Order event: order_id=%s, symbol=%s, action=%s, price=%.2f, quantity=%.4f, status=%s",
                order_id, symbol, action, price, quantity, status)
```

#### 4. 记录API错误 (Logging API Errors)
*此示例对应“API Call Status & Error Responses ONLY”规则。*
```python
if order_status == "rejected":
    logger.error("Order rejected: order_id=%s, reason=%s", order_id, reason)
```

#### 5. 记录系统健康状态 (Logging System Health)
*以下示例对应“System Health & Security Events”规则。*
```python
# 价格异常
if abs(current_price - last_price) > threshold:
    logger.warning("Price anomaly: symbol=%s, current=%.2f, last=%.2f", symbol, current_price, last_price)

# 连接丢失
if not api_connected:
    logger.error("API lost: retrying in %d seconds", retry_interval)

# 策略心跳
logger.info("Strategy heartbeat: id=%s, status=running", strategy_id)
```

#### 6. 安全地记录风险指标 (Logging Risk Metrics Safely)
*此示例展示了如何记录相对的、非敏感的风险指标，符合脱敏原则。*
```python
# 记录止损事件和相对盈亏
if stop_loss_triggered:
    logger.info("Stop-loss: symbol=%s, price=%.2f, pnl_percent=%.2f%%", symbol, price, pnl_percent)

# 记录回撤百分比
if drawdown_percent > max_drawdown_percent:
    logger.critical("Drawdown exceeded: %.2f%% > %.2f%%", drawdown_percent, max_drawdown_percent)
```

#### 7. 标准异常处理 (Standard Exception Handling)
*此示例是“Error Handling Best Practices”的核心实践，展示了如何捕获并记录未知错误。*
```python
try:
    execute_trade()
except Exception as e:
    logger.error("Trade execution failed unexpectedly: %s", str(e), exc_info=True)
```