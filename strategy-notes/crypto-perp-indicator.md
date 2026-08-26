# BTCUSDT 永续指标设计：第一性原理

> 标的：TradingView `BINANCE:BTCUSDT.P` / Binance USDⓈ-M `BTCUSDT` 永续
>
> 口径：单交易所、非聚合、UTC、已收盘数据
>
> 范围：只定义变量、量纲、因果边界和可证伪关系；不定义交易信号、阈值或权重。

## 1. 数据分类

| 类别 | 数据与单位 | TradingView | Binance 官方数据 | 严格含义与边界 |
|---|---|---|---|---|
| 市场状态 | 价格 `P`，USDT/BTC | `BINANCE:BTCUSDT.P` OHLC | [`/fapi/v1/klines`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#kline-candlestick-data) `[1..4]` | BTCUSDT 永续的成交价，不是现货指数或 Mark Price。 |
| 市场状态 | `OI_BTC`，BTC | `BINANCE:BTCUSDT.P_OI`，Non-aggregated | 当前值 `/fapi/v1/openInterest`；历史 [`/futures/data/openInterestHist`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest-statistics) 的 `sumOpenInterest` | 当前未平仓 BTC 数量。不是整数“张数”，也不包含开仓价分布。 |
| 派生状态 | `OI_USDT`，USDT | 可由 `P × OI_BTC` 估算 | `sumOpenInterestValue` | 当前名义敞口，不是保证金、净流入或独立于价格的新信息。 |
| 参照数据 | COIN-M OI，contracts | `BINANCE:BTCUSD.P_OI` | [`BTCUSD_PERP.openInterest`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data) | 反向合约，当前规格为 `100 USD/张`；与 BTCUSDT 不是同一合约，原值不得相加。 |
| 成交流量 | 总成交量，BTC / USDT | `Volume` | `/fapi/v1/klines` `[5]` / `[7]` | 已成交的周转量，不是仍未平仓的状态量。 |
| 成交流量 | 主动买入/卖出量，BTC | Volume Footprint、Volume Delta、CVD | `/fapi/v1/klines`：买入 `[9]`，卖出 `[5]-[9]`；或 [`/futures/data/takerlongshortRatio`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#taker-buy-sell-volume) | Binance 字段按 taker 方向分类；TradingView 按 intrabar 价格方向分类，是估算口径，不能视为原生 taker 数据。 |
| 杠杆事件 | 多头/空头清算量，BTC 或 USDT | Liquidations，Non-aggregated | [`!forceOrder@arr`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market) 后按 `BTCUSDT`、USDⓈ-M 过滤 | 已发生的强制平仓，不是未来清算热力图。流只推送每秒快照；公开全市场历史 REST 已停用，不能完整回补。 |
| 持仓成本 | Funding Rate，%/结算周期 | Funding Rate，Non-aggregated | [`/fapi/v1/fundingRate`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#get-funding-rate-history) 的 `fundingRate` | 正值为多头付空头，负值相反。Premium Index 是组成项，不是实际资金费率。 |
| 持仓代理 | 全体账户多空比，无量纲 | Long / Short Ratio Accounts | [`/futures/data/globalLongShortAccountRatio`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#long-short-ratio) | 统计净多/净空账户数，不按仓位大小加权。 |
| 持仓代理 | 大户账户比 / 仓位比，无量纲 | Top-trader ratios | `topLongShortAccountRatio` / `topLongShortPositionRatio` | 只描述交易所定义的大户子集；仓位比也不等于全市场“净多仓”。当前 Binance 文档要求 API key。 |

TradingView 的定义边界见 [Crypto Open Interest](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)、[Funding Rate](https://www.tradingview.com/support/solutions/43000762390-funding-rate-a-guide-to-market-sentiment/)、[Liquidations](https://www.tradingview.com/support/solutions/43000762400-liquidation-data-what-to-watch-and-why-it-matters/)、[Long / Short Ratio Accounts](https://www.tradingview.com/support/solutions/43000762399-long-short-ratio-accounts/)、[Volume Delta](https://www.tradingview.com/support/solutions/43000725057-volume-delta/) 和 [Volume Footprint](https://www.tradingview.com/support/solutions/43000726164-volume-footprint-charts-a-complete-guide/)。

## 2. 核心恒等式

### 2.1 一张合约同时有一多一空

```text
全市场多头合约量 = 全市场空头合约量 = OI
```

价格由边际成交如何穿透流动性决定，不是由“多头合约比空头合约多”决定。`OI` 增加表示新的配对风险被创建；`OI` 减少表示已有配对风险被消灭。仅看 `ΔOI` 不能知道主动方、开仓方或最终方向。

| 一笔成交中双方的仓位动作 | `ΔOI` |
|---|---:|
| 开仓 + 开仓 | 增加 |
| 平仓 + 平仓 | 减少 |
| 开仓 + 平仓 | 不变 |

### 2.2 BTC OI 与 USDT OI 不提供同一种信息

```text
OI_USDT ≈ P × OI_BTC
Δln(OI_USDT) ≈ Δln(P) + Δln(OI_BTC)
```

因此：

- 研究“持仓数量是否独立于价格变化”时，应使用 `OI_BTC`；
- 研究“当前经济敞口、杠杆冲击和清算规模”时，使用 `OI_USDT`；
- `P` 与 `OI_USDT` 的相关性包含机械价格项，不能全部解释为新增仓位；
- OI 是当前存量，不记录各交易者的开仓价。不同价格建立的仓位会汇总成同一个 OI 数值。

## 3. 价格 × OI 的最小解释

| 价格 | `OI_BTC` | 第一性原理下能说什么 | 不能直接断言什么 |
|---|---|---|---|
| 上涨 | 上升 | 未平仓风险扩张，边际成交价上移 | “净多头增加”或一定继续上涨 |
| 上涨 | 下降 | 未平仓风险收缩，表现与空头回补/去杠杆一致 | 所有下降都来自空头平仓 |
| 下跌 | 上升 | 未平仓风险扩张，边际成交价下移 | 所有新增仓位都是空头 |
| 下跌 | 下降 | 未平仓风险收缩，表现与多头止损/去杠杆一致 | 所有下降都来自多头清算 |

四种状态都只能写“与某机制一致”，不能写“证明某机制”。进一步区分必须结合：

- 主动买卖量：回答谁在穿透盘口，不能回答是在开仓还是平仓；
- Funding Rate：回答持仓成本和拥挤方向，不能单独预测下一步价格；
- 清算：回答哪一侧被强制平仓；清算常伴随 OI 下降，但并非数学恒等式；
- 多空比：回答特定账户集合的方向分布，不能打破“一多一空”的全市场恒等式。

## 4. CSV 与 Binance API 核对记录

### TradingView 与 Finance API 对齐汇总

本表中“数据来源”特指：TradingView 序列是否能够与对应 Finance API 的字段按相同标的、单位、UTC 时间桶和已收盘状态进行数值核对；它不只是记录数据由哪一方提供。

| 字段 | TradingView 数据 | Finance API 对照字段 | 对齐状态 | 当前证据 |
|---|---|---|---|---|
| `P` | `BINANCE:BTCUSDT.P` OHLC | Binance `/fapi/v1/klines` | 完全对齐 | 299/299 个已收盘 UTC 日完全相等；详见 4.2 |
| `Volume` | `BINANCE:BTCUSDT.P` Volume | Binance `/fapi/v1/klines` volume | 完全对齐 | 299/299 个已收盘 UTC 日完全相等；详见 4.2 |
| `OI_BTC` | `BINANCE:BTCUSDT.P_OI` | Binance `sumOpenInterest` | 近似对齐 | 31 个重合日桶，平均绝对误差 `0.0172%`，最大 `0.0520%`；详见 4.2 |
| `OI_USDT` | 该 ticker 未暴露独立 USDT 序列 | Binance `sumOpenInterestValue` | 不可直接对齐 | TradingView 侧只能用 `P × OI_BTC` 派生估算；乘积平均绝对误差 `0.0170%`；详见 4.2 |

其他指标尚未完成同口径的 TradingView/Finance API 数值核对，不应仅凭名称或理论含义标记为“已对齐”。

数据文件：[data/BINANCE_BTCUSDT.P, 1D_a715e.csv](<../data/BINANCE_BTCUSDT.P, 1D_a715e.csv>)。

### 4.1 CSV 字段归属

| CSV 列 | 实际数据 | 单位 | 是否属于主研究标的 |
|---|---|---|---|
| `1–6` | BTCUSDT 永续时间、价格 OHLC、Volume | UTC 日 / USDT/BTC / BTC | 是 |
| `7` | Volume MA | BTC | 派生值，不参与 API 原始字段核对 |
| `8–11` | EMA 1–4 | USDT/BTC | 派生值，不参与 API 原始字段核对 |
| `12–15` | `BINANCE:BTCUSDT.P_OI` OHLC | BTC | 是 |
| `16–19` | `BINANCE:BTCUSD.P_OI` OHLC | COIN-M contracts | 否，仅作参照 |

CSV 中两组序列都继承了“原生合约张数”标题，但第一组标题不准确：`BTCUSDT.P_OI` 是 BTC 数量，不是离散张数。

### 4.2 实测结果：CSV、Binance API 与 TradingView MCP

#### 4.2.1 CSV 与 Binance API 历史核对

价格与成交量使用 `BTCUSDT` 的 `/fapi/v1/klines?interval=1d`；OI 使用最近一个月 `period=5m` 的 `sumOpenInterest`，按 UTC 日近似重建 OHLC。`2026-08-26` 未收盘柱不计入统计。

| 数据 | 范围 | 结果 |
|---|---|---|
| 价格 O/H/L/C | 299 个已收盘 UTC 日 | `299/299` 完全相等，最大误差 `0 bps` |
| Volume（BTC） | 299 个已收盘 UTC 日 | `299/299` 完全相等，最大误差 `0 bps` |
| OI Open | 30 个完整 UTC 日 | 中位 `1.802 bps`，P95 `2.641 bps`，最大 `5.203 bps` |
| OI High | 30 个完整 UTC 日 | 中位 `2.611 bps`，P95 `17.805 bps`，最大 `36.371 bps` |
| OI Low | 30 个完整 UTC 日 | 中位 `1.404 bps`，P95 `7.999 bps`，最大 `36.599 bps` |
| OI Close | 30 个完整 UTC 日 | 中位 `1.811 bps`，P95 `2.061 bps`，最大 `3.445 bps` |

补充结果：日度 OI 收盘变化方向 `29/29` 一致，变化量相关系数 `0.999993254`；CSV 的 Open/Close 平均分别高约 `18.392 BTC` / `19.474 BTC`，约为总 OI 的 `0.02%`。

判定：

- TradingView 价格和 BTC 成交量与 Binance API 完全对齐；
- `BTCUSDT.P_OI` 与 Binance BTC 数量口径、UTC 时序和变化高度对齐，但不是逐点完全相等；
- OI High/Low 误差更大，与 Binance 历史接口仅提供 5 分钟快照、可能漏掉区间内极值一致；
- 该结果不能证明 TradingView 与 Binance 使用相同的内部采样、回填和 OHLC 聚合管线。

完整方法与原始统计见 [核对报告](../docs/btcusdt-binance-api-csv-alignment-2026-08-26.md)。

本轮 CSV 数值核对只覆盖价格、Volume 和 `OI_BTC`。Funding、主动买卖量、清算和多空比尚未包含在该 CSV 中，也未计入上述“对得上”的判定。

#### 4.2.2 TradingView MCP 直接实测：`OI_USDT` 的来源边界

2026-08-26 使用 TradingView MCP 直接读取：

- `BINANCE:BTCUSDT.P_OI` 的 `1D` OHLC；
- 同时间桶 `BINANCE:BTCUSDT.P` 的 `1D` OHLC；
- Binance `/futures/data/openInterestHist?symbol=BTCUSDT&period=1d` 的 `sumOpenInterest` 与 `sumOpenInterestValue`。

TradingView 返回 100 个日桶，Binance 当前接口返回 31 个可用历史点；31 个 UTC 时间戳全部重合。以日桶开盘点比较：

| 比较 | 平均绝对误差 | 最大绝对误差 |
|---|---:|---:|
| TV `OI` Open vs Binance `sumOpenInterest` | `0.0172%` | `0.0520%` |
| TV 价格 Open vs `sumOpenInterestValue / sumOpenInterest` | `0.0015%` | `0.0106%` |
| TV 价格 Open × TV `OI` Open vs Binance `sumOpenInterestValue` | `0.0170%` | `0.0520%` |

判定：

- 对 `BINANCE:BTCUSDT.P_OI` 这个确切 ticker，TradingView 输出的是 BTC 数量口径的 OI，实测与 Binance `sumOpenInterest` 高度对齐；它不是约 80 亿 USDT 量级的 `sumOpenInterestValue`。
- TradingView 没有在该 ticker 上暴露独立的 USDT OI 序列，也没有公开“后台直接读取 `sumOpenInterestValue`”的证据。`P × OI_BTC` 之所以能复现 Binance 名义价值，是因为价格和 BTC 数量分别对齐，乘积自然接近。
- 因此在 TradingView/Pine 内构造的 `OI_USDT = P × OI_BTC` 必须标为“派生估算值”；若要求 Binance 原生值，应使用 Binance API 的 `sumOpenInterestValue`。两者不能在文档中写成同一个数据源。
- 该实测证明的是输出量纲和数值关系，不证明 TradingView 未公开的内部采样、回填或计算管线。Binance 历史接口每个周期只返回一个点，不能据此把 TV 的 OI OHLC 当作 Binance 原生 OI OHLC。

## 5. 指标设计约束

1. 主状态量固定为 `P` 与 `OI_BTC`；`OI_USDT` 只表示名义风险，不用于证明价格与 OI 的独立关系。
2. 所有数据固定到 Binance `BTCUSDT` USDⓈ-M 永续；不得混入 `BTCUSD_PERP`、季度合约或 Aggregated 数据。
3. 同一比较必须使用相同 UTC 时间桶和已收盘柱；实时柱单列。
4. OI 缺失是 `NA`，不是零；不同单位的 OI 不直接相加。
5. 主动流、Funding、清算和多空比是解释变量，不是 OI 的替代品，也不单独构成因果证明。
6. TradingView Footprint/Delta 与 Binance 原生 taker 字段分开命名；Premium Index 与实际 Funding Rate 分开命名。
