<!-- Generated: 2026-06-08 | Files scanned: 96 | Token estimate: ~750 -->
# Dependencies Codemap

All deps managed via **uv** (migrated from pip, see `pyproject.toml` + `uv.lock`).
49 packages total. Python `>=3.11,<3.13`.

## Dependency Groups

```
pyproject.toml dependencies
│
├── [CORE] Freqtrade framework
│   └── freqtrade @ git+https://github.com/freqtrade/freqtrade.git@stable
│       (pulls: numpy, pandas, ccxt, SQLAlchemy, fastapi, uvicorn,
│        ta-lib, technical, pyjwt, python-telegram-bot, requests, ...)
│
├── [INDICATORS] Indicator libraries
│   └── ft-pandas-ta >= 0.3.15
│
├── [PERF] Performance accelerators
│   ├── bottleneck >= 1.5.0     (NumPy nan-aware C accelerations)
│   └── numexpr   >= 2.11.0     (fast array expression evaluator)
│
├── [NET] Networking
│   ├── aiohttp       >= 3.12.0
│   ├── cryptography  >= 45.0.0
│   ├── certifi       >= 2025.1.0
│   └── httpx         >= 0.24.1
│
├── [UTIL] Utilities
│   ├── humanize   >= 4.12.0
│   ├── joblib     >= 1.5.0
│   ├── rich       >= 14.0.0
│   ├── pyarrow    >= 21.0.0    (Feather I/O, non-armv7l)
│   ├── pydantic   >= 2.11.0
│   ├── orjson     >= 3.11.0    (fast JSON)
│   ├── pytz       >= 2025.1
│   ├── ast-comments >= 1.2.0
│   ├── packaging  >= 25.0
│   ├── psutil     >= 7.0.0
│   ├── setuptools >= 82.0.0
│   └── regex      >= 2024.4.16  (Unicode-aware, supports \p{Han})
│
├── [SCHED] Scheduling & WebSocket
│   ├── schedule   >= 1.2.0
│   ├── websockets >= 15.0.0
│   └── janus      >= 2.0.0      (thread/asyncio queue bridge)
│
├── [EXCHANGE] Exchange clients
│   └── ccxt           >= 4.5.37
│
├── [DASHBOARD] ⭐ NEW — Streamlit observability
│   ├── streamlit      >= 1.58.0
│   ├── plotly         >= 6.7.0
│   └── python-dotenv  >= 1.2.2
│
└── [DEV]
    └── (empty — no dev-dependencies declared)
```

## Where Each Dep Is Used

| Package | Used By | File Reference |
|---------|---------|----------------|
| `freqtrade` | Strategy runtime | `LoopRSIStrategy.py:12-19` |
| `numpy` | Hilbert transform | `LoopRSIStrategy.py:5` |
| `pandas` | DataFrame pipeline | `LoopRSIStrategy.py:6-7` |
| `talib` (via `talib.abstract`) | EMA, BBANDS, RSI, ADX, ATR, HMA | `LoopRSIStrategy.py:23` |
| `technical.qtpylib` | Cross helpers | `LoopRSIStrategy.py:24` |
| `pyarrow` | Feather I/O (OHLCV) | implicit via Freqtrade |
| `sqlalchemy` | tradesv3.sqlite ORM | implicit via Freqtrade |
| `fastapi` + `uvicorn` | API server (:8081) | implicit via Freqtrade |
| `streamlit` ⭐ | Dashboard UI | `dashboard/app.py:5` |
| `plotly.express` ⭐ | Pie/bar charts | `dashboard/app.py:9` |
| `plotly.graph_objects` ⭐ | PnL line chart | `dashboard/app.py:9` |
| `python-dotenv` ⭐ | OKX secrets | `dashboard/fetch_trades.py:10` |
| `ccxt` ⭐ | OKX read API | `dashboard/fetch_trades.py:5` |
| `regex` (with `\p{Han}`) | X tweet preprocessing | `.claude/skills/x-trader-analysis/` |
| `bottleneck`, `numexpr` | Freqtrade indicator speedup | implicit |

## External Services

| Service | Purpose | Auth |
|---------|---------|------|
| **Binance** | OHLCV market data + (dry-run) futures | API key in `user_data/config.json` |
| **OKX** ⭐ | Real trade sync (read-only) | API key/secret/passphrase in `.env` |
| **Telegram** ⭐ | Trade notifications (via Freqtrade) | Bot token in config |

## Local Resources (Not Python Deps)

```
TA-Lib C library   → brew install ta-lib (macOS system-level)
Docker             → freqtrade container (docker-compose.yml)
Cron               → dashboard/cron_fetch.sh (system crontab)
TradingView        → Manual research with PineScript/
```

## Dep Version Highlights

```toml
python              = ">=3.11,<3.13"   # Strict
freqtrade           = "stable branch"   # GitHub, not PyPI (stale since 2021)
streamlit           = ">=1.58.0"        # NEW
plotly              = ">=6.7.0"         # NEW
python-dotenv       = ">=1.2.2"         # NEW
ccxt                = ">=4.5.37"        # Bumped from 4.4.99 → 4.5.37
pyarrow             = ">=21.0.0"        # Major version bump
talib (via freqtrade) = "0.6.5"         # Bundled
```

## Stale-Dep Warnings

| Package | Last Bump | Note |
|---------|-----------|------|
| `freqtrade` | pre-2025 (PyPI) | Use stable git branch — Pin via `uv.lock` |
| `talib` | 0.6.5 | C library unchanged for years, low risk |
| `technical` | 1.5.2 | QTPyLib archive, no upstream activity |
| `python-telegram-bot` | 22.3 | Active, fine |
