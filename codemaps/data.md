<!-- Generated: 2026-06-08 | Files scanned: 96 | Token estimate: ~900 -->
# Data Codemap — Models, Schemas & Storage

## Market Data (Freqtrade)

### OHLCV Storage (Feather)

```
Path: user_data/data/binance/futures/
Format: Apache Arrow Feather (columnar, compressed)
```

| File | Timeframe | Type |
|------|-----------|------|
| `BTC_USDT_USDT-5m-futures.feather` | 5 min | OHLCV |
| `BTC_USDT_USDT-15m-futures.feather` | 15 min | OHLCV |
| `BTC_USDT_USDT-1h-futures.feather` | 1 hour | OHLCV (primary) |
| `BTC_USDT_USDT-4h-futures.feather` | 4 hour | OHLCV (informative) |
| `BTC_USDT_USDT-1d-futures.feather` | 1 day | OHLCV |
| `BTC_USDT_USDT-8h-funding_rate.feather` | 8 hour | Funding rate |
| `BTC_USDT_USDT-8h-mark.feather` | 8 hour | Mark price |

**OHLCV Schema (DataFrame columns):**
```
date      : datetime64[ns, UTC]  — Candle open time
open      : float64              — Open price
high      : float64              — High price
low       : float64              — Low price
close     : float64              — Close price
volume    : float64              — Base asset volume
```

---

## Freqtrade Trade Database

### user_data/tradesv3.sqlite

```
Path: user_data/tradesv3.sqlite
Engine: SQLite3 with WAL (Write-Ahead Logging)
ORM: SQLAlchemy 2.0 (via Freqtrade)
```

**Core Tables (Freqtrade managed):**
| Table | Purpose |
|-------|---------|
| `trades` | Trade records (entry/exit price, profit, duration) |
| `orders` | Individual order records (limit/market, fills) |
| `pairlocks` | Pair lock records (cooldown after losses) |

---

## Dashboard Trade Database (NEW)

### dashboard/trades.db

```
Path: dashboard/trades.db
Engine: SQLite3
Writer: dashboard/fetch_trades.py (cron @ 02:00)
Reader: dashboard/app.py (Streamlit, @st.cache_data ttl=60)
Source: OKX read-only API
Retention: 3-month rolling window (OKX limit), local: permanent
```

**Tables:**

#### `trades` — Order Fills
```sql
id          INTEGER PRIMARY KEY    -- OKX trade id
order_id    TEXT                   -- Parent order id (groups entry+exit)
symbol      TEXT                   -- e.g. BTC/USDT:USDT
side        TEXT                   -- 'buy' | 'sell'
datetime    TEXT                   -- ISO 8601 timestamp
price       REAL                   -- Fill price
amount      REAL                   -- Filled contracts
fee         REAL                   -- Fee in USDT
pnl         REAL                   -- Realized PnL (0 for opens)
type        TEXT                   -- 'open' | 'close' | 'liquidation'
```

**Primary key:** `id` (OKX-assigned, unique)

**Grouping:** app.py groups by `order_id` to combine entry+exit pairs,
then aggregates `pnl`, `fee` for metrics.

#### `positions` — Current Holdings
```sql
symbol          TEXT PRIMARY KEY  -- e.g. BTC/USDT:USDT
side            TEXT              -- 'long' | 'short'
contracts       REAL              -- Position size
entry_price     REAL              -- Average entry
mark_price      REAL              -- Current mark
unrealized_pnl  REAL              -- Open PnL
leverage        INTEGER           -- Position leverage
margin          REAL              -- Collateral locked
timestamp       TEXT              -- Last update
```

#### `balance_snapshots` — Account Equity
```sql
id          INTEGER PRIMARY KEY  -- Auto-increment
currency    TEXT                 -- e.g. USDT, BTC
total       REAL                 -- Total balance
free        REAL                 -- Available
used        REAL                 -- In positions
timestamp   TEXT                 -- Snapshot time
```

**Index recommendation** (not yet added):
```sql
CREATE INDEX idx_trades_orderid ON trades(order_id);
CREATE INDEX idx_trades_symbol  ON trades(symbol);
CREATE INDEX idx_balance_ts     ON balance_snapshots(timestamp);
```

---

## Strategy Indicator DataFrame

Columns added by `LoopRSIStrategy.populate_indicators()`:

```python
# Hilbert Transform
'smooth'           : float64  — 4-period MA smoothed price
'detrend'          : float64  — Detrended price
'period'           : float64  — Detected dominant period (clamped 6–50)
'adaptive_rsi'     : float64  — RSI with dynamic period
'rsi_momentum'     : float64  — RSI rate of change

# Squeeze Detection
'bb_upper/lower'   : float64  — Bollinger Bands
'kc_upper/lower'   : float64  — Keltner Channels
'squeeze_on'       : bool     — BB inside KC (compression)

# Trend & Volume
'ema_21/55/100/200': float64  — EMA ladder
'volume_sma'       : float64  — Volume moving average
'adx'              : float64  — ADX trend strength

# Phase 2 — Price Position
'price_position'   : float64  — Percentile rank in range
'is_low_position'  : bool     — Price in lower zone
'is_high_position' : bool     — Price in upper zone

# Phase 3 — Market Environment
'atr'              : float64  — Average True Range
'atr_pct'          : float64  — ATR as % of close
'volatility_regime': str      — 'low' | 'normal' | 'high'
'trend_strength'   : float64  — ADX-based classification
'market_env'       : str      — 'trending' | 'ranging'

# Informative (4h)
'ema_200_4h'       : float64  — 4h EMA for trend filter
```

---

## Backtest Results

```
Path: user_data/backtest_results/
Format: JSON + META.json pairs
Count: 8 result sets (Dec 2025)
```

**Result JSON Schema (simplified):**
```json
{
  "strategy": "LoopRSIStrategy",
  "strategy_comparison": [{ "key": "...", "trades": N, "profit_total": X }],
  "trades": [
    {
      "pair": "BTC/USDT:USDT",
      "profit_ratio": 0.023,
      "open_date": "2025-...",
      "close_date": "2025-...",
      "trade_duration": 180,
      "is_short": false,
      "exit_reason": "roi / stop_loss / custom_exit"
    }
  ]
}
```

---

## Hyperopt Results

```
Path: user_data/hyperopt_results/
Format: .fthypt (Freqtrade hyperopt binary)
Cache: hyperopt_tickerdata.pkl (pickled OHLCV for fast reloads)
Runs: 3 optimization sessions (Dec 2025)
```

**Optimized Parameter Space:**
```
buy_rsi_oversold     : IntParameter(10, 40)
buy_smoothing_length : IntParameter(10, 100)
buy_trend_ema_period : IntParameter(50, 300)
buy_risk_per_trade   : DecimalParameter(0.01, 0.05)
sell_rsi_overbought  : IntParameter(60, 90)
+ boolean feature toggles
```

---

## Configuration Schema

### user_data/config.json
```json
{
  "trading_mode": "futures",
  "margin_mode": "isolated",
  "exchange": { "name": "binance", "key": "***", "secret": "***" },
  "stake_currency": "USDT",
  "dry_run": true,
  "dry_run_wallet": 1000,
  "max_open_trades": 3,
  "pair_whitelist": ["BTC/USDT:USDT", "ETH/USDT:USDT"],
  "api_server": { "enabled": true, "listen_port": 8081 }
}
```

### user_data/strategies/LoopRSIStrategy.json (current)
```json
{
  "buy": {
    "bb_length": 20, "bb_mult": 2.0, "kc_length": 20, "kc_mult": 1.2,
    "median_length": 100, "ema_test_tolerance": 0.005,
    "enable_smoothing": true, "risk_per_trade": 0.03,
    "rsi_oversold": 19, "sl_buffer": 0.008,
    "smoothing_length": 50, "trend_ema_period": 174,
    "use_squeeze_filter": false, "use_trend_filter": false
  },
  "sell": { "rsi_overbought": 70 }
}
```

---

## Logging Schema

```
Path: user_data/logs/
Files: freqtrade.log, security_monitor.log, security_alerts.json
Format: Structured JSON (Winston-style)
Loggers: strategy, trade, performance, error, debug
```

### Dashboard Logs
```
Path: dashboard/cron.log
Format: Plain text timestamped lines
Content: "[YYYY-MM-DD HH:MM:SS] 开始采集OKX交易数据... / 采集完成"
```
