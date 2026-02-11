# Data Codemap — Models, Schemas & Storage

> Freshness: 2026-02-11 | Auto-generated

## Market Data

### OHLCV Storage (Feather format)
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

## Trade Database

### tradesv3.sqlite
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

### config.json
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

### LoopRSIStrategy.json (hyperopt best params)
```json
{
  "buy": {
    "rsi_oversold": 19, "smoothing_length": 50,
    "trend_ema_period": 174, "risk_per_trade": 0.03,
    "enable_smoothing": true, "use_squeeze_filter": false
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
