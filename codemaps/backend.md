<!-- Generated: 2026-06-08 | Files scanned: 96 | Token estimate: ~900 -->
# Backend Codemap — Python Strategies, Components & Dashboard

## Strategy Files

### LoopRSIStrategy.py (1,056 LOC) — Primary Strategy

```
Path: user_data/strategies/LoopRSIStrategy.py
Interface: IStrategy v3 | TF: 1h | Mode: Futures (long+short)
Author: d0m999 | Version: 1.0
```

**Three phases:**
- Phase 1: Hilbert + Adaptive RSI + Dual Squeeze (core)
- Phase 2: Price position + multi-TP (TP1/TP2/TP3 partial closes)
- Phase 3: Volatility + market environment regime filter

**Hyperopt Parameters (24 total):**
```
Phase 1: enable_smoothing, smoothing_length, median_length,
         rsi_oversold, rsi_overbought, bb_length, bb_mult,
         kc_length, kc_mult, trend_ema_period
Phase 2: enable_price_position_filter, tp1_ratio, tp2_ratio, tp3_ratio
Phase 3: enable_volatility_filter, atr_multiplier, enable_market_env
Risk:    risk_per_trade (0.01-0.05)
```

**Key Methods (line numbers):**
| Method | Range | Purpose |
|--------|-------|---------|
| `__init__()` | 55-58 | Init `trade_partial_tp_status` dict |
| `hilbert_transform_period()` | 263-363 | Vectorized period detection |
| `calculate_adaptive_rsi()` | 365-399 | Dynamic-period RSI |
| `populate_indicators()` | 400-530 | Full indicator pipeline |
| `populate_entry_trend()` | 530-700 | Long/short entry signals |
| `populate_exit_trend()` | 700-800 | Exit signals |
| `custom_stake_amount()` | 800-850 | Risk-based position sizing |
| `custom_stoploss()` | 850-920 | EMA trailing stop |
| `custom_exit()` | 920-1000 | Multi-level TP (Phase 2) |
| `confirm_trade_entry()` | 1000-1056 | Volatility gate (Phase 3) |

**Signal Logic:**
```
LONG:  RSI < oversold AND (EMA21_test OR EMA55_test OR EMA100_test)
       AND volume > vol_sma AND [squeeze_ok] AND [trend_ok] AND [vol_ok]
SHORT: RSI > overbought AND (EMA21_test OR EMA55_test OR EMA100_test)
       AND volume > vol_sma AND [squeeze_ok] AND [trend_ok] AND [vol_ok]
```

### base_strategy.py — Abstract Base (16,198 bytes)

```
Path: user_data/strategies/base_strategy.py
Role: Common risk management + indicator init
Subclasses: (not currently used by LoopRSI directly)
```

### Templates (unused in prod)

```
AwesomeStrategy.py       (16,857 bytes)
my_advanced_strategy.py  (22,830 bytes)
sample_strategy.py       (17,152 bytes)
```

---

## Component Library

### components/indicators/

| File | LOC | Exports |
|------|-----|---------|
| `base_indicator.py` | ~80 | `BaseIndicator` (ABC) — validate, calculate, cache |
| `improved_base_indicator.py` | ~100 | `ImprovedBaseIndicator` — performance-enhanced base |
| `adaptive_resonance.py` | ~200 | `AdaptiveResonanceOscillator` — Hilbert + RSI + Squeeze |
| `atr_zigzag.py` | ~100 | `ATRZigZag` — Pivot detection, S/R levels |

**AdaptiveResonanceOscillator pipeline:**
```
price → smooth(4-MA) → detrend → hilbert_transform → phase → period
period → adaptive_rsi(close, period)
BB(close) vs KC(close) → squeeze_on / squeeze_off
rsi + squeeze → composite signal
```

### components/utils/

| File | LOC | Key Exports |
|------|-----|-------------|
| `logging_config.py` | 332 | `setup_logger()`, `StrategyLogger`, `TradeLogger`, `PerfLogger` |
| `math_utils.py` | 490 | 15+ functions (see below) |

**math_utils.py functions:**
```
Statistical:  safe_divide, rolling_zscore, rolling_percentile_rank
Smoothing:    exponential_smoothing, adaptive_ema, smooth_noise_robust
Advanced:     hilbert_transform_period, calculate_fractal_dimension
              calculate_hurst_exponent, calculate_entropy
Risk:         calculate_sharpe_ratio, calculate_sortino_ratio
              calculate_calmar_ratio, calculate_drawdown_series
Detection:    detect_regime_change
```

---

## Dashboard Subsystem (NEW)

### dashboard/fetch_trades.py (222 LOC) — OKX Trade Sync

```
Path: dashboard/fetch_trades.py
Mode: Read-only API | Schedule: cron @ 02:00 daily
Symbols: BTC, ETH, SOL, RENDER /USDT:USDT
```

**Key Functions:**
| Function | Purpose |
|----------|---------|
| `get_exchange()` | Create `ccxt.okx` instance (env-based auth) |
| `fetch_recent_trades()` | Pull last 3 months fills via `fetchMyTrades` |
| `fetch_positions()` | Get current open positions |
| `fetch_balance()` | Get account balance snapshot |
| `init_database()` | Create tables if not exist (idempotent) |
| `sync_all()` | Main orchestrator: trades → positions → balance |

**Schema writes:**
```python
INSERT OR REPLACE INTO trades (id, order_id, symbol, side, ...)
INSERT OR REPLACE INTO positions (symbol, side, contracts, ...)
INSERT OR REPLACE INTO balance_snapshots (currency, total, free, ...)
```

**Env Vars Required:**
```
OKX_API_KEY
OKX_SECRET
OKX_PASSPHRASE
```

### dashboard/app.py (313 LOC) — Streamlit UI

```
Path: dashboard/app.py
Port: 8501 | DB: dashboard/trades.db
Cache: @st.cache_data(ttl=60) on all loaders
```

**Layout Sections:**
1. **Top metric cards** (5 columns): 总交易笔数 / 胜率 / 净盈亏 / 总手续费 / 最大连续亏损
2. **当前持仓** table (10 rows)
3. **账户余额** pie chart (asset distribution)
4. **收益曲线** cumulative PnL line (`px.line` with go.Scatter)
5. **按币种统计** bar (net PnL) + pie (trade count)
6. **按方向统计** table + bar (buy/sell PnL comparison)

**Data Loaders:**
```python
@st.cache_data(ttl=60)
def load_trades()       → pd.read_sql_query("SELECT * FROM trades ...")
def load_positions()    → pd.read_sql_query("SELECT * FROM positions ...")
def load_balance()      → pd.read_sql_query("SELECT * FROM balance_snapshots ...")
```

**Metrics Calculation (`calculate_metrics`):**
- Groups by `order_id` to combine entry/exit fills
- Computes: total_pnl, total_fee, net_pnl, win_rate, avg_win, avg_loss, max_consecutive_loss

### dashboard/cron_fetch.sh (11 LOC) — Cron Wrapper

```
Schedule: 0 2 * * *  (daily 02:00)
cd /Users/d0m999/Desktop/vibe-trading
export PATH="/Users/d0m999/.local/bin:$PATH"
uv run python dashboard/fetch_trades.py
```

---

## Configuration

### user_data/config.json
```
Exchange: Binance | Mode: Futures (isolated margin)
Dry run: true | Wallet: 1000 USDT
Pairs: [BTC/USDT:USDT, ETH/USDT:USDT]
Max open trades: 3
API server: localhost:8081 (JWT auth)
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

### .env (dashboard)
```
OKX_API_KEY=***
OKX_SECRET=***
OKX_PASSPHRASE=***
```

See `dependencies.md` for the full dep list (uv-managed).
