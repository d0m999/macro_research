# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FreqTrade quantitative trading system for Binance futures. Python 3.11+ strategies with PineScript research indicators. Primary strategy: **LoopRSIStrategy** (1h timeframe, 4h informative, isolated margin futures).

## Common Commands

```bash
# Environment setup (one-time)
brew install ta-lib              # macOS TA-Lib C library
uv sync                          # Create .venv and install all dependencies

# All commands use "uv run" prefix, or activate .venv first: source .venv/bin/activate

# Backtesting
uv run freqtrade backtesting --strategy LoopRSIStrategy --config user_data/config.json --timerange 20240101-20241201 --export trades

# Hyperparameter optimization
uv run freqtrade hyperopt --strategy LoopRSIStrategy --config user_data/config.json --epochs 100 --spaces buy sell roi stoploss

# Dry-run trading (ensure dry_run: true in config)
uv run freqtrade trade --config user_data/config.json --strategy LoopRSIStrategy

# Data management
uv run freqtrade download-data --config user_data/config.json --timerange 20240101-
uv run freqtrade list-data --config user_data/config.json

# Dependency management
uv add <package>                 # Add new dependency
uv lock --upgrade && uv sync     # Update all dependencies

# Docker production
docker compose up -d
docker compose logs -f freqtrade
docker compose down

# Config validation
uv run freqtrade show-config --config user_data/config.json
```

## Architecture

### Strategy Pipeline (IStrategy v3)

```
Exchange (Binance CCXT) → OHLCV Feather files
  → DataProvider (self.dp)
  → populate_indicators()  — 20+ columns (Hilbert, Adaptive RSI, Squeeze, EMAs)
  → populate_entry_trend()  — enter_long/enter_short signals
  → populate_exit_trend()   — exit_long/exit_short signals
  → Order Execution → Trade DB (tradesv3.sqlite)
```

### Key Source Files

- **`user_data/strategies/LoopRSIStrategy.py`** — Primary production strategy. Three phases: core RSI (Phase 1), price position + multi-TP (Phase 2), volatility + market environment (Phase 3). 24 hyperopt parameters.
- **`user_data/strategies/components/indicators/adaptive_resonance.py`** — ARO: Hilbert Transform + Adaptive RSI + BB/KC Squeeze detection.
- **`user_data/strategies/components/indicators/atr_zigzag.py`** — ATR-based pivot detection, S/R levels, ZigZag patterns.
- **`user_data/strategies/components/utils/math_utils.py`** — Statistical functions (Hilbert, fractal dimension, Hurst exponent, regime detection).
- **`user_data/strategies/components/utils/logging_config.py`** — Winston-style structured JSON logging with TradingLogger.
- **`user_data/strategies/base_strategy.py`** — Abstract base with risk management skeleton.
- **`PineScript/`** — TradingView research indicators (24 scripts). Prototyped here before Python conversion.

### Entry Signal Logic

Long: `adaptive_rsi < oversold AND EMA_confluence AND volume_ok AND [squeeze_ok] AND [trend_4h_ok] AND [volatility_ok]`
Short: Reversed conditions with `adaptive_rsi > overbought`.

### Risk Management Layers

1. Global: `max_open_trades=3`
2. Position sizing: 1-5% risk via `custom_stake_amount()`
3. Stop loss: 1% hard + EMA-based trailing via `custom_stoploss()`
4. Take profit: Multi-level (TP1/TP2/TP3) partial closes via `custom_exit()`
5. Gate filters: Squeeze, trend, volatility, price position via `confirm_trade_entry()`

### Configuration

- **`user_data/config.json`** — Template with `${ENV_VAR}` placeholders
- **`user_data/config_runtime.json`** — Docker production config (hardcoded creds)
- **`.env`** — API keys, JWT secrets (never committed)
- Trading mode: futures, isolated margin, USDT stake, BTC/ETH pairs

### Development Workflow

Research (PineScript/TradingView) → Prototype (components/indicators/) → Strategy integration (LoopRSIStrategy) → Backtest → Hyperopt → Dry-run → Docker deploy

### Deployment

Docker Compose with security hardening: non-root user, read-only FS, no-new-privileges, internal network (172.20.0.0/16), resource limits (1GB/0.5 CPU). Health check on port 8081.

## Coding Conventions

- Extend `IStrategy` (interface_version = 3) for new strategies
- Use vectorized NumPy/Pandas operations; avoid row-by-row loops in indicator calculations
- Custom indicators extend `BaseIndicator` with `calculate()` method
- Use `TradingLogger` for structured JSON logging (not plain print/logging)
- TA-Lib C library required (`brew install ta-lib` on macOS)
- Dependencies defined in `pyproject.toml`, locked in `uv.lock`
