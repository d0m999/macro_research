Based on Context7 documentation, here is the full breakdown:

---

## FreqTrade 功能全景与运作逻辑

### 一、核心功能模块

```
+=====================================================================+
|                        FREQTRADE  FEATURE  MAP                      |
+=====================================================================+
|                                                                     |
|  [1] STRATEGY DEV        [2] DATA            [3] BACKTESTING       |
|  +------------------+    +---------------+    +------------------+  |
|  | IStrategy class  |    | OHLCV download|    | Historical sim   |  |
|  | populate_*()     |    | JSON/Parquet  |    | Multi-strategy   |  |
|  | Callbacks        |    | Multi-exchange|    | Trade export     |  |
|  | Pine->Python     |    | Futures data  |    | Signal export    |  |
|  +------------------+    +---------------+    +------------------+  |
|                                                                     |
|  [4] HYPEROPT         [5] LIVE/DRY-RUN      [6] MONITORING         |
|  +------------------+ +------------------+   +------------------+   |
|  | ML optimization  | | Real trading     |   | Telegram bot     |   |
|  | ROI/SL/Trailing  | | Dry-run (paper)  |   | Web UI (FreqUI)  |   |
|  | Buy/Sell params  | | Order management |   | API Server       |   |
|  | Sharpe/Sortino   | | Position adjust  |   | Profit/Loss logs |   |
|  +------------------+ +------------------+   +------------------+   |
|                                                                     |
|  [7] RISK MGMT        [8] PLUGINS           [9] FreqAI            |
|  +------------------+  +------------------+  +------------------+  |
|  | Stoploss (fixed) |  | Pairlist filters |  | ML models        |  |
|  | Trailing stop    |  | Protections      |  | RL agents        |  |
|  | ROI table        |  | CooldownPeriod   |  | Feature eng.     |  |
|  | custom_stoploss()|  | MaxDrawdown      |  | Prediction       |  |
|  | Max open trades  |  | StoplossGuard    |  | Auto-retrain     |  |
|  +------------------+  +------------------+  +------------------+  |
+=====================================================================+
```

### 二、Bot 主循环 (Core Event Loop)

```
  freqtrade trade --strategy LoopRSIStrategy
         |
         v
  +-------------------------------+
  |       bot_start()             |   <-- one-time init callback
  +-------------------------------+
         |
         v
  +===========================================+
  |          MAIN LOOP (every N sec)          |  <-- internals.process_throttle_secs
  |          ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    |
  |                                           |
  |  +------------------------------------+  |
  |  | 1. Fetch open trades from DB       |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 2. Calculate tradable pair list    |  |
  |  |    (VolumePairList, filters, etc.) |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 3. Download OHLCV data             |  |  <-- once per candle only
  |  |    (+ informative pairs)           |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 4. bot_loop_start() callback       |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 5. ANALYZE STRATEGY (per pair)     |  |
  |  |    +----------------------------+  |  |
  |  |    | populate_indicators()      |  |  |
  |  |    +----------------------------+  |  |
  |  |                |                   |  |
  |  |                v                   |  |
  |  |    +----------------------------+  |  |
  |  |    | populate_entry_trend()     |  |  |
  |  |    +----------------------------+  |  |
  |  |                |                   |  |
  |  |                v                   |  |
  |  |    +----------------------------+  |  |
  |  |    | populate_exit_trend()      |  |  |
  |  |    +----------------------------+  |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 6. UPDATE EXISTING TRADES          |  |
  |  |    order_filled()                  |  |
  |  |    check_entry_timeout()           |  |
  |  |    check_exit_timeout()            |  |
  |  |    adjust_order_price()            |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 7. PROCESS EXITS                   |  |
  |  |    stoploss / ROI / exit-signal    |  |
  |  |    custom_exit()                   |  |
  |  |    custom_stoploss()               |  |
  |  |    custom_exit_price()             |  |
  |  |    confirm_trade_exit()            |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 8. POSITION ADJUSTMENT             |  |
  |  |    adjust_trade_position()         |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |  +------------------------------------+  |
  |  | 9. PROCESS ENTRIES (if slots open) |  |
  |  |    custom_entry_price()            |  |
  |  |    leverage()                      |  |
  |  |    custom_stake_amount()           |  |
  |  |    confirm_trade_entry()           |  |
  |  +------------------------------------+  |
  |                 |                         |
  |                 v                         |
  |            [ LOOP BACK ]                  |
  +===========================================+
```

### 三、策略数据流 (Strategy Data Pipeline)

```
  Exchange API (Binance/OKX/...)
       |
       |  OHLCV + Orderbook + Trades
       v
  +------------------+     +-------------------+
  | DataProvider     |---->| informative_pairs |  (e.g. BTC/USDT 1d)
  | (self.dp)       |     | additional TFs    |
  +------------------+     +-------------------+
       |                          |
       v                          v
  +------------------------------------------------+
  |          populate_indicators()                  |
  |                                                |
  |   Raw OHLCV DataFrame (pandas)                 |
  |   +------------------------------------------+ |
  |   | open | high | low | close | volume | ... | |
  |   +------------------------------------------+ |
  |          |                                     |
  |          v                                     |
  |   +-- Technical Indicators --+                 |
  |   | RSI, EMA, MACD, ATR,    |                 |
  |   | Bollinger, OBV, ADX,    |                 |
  |   | Custom (ARO, ZigZag...) |                 |
  |   +--------------------------+                 |
  +------------------------------------------------+
       |
       v
  +------------------------------------------------+
  |       populate_entry_trend()                    |
  |                                                |
  |   IF conditions met:                           |
  |     df['enter_long'] = 1                       |
  |     df['enter_short'] = 1                      |
  |     df['enter_tag'] = "reason"                 |
  +------------------------------------------------+
       |
       v
  +------------------------------------------------+
  |       populate_exit_trend()                     |
  |                                                |
  |   IF conditions met:                           |
  |     df['exit_long'] = 1                        |
  |     df['exit_short'] = 1                       |
  |     df['exit_tag'] = "reason"                  |
  +------------------------------------------------+
       |
       v
  +------------------------------------------------+
  |        ORDER EXECUTION                         |
  |                                                |
  |   confirm_trade_entry() ---> Exchange Order    |
  |   confirm_trade_exit()  ---> Exchange Order    |
  +------------------------------------------------+
```

### 四、回调函数全景 (All Strategy Callbacks)

```
  LIFECYCLE CALLBACKS                    ORDER CALLBACKS
  =====================                  ====================

  bot_start()                            confirm_trade_entry()
       |                                 confirm_trade_exit()
  bot_loop_start()                       order_filled()
       |                                 check_entry_timeout()
  populate_indicators()                  check_exit_timeout()
  populate_entry_trend()                 adjust_order_price()
  populate_exit_trend()                    +-- adjust_entry_price()
                                           +-- adjust_exit_price()

  PRICING CALLBACKS                      RISK CALLBACKS
  ====================                   ====================

  custom_entry_price()                   custom_stoploss()
  custom_exit_price()                    custom_exit()
  custom_stake_amount()                  adjust_trade_position()
  leverage()                             protections (plugin)
```

### 五、Pairlist 过滤链 (Plugin Pipeline)

```
  All Exchange Pairs
       |
       v
  +-------------------+
  | VolumePairList    |  Top N by volume
  +-------------------+
       |
       v
  +-------------------+
  | DelistFilter      |  Remove delisted
  +-------------------+
       |
       v
  +-------------------+
  | AgeFilter         |  Min listing age
  +-------------------+
       |
       v
  +-------------------+
  | PrecisionFilter   |  Tick size ok?
  +-------------------+
       |
       v
  +-------------------+
  | PriceFilter       |  Min price ratio
  +-------------------+
       |
       v
  +-------------------+
  | SpreadFilter      |  Max spread
  +-------------------+
       |
       v
  +-------------------+
  | RangeStability    |  Min rate of change
  +-------------------+
       |
       v
  +-------------------+
  | VolatilityFilter  |  Vol range ok?
  +-------------------+
       |
       v
  +-------------------+
  | ShuffleFilter     |  Randomize order
  +-------------------+
       |
       v
  Final Tradable Pairs
```

### 六、风控保护机制 (Protections)

```
  Trade Result
       |
       v
  +-----------------------+
  | CooldownPeriod        |  N candles pause after trade
  +-----------------------+
       |
       v
  +-----------------------+
  | StoplossGuard         |  Too many SL hits? -> pause
  |  4 SL in 24 candles   |
  +-----------------------+
       |
       v
  +-----------------------+
  | MaxDrawdown           |  Drawdown > 20%? -> pause
  |  20 trades lookback   |
  +-----------------------+
       |
       v
  +-----------------------+
  | LowProfitPairs        |  Pair losing money? -> lock
  |  profit < 2% in 6 c.  |
  +-----------------------+
       |
       v
  Continue or LOCK pair/global
```

### 七、开发工作流 (Development Workflow)

```
  [1] DEVELOP            [2] BACKTEST          [3] OPTIMIZE
  Write strategy.py  --> freqtrade backtesting --> freqtrade hyperopt
  populate_*()           --timerange              --spaces roi stoploss
  callbacks              --export trades          --epochs 100
       |                      |                        |
       v                      v                        v
  [4] DRY-RUN            [5] ANALYZE           [6] LIVE
  freqtrade trade        freqtrade plot-profit  freqtrade trade
  --dry-run              backtesting-analysis   (dry_run: false)
  Paper trading          SQL / DataFrame         Real money
       |                      |                        |
       +----------+-----------+                        |
                  |                                     |
                  v                                     v
           [7] MONITOR via Telegram / FreqUI / API Server
```

### 功能总结

| 类别 | 功能 |
|------|------|
| **策略开发** | Python + Pandas，三段式 `populate_*()` 架构，20+ 回调钩子 |
| **数据** | 多交易所 OHLCV，JSON/Parquet/Feather，多时间框架，Orderbook/Trades |
| **回测** | 历史模拟，多策略对比，逐 tick 精细回测，信号/交易导出 |
| **优化** | Hyperopt (ML)，ROI/SL/Trailing/Buy/Sell 参数空间，Sharpe/Sortino 损失函数 |
| **风控** | 固定/追踪/自定义止损，ROI 表，Protections 插件，最大持仓限制 |
| **交易** | Dry-run / Live，限价/市价单，仓位调整，杠杆控制 (期货) |
| **插件** | Pairlist 过滤链，保护机制，Edge positioning |
| **AI/ML** | FreqAI 集成，强化学习 agent，自动特征工程，模型自动重训 |
| **监控** | Telegram 机器人，FreqUI Web 界面，REST API Server |
