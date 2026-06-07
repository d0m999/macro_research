<!-- Generated: 2026-06-08 | Files scanned: 96 | Token estimate: ~800 -->
# Frontend Codemap — PineScript & Streamlit Dashboard

Two distinct "frontends":

1. **PineScript/** — TradingView research indicators (24 .pine files)
2. **dashboard/app.py** — Streamlit observability UI

---

## PineScript — Research Indicators (24 files, ~8,400 LOC)

Used for **research & visual analysis** on TradingView. Strategy execution is in Python.

```
PineScript/
├── _L∞p/              # Core Loop brand indicators
├── Oscillator/        # Momentum & cycle oscillators
├── Price_Zones/       # Support/Resistance & structure
├── Vol/               # Volume analysis
├── Open Interest/     # Multi-exchange OI tracking
├── Zigzag/            # Zigzag pattern detection
└── (root)             # ML classification, simple OI
```

### _L∞p/ — Core Indicators

| File | LOC | Purpose |
|------|-----|---------|
| `L∞p \| RSI.pine` | ~150 | Base adaptive RSI with Hilbert period |
| `L∞p \| RSI-monitor.pine` | ~200 | RSI dashboard v1 |
| `L∞p \| RSI-monitor-v2.pine` | ~250 | RSI dashboard v2 (multi-TF) |
| `L∞p \| MA.pine` | ~120 | Moving average suite (EMA/SMA/HMA/WMA) |
| `L∞p \| ATR-zigzag.pine` | ~180 | ATR-based zigzag with S/R levels |

**Relationship to Python:** `L∞p | RSI` is the PineScript prototype of
`LoopRSIStrategy.py`'s Hilbert + adaptive RSI logic.

### Oscillator/ — Momentum Indicators

| File | LOC | Purpose |
|------|-----|---------|
| `ARO-GARCH.pine` | 361 | Adaptive Resonance + GARCH volatility |
| `ARO-Fourier.pine` | 285 | ARO with Fourier spectral decomposition |
| `ARO-RMA-ATR-define.pine` | 285 | ARO with RMA smoothing + ATR bands |
| `detrended-rhythm-oscillator.pine` | 193 | Trend-removed cycle oscillator |
| `TDI Sq.pine` | 178 | Trader's Dynamic Index + Squeeze |
| `1090 tester.pine` | 201 | 10/90 level testing |

**ARO family** shares: Hilbert → period → adaptive oscillator.
Variants differ in volatility model (GARCH vs Fourier vs RMA).

### Price_Zones/ — Structure Indicators

| File | LOC | Purpose |
|------|-----|---------|
| `Smart Money Concepts.pine` | 845 | SMC: order blocks, FVG, liquidity sweeps |
| `Price zones.pine` | 422 | Multi-TF price zone identification |
| `RS zones.pine` | 116 | Resistance/support zones |
| `SRchannel.pine` | 192 | Dynamic S/R channel bands |
| `Previous-HL.pine` | 122 | Previous session H/L levels |
| `ATR.pine` | 94 | ATR-based volatility bands |

**Smart Money Concepts** is the largest — institutional-level structure analysis.

### Vol/ — Volume Analysis

| File | LOC | Purpose |
|------|-----|---------|
| `high-vol-boxes.pine` | 239 | High-volume candle boxes |
| `Vol-by-time.pine` | 67 | Volume distribution by time-of-day |

### Open Interest/ — Derivatives

| File | LOC | Purpose |
|------|-----|---------|
| `L∞p \| Open-Interest.pine` | 305 | Loop OI tracker (multi-exchange) |
| `integrated-OI-with-analysis.pine` | 257 | OI + funding rate + crowding |
| `integrated-OI.pine` | 55 | Simple OI aggregation |
| `simple_total_oi.pine` | 11 | Minimal OI sum |

**Supported exchanges:** Binance, Bybit, Bitget, Coinbase, OKX, CME

### Machine Learning

| File | LOC | Purpose |
|------|-----|---------|
| `Machine Learning: Lorentzian Classification.pine` | 562 | ML classification via Lorentzian distance |

### Pine → Python Conversion Map

| PineScript Source | Python Target | Status |
|-------------------|---------------|--------|
| `L∞p \| RSI` (Hilbert + RSI) | `LoopRSIStrategy.hilbert_transform_period()` | Converted |
| ARO family | `adaptive_resonance.py` | Converted |
| ATR-zigzag | `atr_zigzag.py` | Converted |
| Smart Money Concepts | — | Not converted |
| Open Interest suite | — | Not converted |
| Lorentzian ML | — | Not converted |

---

## Dashboard (Streamlit) — NEW

### Component Hierarchy

```
Streamlit Page (app.py @ :8501)
├── Page Config (title, icon, layout="wide")
├── Title + Caption
│
├── Section 1: 总览 (Overview)
│   ├── col1: st.metric — 总交易笔数
│   ├── col2: st.metric — 胜率 (%)
│   ├── col3: st.metric — 净盈亏 (USDT, color-coded)
│   ├── col4: st.metric — 总手续费
│   └── col5: st.metric — 最大连续亏损
│
├── Section 2: 当前持仓 (Current Positions)
│   └── st.dataframe (symbol, side, contracts, entry, unrealized, ts)
│
├── Section 3: 账户余额 (Account Balance)
│   └── px.pie(values=total, names=currency) — 资产分布
│
├── Section 4: 收益曲线 (PnL Curve)
│   └── go.Figure(go.Scatter) — cumulative PnL line
│
├── Section 5: 按币种统计 (Per-Symbol)
│   ├── px.bar(x=symbol, y=net_pnl) — 各币种净盈亏
│   └── px.pie(values=trade_count) — 各币种交易笔数占比
│
└── Section 6: 按方向统计 (Per-Side)
    ├── st.dataframe — multi/sell stats
    └── px.bar — 多空收益对比
```

### State Management

- **No persistent state** beyond `@st.cache_data(ttl=60)` for DB reads
- All data is pull-based from `dashboard/trades.db`
- No user input forms, no session state, no auth

### Rendering Pipeline

```
cron @ 02:00 → fetch_trades.py writes trades.db
                              ↓
User opens :8501 → app.py loads cached → renders sections
                              ↓
60s TTL cache expires → re-read from trades.db
```

### Chart Types

| Chart | Library | Purpose |
|-------|---------|---------|
| `px.pie` | plotly.express | Asset distribution, symbol share |
| `px.bar` | plotly.express | Per-symbol/per-side PnL |
| `go.Scatter` | plotly.graph_objects | Cumulative PnL line |
| `st.metric` | streamlit | KPI cards (5 columns) |
| `st.dataframe` | streamlit | Tabular data (positions, stats) |
