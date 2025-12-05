# LoopRSI v2 策略设计文档：EMA 均线流与共振

## 1. 核心理念

结合 **L∞p | RSI** 的自适应超买超卖信号与 **EMA 均线系统** (21, 55, 100, 200) 的趋势支撑/阻力作用，旨在提高盈亏比（R:R）和胜率。

### 核心逻辑

*   **趋势判断**：利用大周期均线（4H EMA）判断主趋势。
*   **入场时机**：当 RSI 出现超买/超卖信号，且价格回踩/测试关键均线（1H EMA 21/55/100）时入场。这代表了"趋势中的回调买入"或"关键阻力的反转"。
*   **风险管理**：止损紧贴所测试的均线，止盈参考均线阻力。

---

## 2. 技术指标配置

### 主时间周期 (1H)

*   **Adaptive RSI**: 周期自适应 RSI (源自 L∞p | RSI，可启用 HMA 平滑)
*   **EMA Group**:
    *   `EMA 21`: 短期趋势/惯性
    *   `EMA 55`: 中期支撑
    *   `EMA 100`: 重要支撑
    *   `EMA 200`: 长期趋势参考
*   **Dual Channel Squeeze**: 布林带与肯特纳通道挤压检测（可选过滤器）
* 模拟 OFI：使用 volume 和 close 的关系。大阳线+巨量 = 强烈的买入失衡。
* 盘口保护 (在实盘中)：利用 custom_entry_price，检查 ob = self.dp.orderbook(pair, 5)。如果 Ask 侧挂单量是 Bid 侧的 10 倍（上方抛压巨大），即使 RSI 金叉了，也暂时不要买入。这就是利用订单簿逻辑来辅助中低频交易。

### 辅助时间周期 (4H - Informative)

*   **Trend EMA**: 用于判断大级别趋势方向 (e.g., EMA 174/200)。

---

## 3. 交易逻辑详解

### 3.1 入场策略 (Entry)

#### 做多 (Long) 条件：
1.  **RSI 超卖**：`Adaptive RSI < rsi_oversold` (优化值: 19)。
2.  **均线测试 (Confluence)**：
    *   价格 (`Low`) 触及或向下穿越 1H 周期某一根均线 (`EMA 21`, `55`, 或 `100`)。
    *   或者 价格在均线附近一定范围内 (`ema_test_tolerance`, e.g., 0.5%)。
3.  **趋势过滤** (可选/优化)：4H 收盘价 > 4H Trend EMA。
4.  **挤压过滤** (可选/优化)：仅在 Bollinger Band 挤入 Keltner Channel 时交易。

#### 做空 (Short) 条件：
1.  **RSI 超买**：`Adaptive RSI > rsi_overbought` (优化值: 70)。
2.  **均线测试 (Confluence)**：
    *   价格 (`High`) 触及或向上穿越 1H 周期某一根均线。
3.  **趋势过滤** (可选/优化)：4H 收盘价 < 4H Trend EMA。
4.  **挤压过滤** (可选/优化)。

### 3.2 动态止损 (Stop Loss)

利用 `custom_stoploss` 回调函数：

*   **逻辑**：止损位设在入场时测试的那根均线的外侧。
*   **计算**：
    *   **Long SL** = `Tested_EMA_Price * (1 - sl_buffer)`
    *   **Short SL** = `Tested_EMA_Price * (1 + sl_buffer)`
    *   `sl_buffer` (优化值: 0.8%)。
*   **兜底**：如果入场时未明显测试某根均线（例如纯 RSI 信号），使用固定止损（默认 -1%）。

### 3.3 动态止盈 (Take Profit)

利用 `custom_exit`：

*   **逻辑**：利用同周期 (1H) 的均线作为短期获利点。
*   **场景**：
    *   **Long TP**：价格触及 `EMA 55` 或 `EMA 100` (作为短期阻力)。
    *   **Short TP**：价格触及 `EMA 55` 或 `EMA 100` (作为短期支撑)。
    *   **RSI 止盈**：RSI 反向突破超买/超卖区。

---

## 4. Freqtrade 实现方案

### 4.1 `populate_indicators`
*   计算 1H 的 `EMA 21/55/100/200`。
*   引入 4H 数据 (`merge_informative_pair`) 并计算其 Trend EMA。
*   计算 1H 的 Adaptive RSI 和 Squeeze 指标。

### 4.2 `populate_entry_trend`
*   检测 1H 价格与 1H 均线的交叉/接触。
*   检查 4H 趋势方向。
*   定义 `enter_tag` 标记具体测试了哪根均线 (e.g., `long_test_ema55`)，以便在止损逻辑中使用。

### 4.3 `custom_stoploss`
*   读取 `trade.enter_tag`。
*   如果 tag 包含 `ema55`，则获取开仓时的 1H EMA 55 价格，计算止损距离。

### 4.4 `custom_exit`
*   监控实时价格与 1H EMA (55/100) 的关系。
*   如果触及，触发退出 (`reason: ema55_tp` / `ema100_tp`)。

---

## 5. 当前优化参数 (2024.01 - 2024.06)

基于 Hyperopt 优化结果：

*   **Timeframe**: 1h
*   **RSI**: Oversold 19, Overbought 70
*   **Filters**:
    *   `use_squeeze_filter`: False
    *   `use_trend_filter`: False (震荡行情参数)
*   **Risk**:
    *   `risk_per_trade`: 3%
    *   `sl_buffer`: 0.8%
    *   `ema_test_tolerance`: 0.5%

---

## 6. 策略优化建议

### 6.1 入场确认条件增强

#### 6.1.1 成交量确认机制

**当前状态**：仅有基础成交量过滤 `dataframe['volume_positive']`

**改进建议**：
```python
# 1. 成交量异常检测
volume_spike_threshold = 2.0  # 2倍平均成交量
volume_surge = dataframe['volume'] > dataframe['volume'].rolling(20).mean() * volume_spike_threshold

# 2. 成交量价格背离检测
price_up_volume_down = (dataframe['close'] > dataframe['close'].shift(1)) & \
                      (dataframe['volume'] < dataframe['volume'].shift(1))
price_down_volume_up = (dataframe['close'] < dataframe['close'].shift(1)) & \
                      (dataframe['volume'] > dataframe['volume'].shift(1))

# 3. 成交量动能指标
volume_momentum = dataframe['volume'] / dataframe['volume'].rolling(10).mean()
volume_confirm = volume_momentum > 1.5  # 成交量放大50%以上
```

**量化逻辑**：在RSI信号基础上，要求成交量确认信号有效性，避免虚假突破。

#### 6.1.2 多时间框架趋势一致性

**当前状态**：仅有EMA200趋势过滤

**改进建议**：
```python
# 1. 1H趋势确认
trend_1h_bullish = dataframe.get('trend_1h', 0) == 1
trend_1h_bearish = dataframe.get('trend_1h', 0) == -1

# 2. 15分钟趋势强度
trend_strength_15m = abs(dataframe['ema12'] - dataframe['ema26']) / dataframe['atr']
strong_trend_15m = trend_strength_15m > trend_strength_15m.rolling(50).mean() * 1.2

# 3. 趋势一致性评分
trend_consistency_score = 0
if trend_1h_bullish and dataframe['trend_bullish']:
    trend_consistency_score += 2
if trend_1h_bearish and dataframe['trend_bearish']:
    trend_consistency_score += 2
if strong_trend_15m:
    trend_consistency_score += 1

trend_confirm = trend_consistency_score >= 2
```

**量化逻辑**：要求多个时间框架趋势方向一致，提高信号可靠性。

#### 6.1.3 价格位置过滤器

**改进建议**：
```python
# 1. 价格在布林带中的位置
bb_position = (dataframe['close'] - dataframe['bb_lowerband']) / \
             (dataframe['bb_upperband'] - dataframe['bb_lowerband'])

# 2. 避免在极端位置入场
avoid_extreme_high = bb_position < 0.9  # 不在布林带上沿90%以上位置做多
avoid_extreme_low = bb_position > 0.1   # 不在布林带下沿10%以下位置做空

# 3. 价格相对EMA位置
price_above_ema21 = dataframe['close'] > dataframe['ema21']
price_below_ema21 = dataframe['close'] < dataframe['ema21']

# 4. 支撑阻力位距离
support_distance = abs(dataframe['close'] - dataframe['current_support']) / dataframe['close']
resistance_distance = abs(dataframe['current_resistance'] - dataframe['close']) / dataframe['close']

near_support = support_distance < 0.02  # 距离支撑2%以内
near_resistance = resistance_distance < 0.02  # 距离阻力2%以内
```

**量化逻辑**：避免在价格极端位置入场，提高风险收益比。

#### 6.1.4 市场波动性过滤

**改进建议**：
```python
# 1. ATR相对波动率
atr_ratio = dataframe['atr'] / dataframe['close']
volatility_threshold = atr_ratio.rolling(50).mean() * 1.5

# 2. 波动率状态分类
low_volatility = atr_ratio < atr_ratio.rolling(50).mean() * 0.7
normal_volatility = (atr_ratio >= atr_ratio.rolling(50).mean() * 0.7) & \
                    (atr_ratio <= atr_ratio.rolling(50).mean() * 1.5)
high_volatility = atr_ratio > atr_ratio.rolling(50).mean() * 1.5

# 3. 波动率变化率
volatility_change = atr_ratio.pct_change(5)
volatility_stable = abs(volatility_change) < 0.3  # 5日内波动率变化小于30%

# 4. 根据波动率调整入场条件
volatility_confirm = normal_volatility & volatility_stable
```

**量化逻辑**：在正常波动环境下入场，避免极端波动时期的虚假信号。

### 6.2 LTF止盈机制完善

#### 6.2.1 动态止盈目标调整

**当前状态**：固定使用1H EMA55/100作为止盈目标

**改进建议**：
```python
# 1. 根据入场信号强度调整止盈目标
def get_dynamic_tp_targets(entry_strength, market_regime):
    base_tp_multiplier = 1.0
    
    # 根据信号强度调整
    if entry_strength >= 6:
        base_tp_multiplier *= 1.3  # 强信号提高30%目标
    elif entry_strength <= 3:
        base_tp_multiplier *= 0.8  # 弱信号降低20%目标
    
    # 根据市场状态调整
    if market_regime == 'trending_up':
        base_tp_multiplier *= 1.2  # 趋势市场提高目标
    elif market_regime == 'volatile':
        base_tp_multiplier *= 0.7  # 波动市场降低目标
    
    return base_tp_multiplier

# 2. 分级止盈目标
tp_level_1 = 0.8   # 第一级目标：80%的常规目标
tp_level_2 = 1.2   # 第二级目标：120%的常规目标
tp_level_3 = 1.5   # 第三级目标：150%的常规目标

# 3. 根据持仓时间调整目标
def time_based_tp_adjustment(trade_duration_hours):
    if trade_duration_hours < 2:
        return 1.2  # 短时间内获利，提高目标
    elif trade_duration_hours > 24:
        return 0.8  # 长时间持仓，降低目标
    else:
        return 1.0  # 正常目标
```

#### 6.2.2 多重止盈触发条件

**改进建议**：
```python
# 1. EMA止盈 + RSI确认
def ema_rsi_tp_condition(current_rate, ema55_1h, ema100_1h, rsi_1h, trade_side):
    if trade.is_short:
        # 做空止盈：价格触及EMA且RSI未超卖
        tp1 = (current_rate <= ema55_1h) and (rsi_1h > 30)
        tp2 = (current_rate <= ema100_1h) and (rsi_1h > 25)
        return tp1 or tp2
    else:
        # 做多止盈：价格触及EMA且RSI未超买
        tp1 = (current_rate >= ema55_1h) and (rsi_1h < 70)
        tp2 = (current_rate >= ema100_1h) and (rsi_1h < 75)
        return tp1 or tp2

# 2. 趋势反转止盈
def trend_reversal_tp_condition(dataframe, trade_side):
    current_candle = dataframe.iloc[-1]
    prev_candle = dataframe.iloc[-2]
    
    if trade.is_short:
        # 做空趋势反转：1H EMA金叉
        ema_cross_up = (prev_candle['ema12_1h'] <= prev_candle['ema26_1h']) and \
                      (current_candle['ema12_1h'] > current_candle['ema26_1h'])
        return ema_cross_up
    else:
        # 做多趋势反转：1H EMA死叉
        ema_cross_down = (prev_candle['ema12_1h'] >= prev_candle['ema26_1h']) and \
                        (current_candle['ema12_1h'] < current_candle['ema26_1h'])
        return ema_cross_down

# 3. 时间止盈
def time_based_tp_condition(trade_duration_hours, current_profit):
    # 持仓超过一定时间且有合理利润时止盈
    if trade_duration_hours > 12 and current_profit > 0.015:  # 12小时且1.5%利润
        return True
    elif trade_duration_hours > 24 and current_profit > 0.01:  # 24小时且1%利润
        return True
    return False
```

#### 6.2.3 部分止盈机制

**改进建议**：
```python
# 1. 分级部分止盈
def partial_exit_logic(current_profit, trade_duration_hours):
    if current_profit >= 0.03:  # 盈利3%时
        if trade_duration_hours < 4:
            return 0.5  # 快速获利，止盈50%
        else:
            return 0.3  # 正常速度，止盈30%
    elif current_profit >= 0.05:  # 盈利5%时
        return 0.7  # 止盈70%
    return 0

# 2. 移动止盈
def trailing_tp_logic(current_profit, highest_profit, current_rate, entry_rate):
    # 盈利超过2%时启用移动止盈
    if current_profit > 0.02:
        # 保护50%的已实现最高利润
        trailing tp_level = highest_profit * 0.5
        if current_profit <= trailing_tp_level:
            return True
    return False

# 3. 动态调整仓位
def dynamic_position_management(current_profit, trade):
    # 根据盈利情况动态调整仓位
    if current_profit >= 0.04:  # 盈利4%以上
        return 0.5  # 减仓50%
    elif current_profit >= 0.02:  # 盈利2%以上
        return 0.7  # 减仓30%
    return 1.0  # 保持满仓
```

#### 6.2.4 市场环境适应性止盈

**改进建议**：
```python
# 1. 根据市场状态调整止盈策略
def market_adaptive_tp(market_regime, volatility_ratio):
    if market_regime == 'trending_up':
        # 趋势市场：放宽止盈目标
        tp_multiplier = 1.3
        trailing_activation = 0.025  # 2.5%盈利激活移动止盈
    elif market_regime == 'volatile':
        # 波动市场：收紧止盈目标
        tp_multiplier = 0.8
        trailing_activation = 0.015  # 1.5%盈利激活移动止盈
    else:
        # 震荡市场：标准止盈目标
        tp_multiplier = 1.0
        trailing_activation = 0.02   # 2%盈利激活移动止盈
    
    return tp_multiplier, trailing_activation

# 2. 重要时间窗口止盈
def time_window_tp(current_time, market_session):
    # 在重要时间窗口前止盈
    hour = current_time.hour
    
    # 避开重要数据发布时间
    if hour in [13, 14]:  # 美国CPI等数据发布时间
        return True
    
    # 避开流动性低的时间段
    if hour in [0, 1, 22, 23]:  # 深夜时段
        return True
    
    return False

# 3. 相关性止盈
def correlation_tp(pair, current_profit, other_pairs_profits):
    # 如果多个相关交易对同时盈利，考虑部分止盈
    if len(other_pairs_profits) >= 2:
        avg_other_profit = sum(other_pairs_profits) / len(other_pairs_profits)
        if avg_other_profit > 0.02 and current_profit > 0.015:
            return True
    return False
```

### 6.3 实施优先级建议

#### 高优先级（立即实施）
1. **成交量确认机制**：显著减少虚假信号
2. **动态止盈目标调整**：提高盈亏比
3. **趋势一致性确认**：提高信号质量

#### 中优先级（1-2周内）
1. **价格位置过滤器**：优化入场时机
2. **多重止盈触发条件**：提高止盈效率
3. **部分止盈机制**：锁定利润

#### 低优先级（长期优化）
1. **市场波动性过滤**：适应不同市场环境
2. **市场环境适应性止盈**：精细化风险管理
3. **相关性止盈**：组合层面优化

---

## 7. 操作指南

### 数据准备

```bash
# 下载数据 (含 4H Informative)
freqtrade download-data --exchange binance \
  --pairs BTC/USDT:USDT \
  --timeframes 1h 4h \
  --timerange 20240101-20251101 \
  --trading-mode futures
```

### 回测执行

```bash
# 激活环境
conda activate freqtrade

# 执行回测
freqtrade backtesting \
  --strategy LoopRSIStrategy \
  --timeframe 1h \
  --timerange 20240101-20251101 \
  --config user_data/config.json
```

### Hyperopt 优化

```bash
# 运行参数优化
freqtrade hyperopt \
  --strategy LoopRSIStrategy \
  --hyperopt-loss SharpeHyperOptLoss \
  --spaces buy sell \
  --timeframe 1h \
  --timerange 20240101-20240601 \
  -c user_data/config.json \
  -e 100
```