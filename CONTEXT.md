# TradingView Open Interest Research

> **范围声明**：本文件的术语表只服务于 **TradingView / PineScript / OI 研究线**（本仓库当前处于休眠状态）。
> 它不是仓库的全局词汇表——KOL 语料蒸馏线与基本面研究线各有自己的术语来源，
> 见 `docs/agents/domain.md`。涉及那两条线时不要从这里取词。

本上下文统一 TradingView OI 研究中的数据范围和单位语言，避免把单一合约、单一交易所与聚合市场口径混为一谈。

## Language

**Binance BTCUSD COIN-M 永续 OI（合约张数）**:
Binance BTCUSD COIN-M 永续合约中尚未平仓的原生合约数量。它只覆盖该永续合约，不代表 Binance 全部 BTC OI 或跨交易所 BTC OI。
_Avoid_: Binance BTC 总 OI、BTC 聚合 OI、全市场 BTC OI

**TradingView OI 服务符号**:
TradingView 为特定交易所衍生品提供的 OI 时间序列标识；其范围与单位取决于对应合约。`BINANCE:BTCUSD.P_OI` 对应 Binance BTCUSD COIN-M 永续 OI（合约张数）。
_Avoid_: 价格符号、交易所原生 API、聚合 OI

**实时 OI 柱**:
当前尚未结束的图表周期内持续变化的 OI 观测；其 OHLC 在周期结束前不是最终值。
_Avoid_: 已确认 OI、收线 OI

**OI OHLC 蜡烛**:
一个图表周期内 OI 的起始值、最高值、最低值和结束值所组成的蜡烛。它描述 OI 自身在该周期内的变化，不表达价格方向或多空方向。
_Avoid_: 价格蜡烛、多空蜡烛、净多头蜡烛

**OI 数据缺口**:
某个图表周期没有可用 OI 观测的状态。数据缺口不等于 OI 为零，也不等于上一周期的 OI。
_Avoid_: 零 OI、沿用 OI、已填充 OI
