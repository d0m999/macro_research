<!-- Generated: 2026-06-08 | Files scanned: 96 | Token estimate: ~850 -->
# Architecture Codemap

## System Overview

Freqtrade-based algorithmic trading system for **BTC/ETH/SOL/RENDER USDT futures**.
Two coexisting subsystems:

1. **Freqtrade engine** — Python strategy execution (Binance, dry-run)
2. **Dashboard** — Streamlit visualization + OKX read-only trade sync

```
vibe-trading/
├── user_data/strategies/      # Freqtrade Python strategies
│   ├── LoopRSIStrategy.py     #   Primary: Hilbert + Adaptive RSI (1,056 LOC)
│   ├── base_strategy.py       #   Abstract base
│   ├── AwesomeStrategy.py     #   Template (unused in prod)
│   └── components/            #   Reusable indicator library
│       ├── indicators/        #     ARO, ATR-ZigZag, base classes
│       └── utils/             #     logging_config, math_utils
│
├── user_data/data/            # OHLCV Feather files (Binance futures)
├── user_data/backtest_results/  # JSON backtest outputs
├── user_data/hyperopt_results/  # Hyperopt .fthypt + ticker cache
├── user_data/tradesv3.sqlite  # Freqtrade trade history (SQLite/WAL)
│
├── dashboard/                 # ⭐ NEW — Streamlit observability
│   ├── app.py                 #   Web UI (313 LOC, plotly charts)
│   ├── fetch_trades.py        #   OKX read-only trade sync (222 LOC)
│   ├── cron_fetch.sh          #   Daily 02:00 cron wrapper
│   ├── cron.log               #   Last sync log
│   ├── README.md              #   Quickstart
│   └── trades.db              #   Local SQLite (trades, positions, balance)
│
├── PineScript/                # TradingView research indicators (24 .pine)
├── codemaps/                  # This directory
├── docker-compose.yml         # Container deployment
└── pyproject.toml             # uv-managed deps (49 packages)
```

## Core Data Flow (Freqtrade)

```
Market Data (Binance API)
    │
    ▼
OHLCV Feather Files (5m/15m/1h/4h/1d)
    │
    ▼
LoopRSIStrategy.populate_indicators()
    ├── Hilbert Transform → Adaptive Period (clamped 6-50)
    ├── Adaptive RSI (dynamic thresholds)
    ├── Dual Squeeze (BB inside KC)
    ├── EMA Confluence (21/55/100/200)
    └── Volatility Regime (ATR-based, Phase 3)
    │
    ▼
populate_entry_trend() / populate_exit_trend()
    ├── RSI oversold/overbought signals
    ├── EMA test confluence
    ├── Volume confirmation
    ├── Squeeze/trend/volatility filters
    │
    ▼
Risk Management Layer
    ├── custom_stake_amount()  → Dynamic position sizing
    ├── custom_stoploss()      → EMA-based trailing stop
    ├── custom_exit()          → Multi-level TP (TP1/TP2/TP3)
    └── confirm_trade_entry()  → Volatility gate
    │
    ▼
Trade Execution → user_data/tradesv3.sqlite
```

## Dashboard Data Flow (NEW)

```
OKX Read-Only API (every 24h @ 02:00)
    │  fetch_trades.py (ccxt, 3-month window)
    ▼
OKX Raw Trades / Positions / Balance Snapshots
    │
    ▼
dashboard/trades.db (SQLite)
    ├── trades            — order fills (pnl, fee, side, symbol)
    ├── positions         — current holdings (contracts, entry, unrealized)
    └── balance_snapshots — asset distribution over time
    │
    ▼
dashboard/app.py (Streamlit @ :8501)
    ├── 5-column metric cards (胜率/净盈亏/最大连亏/总手续费/笔数)
    ├── Cumulative PnL curve (plotly line)
    ├── Per-symbol & per-side statistics (bar/pie)
    ├── Current positions table
    └── Asset distribution pie (balance_snapshots)
```

## Module Dependency Graph

```
LoopRSIStrategy (main)
    ├── freqtrade.strategy (IStrategy, merge_informative_pair)
    ├── numpy (Hilbert transform, vectorized math)
    ├── pandas (DataFrame pipeline)
    ├── talib (EMA, BBANDS, RSI, ADX, ATR, HMA)
    └── technical (qtpylib helpers)

components/indicators/
    ├── base_indicator.py        → Abstract base (validation, caching)
    ├── improved_base_indicator.py → Performance-enhanced base
    ├── adaptive_resonance.py    → ARO (Hilbert + RSI + Squeeze)
    └── atr_zigzag.py            → ATR-based pivot detection

components/utils/
    ├── logging_config.py        → Multi-logger structured system
    └── math_utils.py            → Stats (Sharpe, Hurst, entropy, regime)

dashboard/app.py (Streamlit)
    ├── streamlit        (UI framework)
    ├── pandas           (data load)
    ├── plotly.express   (bar/pie charts)
    ├── plotly.graph_objects (line charts)
    └── sqlite3          (trades.db read)

dashboard/fetch_trades.py (OKX sync)
    ├── ccxt.okx         (exchange client)
    ├── python-dotenv    (secrets from .env)
    └── sqlite3          (trades.db write)
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
| Observability | Streamlit + OKX sync (new) | Real PnL/positions outside Freqtrade sandbox |
| Dep mgmt | uv (migrated from pip) | Faster, lockfile-driven |
