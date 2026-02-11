# Backend Codemap — Python Strategies & Components

> Freshness: 2026-02-11 | Auto-generated

## Strategy Files

### LoopRSIStrategy.py (1,057 LOC) — Primary Strategy

```
Path: user_data/strategies/LoopRSIStrategy.py
Interface: IStrategy v3 | TF: 1h | Mode: Futures (long+short)
```

**Hyperopt Parameters (24 total):**
- `rsi_oversold` / `rsi_overbought` — Entry thresholds (default 20/80)
- `smoothing_length` — HMA smoothing period
- `trend_ema_period` — Trend filter EMA length
- `bb_length` / `bb_mult` — Bollinger Bands config
- `kc_length` / `kc_mult` — Keltner Channels config
- `risk_per_trade` — Position sizing (0.01–0.05)
- `enable_smoothing` / `use_squeeze_filter` / `use_trend_filter` — Feature toggles
- Phase 2: `enable_price_position_filter`, `tp1_ratio`–`tp3_ratio`
- Phase 3: `enable_volatility_filter`, `atr_multiplier`, `enable_market_env`

**Key Methods:**
| Method | Lines | Purpose |
|--------|-------|---------|
| `hilbert_transform_period()` | 263–363 | Vectorized period detection |
| `calculate_adaptive_rsi()` | 365–399 | Dynamic-period RSI |
| `populate_indicators()` | 400–530 | Full indicator pipeline |
| `populate_entry_trend()` | 530–700 | Long/short entry signals |
| `populate_exit_trend()` | 700–800 | Exit signals |
| `custom_stake_amount()` | 800–850 | Risk-based position sizing |
| `custom_stoploss()` | 850–920 | EMA trailing stop |
| `custom_exit()` | 920–1000 | Multi-level TP (Phase 2) |
| `confirm_trade_entry()` | 1000–1057 | Volatility gate (Phase 3) |

**Signal Logic:**
```
LONG: RSI < oversold AND (EMA21_test OR EMA55_test OR EMA100_test)
      AND volume > vol_sma AND [squeeze_ok] AND [trend_ok] AND [vol_ok]

SHORT: RSI > overbought AND (EMA21_test OR EMA55_test OR EMA100_test)
       AND volume > vol_sma AND [squeeze_ok] AND [trend_ok] AND [vol_ok]
```

### base_strategy.py — Abstract Base

```
Path: user_data/strategies/base_strategy.py
Role: Common risk management + indicator init
Subclasses: (not currently used by LoopRSI directly)
```

### my_advanced_strategy.py — Multi-Timeframe Template

```
Path: user_data/strategies/my_advanced_strategy.py
Role: Example multi-TF strategy with informative pairs
```

### AwesomeStrategy.py / sample_strategy.py — Templates

```
Role: Freqtrade starter templates (unused in production)
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

## Configuration

### config.json
```
Exchange: Binance | Mode: Futures (isolated margin)
Dry run: true | Wallet: 1000 USDT
Pairs: [BTC/USDT:USDT, ETH/USDT:USDT]
Max open trades: 3
API server: localhost:8081 (JWT auth)
```

### LoopRSIStrategy.json (hyperopt output)
```json
{
  "buy": { "rsi_oversold": 19, "smoothing_length": 50, "trend_ema_period": 174,
           "risk_per_trade": 0.03, "enable_smoothing": true },
  "sell": { "rsi_overbought": 70 }
}
```

---

## Dependencies (requirements.txt)

**Core:** numpy<2.0, pandas==2.3.1, talib==0.6.5, technical==1.5.2
**Exchange:** ccxt==4.4.99, aiohttp==3.12.15
**Data:** pyarrow==21.0.0, sqlalchemy==2.0.42
**API:** fastapi==0.116.1, uvicorn==0.35.0
**Notifications:** python-telegram-bot==22.3
**Utilities:** joblib, rich, jinja2, pydantic
