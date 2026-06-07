# Contributing Guide

## Project Overview

FreqTrade 量化交易用户数据项目，包含自定义策略、PineScript 指标和 Docker 部署配置。

## Tech Stack

- **Runtime**: Python 3.11+ (uv 环境)
- **Framework**: FreqTrade 2026.1 (stable, from GitHub)
- **Data**: Pandas, NumPy 2.x, PyArrow
- **Indicators**: TA-Lib, ft-pandas-ta, technical
- **Exchange**: CCXT (Binance)
- **API Server**: FastAPI + Uvicorn
- **Database**: SQLite (tradesv3.sqlite)
- **Notifications**: python-telegram-bot 22.3
- **Container**: Docker (freqtradeorg/freqtrade:stable)

## Project Structure

```
ft_userdata/
├── docker-compose.yml          # Docker 部署（安全加固配置）
├── Dockerfile                  # 自定义镜像构建
├── pyproject.toml              # Python 依赖（source of truth）
├── uv.lock                     # 确定性依赖锁文件
├── requirements.txt            # Docker 兼容依赖列表
├── .env                        # 环境变量（敏感信息，勿提交）
├── .gitignore                  # Git 忽略规则
├── LOCAL_SETUP.md              # 本地开发环境指南
├── open-interest-logic.md      # OI 持仓量分析逻辑
├── PineScript/                 # TradingView Pine Script 指标
│   ├── _L∞p/                   # Loop 系列指标
│   ├── Open Interest/          # OI 相关指标
│   ├── Oscillator/             # 振荡器指标
│   ├── Price_Zones/            # 价格区域指标
│   ├── Vol/                    # 成交量指标
│   └── Zigzag/                 # ZigZag 指标
└── user_data/                  # FreqTrade 用户数据
    ├── config.json             # FreqTrade 主配置
    ├── config_runtime.json     # 运行时安全配置
    ├── strategies/             # 交易策略
    │   ├── LoopRSIStrategy.py  # Loop RSI 策略（主力策略）
    │   ├── AwesomeStrategy.py  # 综合策略
    │   ├── base_strategy.py    # 基础策略类
    │   ├── my_advanced_strategy.py
    │   ├── sample_strategy.py
    │   └── components/         # 策略组件
    │       ├── indicators/     # 自定义指标（ARO, ATR ZigZag）
    │       └── utils/          # 工具（日志、数学函数）
    ├── data/                   # 历史数据缓存
    ├── backtest_results/       # 回测结果
    ├── hyperopt_results/       # 超参数优化结果
    ├── logs/                   # 运行日志
    └── notebooks/              # Jupyter notebooks
```

## Environment Setup

### Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python 包管理器)
- Python 3.11+（uv 自动安装）
- TA-Lib C library（macOS: `brew install ta-lib`）

### Quick Start

```bash
# 安装 TA-Lib C 库（macOS）
brew install ta-lib

# 创建环境并安装所有依赖
uv sync

# 验证
uv run freqtrade --version
uv run freqtrade show-config --config user_data/config.json
```

## Environment Variables

Source: `.env` (not committed to git)

| Variable | Purpose | Format |
|----------|---------|--------|
| `EXCHANGE_API_KEY` | Exchange API key | String |
| `EXCHANGE_API_SECRET` | Exchange API secret | String |
| `JWT_SECRET_KEY` | JWT authentication secret | 64-char hex |
| `WS_TOKEN` | WebSocket authentication token | 32-char hex |
| `API_USERNAME` | FreqTrade API username | String |
| `API_PASSWORD` | FreqTrade API password | Base64 string |
| `TELEGRAM_TOKEN` | Telegram bot token (optional) | `bot_id:token` |
| `TELEGRAM_CHAT_ID` | Telegram chat ID (optional) | Numeric string |
| `DB_URL` | Database connection string | SQLite URI |

## Available Commands

### Backtesting

```bash
# Basic backtest
freqtrade backtesting --config user_data/config.json --strategy LoopRSIStrategy

# With timerange
freqtrade backtesting --strategy LoopRSIStrategy --timerange 20230101-20231201

# Export trades for analysis
freqtrade backtesting --strategy LoopRSIStrategy --timerange 20230101-20231201 --export trades

# Analyze results
freqtrade backtesting-analysis --export-filename user_data/backtest_results/backtest-result.json
```

### Hyperparameter Optimization

```bash
freqtrade hyperopt --config user_data/config.json \
  --hyperopt-loss SampleHyperOptLoss \
  --strategy LoopRSIStrategy \
  --epochs 100
```

### Trading

```bash
# Dry-run (simulated)
freqtrade trade --config user_data/config.json --strategy LoopRSIStrategy

# Web UI
freqtrade webserver --config user_data/config.json
```

### Docker

```bash
# Start with docker-compose
docker compose up -d

# View logs
docker compose logs -f freqtrade

# Stop
docker compose down
```

### Data Management

```bash
# Download historical data
freqtrade download-data --config user_data/config.json --timerange 20230101-

# List available data
freqtrade list-data --config user_data/config.json
```

## Testing Procedures

### Strategy Validation

```bash
# 1. Backtest on historical data
freqtrade backtesting --strategy LoopRSIStrategy --timerange 20240101-20241201

# 2. Check config validity
freqtrade show-config --config user_data/config.json

# 3. Dry-run for live validation
freqtrade trade --config user_data/config.json --strategy LoopRSIStrategy
# (ensure dry_run: true in config.json)
```

### Pine Script Indicators

Pine Script indicators in `PineScript/` are tested directly on TradingView. When converting to Python, verify output matches the original Pine Script indicator on the same dataset.

## Development Workflow

1. Create/modify strategy in `user_data/strategies/`
2. Backtest with historical data to validate logic
3. Run hyperopt to optimize parameters
4. Dry-run to validate in simulated live conditions
5. Deploy via Docker for production trading

## Coding Conventions

- Strategy classes extend `BaseStrategy` or `IStrategy`
- Custom indicators go in `user_data/strategies/components/indicators/`
- Utility functions go in `user_data/strategies/components/utils/`
- Use vectorized Pandas/NumPy operations over Python loops
- All strategy parameters should be configurable via `hyperopt_params`
- Log important events using the structured logging system in `components/utils/logging_config.py`

<!-- AUTO-GENERATED:START (source: dashboard/* + CLAUDE.md + pyproject.toml) -->
## Dashboard Subsystem (added 2026-06-08)

### Dashboard Commands

| Command | Description |
|---------|-------------|
| `uv run streamlit run dashboard/app.py` | Launch Streamlit dashboard @ http://localhost:8501 |
| `uv run python dashboard/fetch_trades.py` | Manually trigger OKX trade sync to `trades.db` |
| `bash dashboard/cron_fetch.sh` | Run the cron-wrapper (used by system crontab) |
| `tail -f dashboard/cron.log` | View last sync log output |

### Dashboard Files

| File | Purpose |
|------|---------|
| `dashboard/app.py` | Streamlit UI: 5 metric cards, PnL curve, per-symbol/per-side stats |
| `dashboard/fetch_trades.py` | OKX read-only sync (ccxt → SQLite). 3-month rolling window |
| `dashboard/cron_fetch.sh` | Cron wrapper (sets PATH then runs fetch_trades.py) |
| `dashboard/trades.db` | SQLite: `trades`, `positions`, `balance_snapshots` tables |
| `dashboard/cron.log` | Last fetch log output |
| `dashboard/README.md` | Quickstart |

### Dashboard Env Vars

Requires `OKX_API_KEY`, `OKX_SECRET`, `OKX_PASSPHRASE` in `.env`.
See [ENV.md](ENV.md) for full reference.

### Dashboard Cron

```
Schedule: 0 2 * * *  (daily 02:00)
User:     current shell user
Command:  bash /Users/d0m999/Desktop/vibe-trading/dashboard/cron_fetch.sh
```

Verify cron is installed:
```bash
crontab -l | grep dashboard
```

### Strategy Hyperopt Parameters (current best — auto-extracted from `user_data/strategies/LoopRSIStrategy.json`)

| Param | Value | Param | Value |
|-------|-------|-------|-------|
| `rsi_oversold` | 19 | `rsi_overbought` | 70 |
| `smoothing_length` | 50 | `median_length` | 100 |
| `trend_ema_period` | 174 | `risk_per_trade` | 0.03 |
| `bb_length` | 20 | `bb_mult` | 2.0 |
| `kc_length` | 20 | `kc_mult` | 1.2 |
| `ema_test_tolerance` | 0.005 | `sl_buffer` | 0.008 |
| `enable_smoothing` | true | `use_squeeze_filter` | false |
| `use_trend_filter` | false | | |
<!-- AUTO-GENERATED:END -->

<!-- AUTO-GENERATED:START (source: pyproject.toml) -->
### Python Dependencies (49 packages via uv)

| Group | Packages |
|-------|----------|
| Core | `freqtrade` (git stable), `numpy>=2.0`, `pandas==2.3.1` |
| Indicators | `ft-pandas-ta>=0.3.15`, `ta-lib==0.6.5` (via freqtrade), `technical==1.5.2` |
| Exchange | `ccxt>=4.5.37`, `cryptography>=45.0.0`, `aiohttp>=3.12.0` |
| Data | `pyarrow>=21.0.0`, `SQLAlchemy` (via freqtrade) |
| API | `fastapi`, `uvicorn`, `pydantic>=2.11.0` (all via freqtrade) |
| Notify | `python-telegram-bot` (via freqtrade) |
| Perf | `bottleneck>=1.5.0`, `numexpr>=2.11.0` |
| **Dashboard** ⭐ | `streamlit>=1.58.0`, `plotly>=6.7.0`, `python-dotenv>=1.2.2` |
| Util | `humanize`, `joblib`, `rich`, `orjson`, `pytz`, `schedule`, `websockets` |
<!-- AUTO-GENERATED:END -->
