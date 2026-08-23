# TradingView 官方加密货币 Open Interest 数据覆盖与聚合口径

> 截至日：2026-08-22｜检索日期：2026-08-22｜范围：TradingView 内置 `Open Interest` / `Crypto Open Interest` 及官方 Pine 数据接口

## 结论先行

- TradingView 官方 `Open Interest` 帮助页当前列出的加密衍生品交易所为：**BINANCE、BITGET、BITMEX、BYBIT、COINBASE、DERIBIT、KRAKEN、HTX、OKX**。
- `Crypto Open Interest` 有两种显示方式：`Aggregated` 是该资产在**所有可用交易所**上的 OI 聚合；`Non-aggregated` 是单一交易所/合约的 OI。现货市场只显示聚合数据，币种 Symbol page 也只显示聚合数据。
- BitMEX 可作为单一交易所数据使用，但 TradingView 的官方 OI 页面镜像明确标注 **BitMEX 不支持 aggregated data**，因此不能默认把 BitMEX 加进币种级聚合值。
- TradingView 没有在公开帮助页披露跨交易所 OI 聚合的完整工程公式：包括合约单位换算、价格取值、合约筛选、时间戳对齐和缺失值处理。能够确认的是“跨所有可用交易所的总量/总价值”语义，而不是资金费率那种公开说明的 OI 加权平均。

## 官方证据

### 1. 交易所清单

- [Open Interest — TradingView Help Center](https://www.tradingview.com/support/solutions/43000685269-open-interest/)：说明 OI 是尚未结算的衍生品未平仓合约总数，并列出 crypto derivatives 的九家交易所；同时说明 crypto OI 支持分钟级盘中数据。
- [Understanding crypto open interest — TradingView Help Center](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)：说明入口为 `Indicators → Fundamentals → Derivatives → Crypto open interest`，并定义 `Aggregated` / `Non-aggregated`。
- [Crypto Open Interest — TradingView 日本官方镜像](https://jp.tradingview.com/support/solutions/43000762388/)：同一 OI 文章明确列出九家交易所，并在 BitMEX 后注明“集計データは非対応です”（不支持聚合数据）。英文页面相应列表的段落标题目前写成了 `Liquidations data`，与文章主题不一致，因此 BitMEX 例外采用官方镜像和页面语义交叉核验。

### 2. 聚合与显示单位

- 英文 OI 帮助页明确：`Aggregated` 显示资产在所有可用交易所的 OI；`Non-aggregated` 显示单一交易所的 OI；非聚合值可能以 base currency、quote currency 或 contracts 表示。
- [Bitcoin Derivatives — TradingView](https://www.tradingview.com/symbols/BTCUSD/derivatives/) 将币种级 OI 描述为“交易所上未平仓衍生品头寸的总价值”，并提供历史趋势与交易所拆分。这支持“总量/总价值型跨市场聚合”的解释，但没有给出重现该数值所需的完整公式。
- [New crypto derivatives indicators, now on TradingView](https://www.tradingview.com/blog/en/crypto-derivatives-indicators-on-tradingview-53558/) 说明 OI 依交易所和合约可按 contracts、base currency 或 quote currency 展示。

### 3. 单合约数据与币种聚合的区别

- [TradingView 官方 `Request` Pine library](https://www.tradingview.com/script/Rpmobpw5-Request/) 说明 `openInterestCrypto()` 请求指定加密货币合约的 OI，并以 `<symbol>_OI` 构造 OI ticker；官方示例为 `BINANCE:BTCUSDT.P`。因此 Pine 中按合约请求的 OI 不应被当作币种级跨交易所聚合序列。

## 计算口径与可复现边界

可以把币种级聚合的概念写成：

```text
Aggregated OI(asset, t)
  ≈ Σ exchange Σ contract normalized_OI(exchange, contract, t)
```

这里的“先统一单位再合计”是基于 TradingView 对“总价值”和不同原生单位的说明作出的合理推断，不是 TradingView 公布的逐步算法。不能仅凭公开帮助页确认：

- contracts 如何按 contract multiplier 换算为 base/quote value；
- 使用哪一个价格（mark、index、last 或其他）进行计价；
- 到期 futures、perpetual、inverse/linear 合约的纳入范围；
- 不同交易所更新时间不一致时如何对齐；
- 单个交易所或合约缺数时是剔除、沿用还是记零。

因此，研究或 Pine 复现时应将 TradingView 聚合线视为 TradingView 自己的数据产品；若需要可审计的精确聚合，应分别读取各交易所原生 OI，明确单位和合约乘数后自行统一并求和。

## 不应混淆的范围

- `CME` 等交易所出现在 TradingView 的传统 futures OI 分类中，不等于被纳入上述九家 crypto derivatives 的币种级聚合清单。
- 清单是官方公开的交易所级覆盖范围，不保证每一家对每一种币、每个合约或每个时间周期都有数据；实际聚合只会使用当时“可用”的数据。
- 官方 2025 年公告先后说明 Bybit、Binance、OKX，以及 Bitget、HTX、Kraken、Deribit、BitMEX、Coinbase 的 crypto derivatives 指标加入 TradingView：[第一阶段公告](https://www.tradingview.com/blog/en/crypto-derivatives-indicators-on-tradingview-53558/)、[扩展覆盖公告](https://www.tradingview.com/blog/en/indicators-for-bitget-htx-kraken-deribit-bitmex-coinbase-derivatives-53708/)。
