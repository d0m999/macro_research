# Frontend Codemap — PineScript / TradingView Indicators

> Freshness: 2026-02-11 | Auto-generated

## Overview

24 PineScript indicators (~8,400 LOC) organized into 6 categories.
Used for **research & visual analysis** on TradingView; strategy execution is in Python.

```
PineScript/
├── _L∞p/              # Core Loop brand indicators
├── Oscillator/        # Momentum & cycle oscillators
├── Price_Zones/       # Support/Resistance & structure
├── Vol/               # Volume analysis
├── Open Interest/     # Multi-exchange OI tracking
└── (root)             # ML classification, simple OI
```

---

## _L∞p/ — Core Indicators

| File | LOC | Purpose |
|------|-----|---------|
| `L∞p \| RSI.pine` | ~150 | Base adaptive RSI with Hilbert period |
| `L∞p \| RSI-monitor.pine` | ~200 | RSI dashboard v1 |
| `L∞p \| RSI-monitor-v2.pine` | ~250 | RSI dashboard v2 (multi-TF) |
| `L∞p \| MA.pine` | ~120 | Moving average suite (EMA/SMA/HMA/WMA) |
| `L∞p \| ATR-zigzag.pine` | ~180 | ATR-based zigzag with S/R levels |

**Relationship to Python:** `L∞p | RSI` is the PineScript prototype of `LoopRSIStrategy.py`'s Hilbert + adaptive RSI logic.

---

## Oscillator/ — Momentum Indicators

| File | LOC | Purpose |
|------|-----|---------|
| `ARO-GARCH.pine` | 361 | Adaptive Resonance + GARCH volatility model |
| `ARO-Fourier.pine` | 285 | ARO with Fourier spectral decomposition |
| `ARO-RMA-ATR-define.pine` | 285 | ARO with RMA smoothing + ATR bands |
| `detrended-rhythm-oscillator.pine` | 193 | Trend-removed cycle oscillator |
| `TDI Sq.pine` | 178 | Trader's Dynamic Index + Squeeze detection |
| `1090 tester.pine` | 201 | Custom 10/90 level testing indicator |

**ARO family** shares core pattern: Hilbert → period → adaptive oscillator.
Variants differ in volatility model (GARCH vs Fourier vs RMA).

---

## Price_Zones/ — Structure Indicators

| File | LOC | Purpose |
|------|-----|---------|
| `Smart Money Concepts.pine` | 845 | SMC: order blocks, FVG, liquidity sweeps |
| `Price zones.pine` | 422 | Multi-TF price zone identification |
| `RS zones.pine` | 116 | Simple resistance/support zones |
| `SRchannel.pine` | 192 | Dynamic S/R channel bands |
| `Previous-HL.pine` | 122 | Previous session high/low levels |
| `ATR.pine` | 94 | ATR-based volatility bands |

**Smart Money Concepts** is the largest single indicator — provides institutional-level structure analysis.

---

## Vol/ — Volume Analysis

| File | LOC | Purpose |
|------|-----|---------|
| `high-vol-boxes.pine` | 239 | High volume candle detection with visual boxes |
| `Vol-by-time.pine` | 67 | Volume distribution by time-of-day |

---

## Open Interest/ — Derivatives Data

| File | LOC | Purpose |
|------|-----|---------|
| `L∞p \| Open-Interest.pine` | 305 | Loop OI tracker (multi-exchange) |
| `integrated-OI-with-analysis.pine` | 257 | OI + funding rate + crowding analysis |
| `integrated-OI.pine` | 55 | Simple OI aggregation |
| `simple_total_oi.pine` | 11 | Minimal OI sum (root dir) |

**Supported exchanges:** Binance, Bybit, Bitget, Coinbase, OKX, CME
**Features:** USDT/USDC margin conversion, funding rate thresholds, long/short crowding detection

---

## Machine Learning

| File | LOC | Purpose |
|------|-----|---------|
| `Machine Learning: Lorentzian Classification.pine` | 562 | ML-based signal classification using Lorentzian distance |

---

## Pine → Python Conversion Map

| PineScript Source | Python Target | Status |
|-------------------|---------------|--------|
| `L∞p \| RSI` (Hilbert + RSI) | `LoopRSIStrategy.hilbert_transform_period()` | Converted |
| ARO family | `adaptive_resonance.py` | Converted |
| ATR-zigzag | `atr_zigzag.py` | Converted |
| Smart Money Concepts | — | Not converted |
| Open Interest suite | — | Not converted |
| Lorentzian ML | — | Not converted |
