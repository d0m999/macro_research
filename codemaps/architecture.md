# Architecture Codemap

> Freshness: 2026-02-11 | Auto-generated

## System Overview

Freqtrade-based algorithmic trading system for **BTC/USDT futures** on Binance.
Combines Python strategy engine with TradingView PineScript research indicators.

```
ft_userdata/
├── PineScript/              # TradingView research indicators (~8,400 LOC)
│   ├── _L∞p/                #   Core Loop indicators (RSI, MA, ATR-ZigZag)
│   ├── Oscillator/          #   ARO variants, TDI, rhythm oscillator
│   ├── Price_Zones/         #   SMC, S/R zones, price levels
│   ├── Vol/                 #   Volume analysis
│   ├── Open Interest/       #   Multi-exchange OI aggregation
│   └── ML: Lorentzian       #   Machine learning classification
│
├── user_data/               # Freqtrade runtime directory
│   ├── strategies/          #   Python strategies + components
│   ├── data/                #   OHLCV feather files (Binance futures)
│   ├── backtest_results/    #   JSON backtest outputs
│   ├── hyperopt_results/    #   Parameter optimization results
│   ├── logs/                #   Structured logs + security alerts
│   ├── config.json          #   Main trading config
│   └── tradesv3.sqlite      #   Trade history database
│
├── docker-compose.yml       # Container deployment
├── Dockerfile               # Build configuration
└── requirements.txt         # Python dependencies (50+ packages)
```

## Core Data Flow

```
Market Data (Binance API)
    │
    ▼
OHLCV Feather Files (5m/15m/1h/4h/1d)
    │
    ▼
LoopRSIStrategy.populate_indicators()
    ├── Hilbert Transform → Adaptive Period
    ├── Adaptive RSI (dynamic thresholds)
    ├── Dual Squeeze (BB + KC)
    ├── EMA Confluence (21/55/100/200)
    └── Volatility Regime (ATR-based)
    │
    ▼
populate_entry_trend() / populate_exit_trend()
    ├── RSI oversold/overbought signals
    ├── EMA test confluence
    ├── Volume confirmation
    ├── Squeeze filter (optional)
    ├── Trend filter (4h EMA)
    └── Volatility filter (Phase 3)
    │
    ▼
Risk Management Layer
    ├── custom_stake_amount()  → Dynamic position sizing
    ├── custom_stoploss()      → EMA-based trailing stop
    ├── custom_exit()          → Multi-level take profit
    └── confirm_trade_entry()  → Entry gate filter
    │
    ▼
Trade Execution → tradesv3.sqlite
```

## Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Freqtrade (IStrategy v3) | Mature, supports futures + dry-run |
| Data format | Feather (PyArrow) | Fast columnar I/O for OHLCV data |
| Timeframe | 1h primary, 4h informative | Balance between noise and signal |
| Indicators | Custom Hilbert/ARO, not TA-Lib RSI | Adaptive to market frequency |
| Risk mgmt | Per-trade custom sizing | 1-3% risk per trade, dynamic stops |
| Logging | Winston-style structured JSON | Audit trail + performance monitoring |
| Deployment | Docker + docker-compose | Reproducible, easy VPS deploy |

## Module Dependency Graph

```
LoopRSIStrategy (main)
    ├── freqtrade.strategy (IStrategy, merge_informative_pair)
    ├── freqtrade.persistence (Trade)
    ├── numpy (Hilbert transform, vectorized math)
    ├── pandas (DataFrame pipeline)
    ├── talib (EMA, BBANDS, RSI, ADX, ATR, HMA)
    └── technical (qtpylib helpers)

base_strategy
    ├── freqtrade.strategy (IStrategy)
    ├── components.indicators.adaptive_resonance
    └── components.indicators.atr_zigzag

components/indicators/
    ├── base_indicator.py        → Abstract base (validation, caching)
    ├── improved_base_indicator   → Enhanced base with performance
    ├── adaptive_resonance.py    → ARO (Hilbert + RSI + Squeeze)
    └── atr_zigzag.py            → ATR-based pivot detection

components/utils/
    ├── logging_config.py        → Multi-logger structured system
    └── math_utils.py            → Stats (Sharpe, Hurst, entropy, regime)
```
