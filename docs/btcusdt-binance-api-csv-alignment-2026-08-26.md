# Binance BTCUSDT USDⓈ-M 官方 API 与 CSV 对齐边界

研究日期：2026-08-26

## 范围与结论

本文只研究 Binance 官方 USDⓈ-M `BTCUSDT` 永续合约市场数据接口，并与 `data/BINANCE_BTCUSDT.P, 1D_a715e.csv` 比较。比较只使用 CSV 的主图 OHLCV 和第一组 `BTCUSDT.P_OI`；第二组百万级 `BTCUSD.P_OI`、`BTCUSD_PERP`、COIN-M 和连续合约接口均排除。

结论如下：

1. 价格与成交量日线可以用 `/fapi/v1/klines?symbol=BTCUSDT&interval=1d` 重取。返回数组的第 `0` 项是开盘时间，第 `5` 项是成交量，第 `6` 项是收盘时间，第 `7` 项是计价资产成交量。官方 API 返回可验证 `1d` 边界为每日 `00:00:00.000 UTC` 至 `23:59:59.999 UTC`。
2. `/futures/data/openInterestHist` 支持 `1d`，但每个周期只返回一个 OI 统计快照，不返回 OI 的 `open/high/low/close`。
3. 官方 OI 历史接口最多只提供最近 `1 month`，单次 `limit` 最大 `500`。因此它不能直接、完整重建较长历史窗口中的 TradingView `BINANCE:BTCUSDT.P_OI` 日线 OHLC。
4. 最近一个月内可用 `period=5m` 快照聚合出近似日线 OI OHLC，但这不是 TradingView 日线 OI 的精确重建：5 分钟之间的极值可能丢失，而且 Binance 文档没有声明 TradingView 的采样和聚合方法。
5. 本次实测中，CSV 的 299 根已收盘 BTCUSDT 日线价格 OHLC 和 `Volume` 与 Binance Kline API 全部精确相等；最近 30 个完整 UTC 日的 OI 开盘、收盘通常相差约 `1.8 bps`，日度收盘变化方向 `29/29` 一致，说明标的、单位和时序高度吻合，但不能称为逐点完全相等。

官方来源：

- [Binance USDⓈ-M Kline/Candlestick Data](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#kline-candlestick-data)
- [Binance USDⓈ-M Open Interest Statistics](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest-statistics)
- [Binance USDⓈ-M Market Data API 总表](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data)

## 实测对齐结果

### 比较范围

CSV 共 300 根日线，日期为 `2025-10-31` 至 `2026-08-26`。执行比较时，`2026-08-26` 尚未收盘，因此正式统计只包括已经收盘的数据：

- 价格 OHLC 和 `Volume`：`2025-10-31` 至 `2026-08-25`，共 299 天；
- OI OHLC：受 Binance 官方最近一个月历史限制，使用 `2026-07-27 00:00 UTC` 至 `2026-08-26 00:00 UTC` 的 8,641 个连续 5 分钟边界样本，重建 `2026-07-27` 至 `2026-08-25` 共 30 个完整 UTC 日；
- CSV 第 12--15 列作为 `BTCUSDT.P_OI`；第 16--19 列属于另一标的，未参与任何比较；
- `Volume MA` 和四条 EMA 是 TradingView 派生指标，不是 Binance API 原始字段，未纳入 API 一致性判定。

### BTCUSDT 价格和成交量

使用：

```text
GET /fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=500
```

按 UTC 开盘日期对齐后：

| 字段 | 完全相等 | 最大绝对误差 | 最大相对误差 |
|---|---:|---:|---:|
| Open | 299 / 299 | 0 | 0 bps |
| High | 299 / 299 | 0 | 0 bps |
| Low | 299 / 299 | 0 | 0 bps |
| Close | 299 / 299 | 0 | 0 bps |
| Volume（BTC） | 299 / 299 | 0 | 0 bps |

这也反向确认 CSV 日期与 Binance BTCUSDT 永续的 UTC 日线边界一致。当前未收盘的 `2026-08-26` 柱没有计入通过率；在不同抓取时刻比较时，其 close、volume 和 OI 继续变化属于正常现象。

### BTCUSDT OI

Binance 日周期 OI 接口只给单点，不能直接比较 OHLC。因此，本次把官方 `period=5m` 的 `sumOpenInterest` 边界样本按 UTC 日近似聚合：日界线首值为 open、最大值为 high、最小值为 low、次日日界线值为 close。8,641 个样本时间间隔全部为 5 分钟，无 API 序列缺口。

误差公式：

```text
error_bps = abs(TradingView - Binance近似值) / Binance近似值 × 10,000
```

| OI 字段 | 比较天数 | 中位误差 | P95 误差 | 最大误差 |
|---|---:|---:|---:|---:|
| Open | 30 | 1.801844 bps | 2.641334 bps | 5.203298 bps |
| High | 30 | 2.611365 bps | 17.805207 bps | 36.370700 bps |
| Low | 30 | 1.403547 bps | 7.998594 bps | 36.598617 bps |
| Close | 30 | 1.810668 bps | 2.061011 bps | 3.444733 bps |

补充一致性指标：

- 30 天 close-to-close 产生 29 个日变化，方向 `29/29` 全部一致；
- 两组日度 OI 收盘变化的 Pearson 相关系数为 `0.999993254`；
- CSV open 和 close 相对 5 分钟 API 边界样本平均分别高约 `18.392 BTC` 和 `19.474 BTC`，相对于约 10 万 BTC 的 OI 是约 `0.02%` 量级；
- High/Low 的尾部误差大于 Open/Close，方向上也符合 5 分钟快照可能漏掉分钟内极值的预期：TradingView high 往往更高，low 往往更低。

### 判定

- **价格和成交量：完全对得上。** 299 根已收盘日线逐项零误差。
- **OI：高度对得上，但不是逐点完全相等。** 数量级、UTC 时序、日变化方向和变化幅度均强一致；开盘和收盘误差约万分之二。High/Low 最大约 `0.366%` 的差异可以由官方历史 OI 最细只有 5 分钟采样、而 TradingView 可能捕获更细粒度极值解释。
- 这些结果支持 CSV 第一组 OI 是同一 `BTCUSDT` USDⓈ-M 永续的 BTC 数量口径；它们不构成 TradingView 与 Binance 内部数据管线逐笔完全相同的证明。

## 1. `/fapi/v1/klines`：BTCUSDT 永续日线

请求：

```text
GET https://fapi.binance.com/fapi/v1/klines
```

本研究固定参数：

```text
symbol=BTCUSDT
interval=1d
```

不要改用 `continuousKlines`，因为本任务要求与 TradingView 的 Binance `BTCUSDT` 永续标的保持一致，而不是构造一个按合约类型连续拼接的序列。

### 返回字段

官方文档规定每根 Kline 是固定长度为 12 的数组；Kline 由开盘时间唯一标识：

| 下标 | 官方字段 | 对 BTCUSDT 的对齐含义 |
|---:|---|---|
| `0` | Open time | 日线开盘时间，Unix 毫秒 |
| `1` | Open | 开盘价 |
| `2` | High | 最高价 |
| `3` | Low | 最低价 |
| `4` | Close | 收盘价；当前未收线日会继续变化 |
| `5` | Volume | 成交量；对 BTCUSDT 按 BTC 数量量级读取 |
| `6` | Close time | 日线收盘时间，Unix 毫秒 |
| `7` | Quote asset volume | 计价资产成交量；BTCUSDT 的计价资产是 USDT |
| `8` | Number of trades | 成交笔数 |
| `9` | Taker buy base asset volume | 主动买入的基础资产成交量 |
| `10` | Taker buy quote asset volume | 主动买入的计价资产成交量 |
| `11` | Ignore | 忽略 |

文档对第 `5` 项只写 `Volume`，对第 `7` 项明确写 `Quote asset volume`。官方 `exchangeInfo` 又把 `BTCUSDT` 定义为 `baseAsset=BTC`、`quoteAsset=USDT`、`contractType=PERPETUAL`。因此，在本标的上应把第 `5` 项与 BTC 数量量级比较，把第 `7` 项与 USDT 成交额量级比较。这一单位展开来自同一官方 API 的标的元数据和字段关系，而不是 Kline 页面对第 `5` 项的额外文字承诺。

- [官方 `BTCUSDT` 日线 API 示例](https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=3)
- [官方 USDⓈ-M `exchangeInfo`](https://fapi.binance.com/fapi/v1/exchangeInfo)

### 日线时间边界

官方文档说明 Kline 由 `open time` 唯一标识，并同时返回 `close time`。对官方 API 的 `interval=1d` 返回值进行毫秒时间转换，可验证日线边界是 UTC 自然日：

```text
openTime  = 2026-08-25T00:00:00.000Z = 1787616000000
closeTime = 2026-08-25T23:59:59.999Z = 1787702399999
```

因此，对齐 CSV 时必须先确认 CSV 的 `time`/日期采用 UTC、交易所时区还是本地显示时区，不能仅凭界面显示的日期字符串假定它已经是 UTC。当前 UTC 日尚未结束时，API 最后一根 `1d` Kline 是未收线柱，应与同一抓取时刻的 CSV 当前柱比较，或从历史对齐中排除。

### 可复现 curl

取最近三根 BTCUSDT 永续日线：

```bash
curl -sS 'https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=3' | jq .
```

固定请求 2026-08-25 UTC 日线：

```bash
curl -sS 'https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&startTime=1787616000000&endTime=1787702399999&limit=1' | jq '.[0]'
```

只抽取对齐所需字段：

```bash
curl -sS 'https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=3' \
  | jq 'map({openTime: .[0], open: .[1], high: .[2], low: .[3], close: .[4], volume: .[5], closeTime: .[6], quoteVolume: .[7]})'
```

补充限制：`limit` 默认 `500`、最大 `1500`；未传 `startTime` 和 `endTime` 时返回最近的 Kline。详见 [官方 Kline 文档](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#kline-candlestick-data)。

## 2. `/futures/data/openInterestHist`：OI 历史统计

请求：

```text
GET https://fapi.binance.com/futures/data/openInterestHist
```

固定标的参数：

```text
symbol=BTCUSDT
```

### 参数与覆盖范围

官方文档列出的 `period` 枚举为：

```text
5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d
```

其他限制：

- `period` 必填。
- `limit` 默认 `30`，最大 `500`。
- `startTime`、`endTime` 可选，单位为 Unix 毫秒。
- 两个时间参数均不提供时返回最近数据。
- 官方明确限制为仅能取得最近 `1 month` 的数据；这个历史保留限制不会因为把 `limit` 设为 `500` 而扩大。
- 文档将返回的 `timestamp` 定义为该 period 的结束时间，单位为毫秒。

来源：[官方 Open Interest Statistics 文档](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest-statistics)。

### 返回字段语义与单位边界

| 字段 | 官方文档语义 | BTCUSDT 对齐解释 |
|---|---|---|
| `symbol` | 标的 | 必须为 `BTCUSDT` |
| `sumOpenInterest` | `total open interest` | OI 总量；对 BTCUSDT 呈 BTC 数量量级 |
| `sumOpenInterestValue` | `total open interest value` | OI 总价值；对 BTCUSDT 呈 USDT 名义价值量级 |
| `CMCCirculatingSupply` | CMC 提供的流通量 | 与 OI OHLC 对齐无直接关系 |
| `timestamp` | period 的结束时间 | Unix 毫秒；用于按 UTC 边界分组 |

必须保留一个文档边界：官方字段说明只写“总 OI”和“总 OI 价值”，并没有在该页面把 `sumOpenInterest` 的单位逐字规定为 `BTC` 或“合约张数”。对 BTCUSDT 可通过两个官方事实作操作性判断：

1. `exchangeInfo` 定义其基础资产为 BTC、计价资产为 USDT；
2. 同一条官方 OI 返回中，`sumOpenInterestValue / sumOpenInterest` 与 BTCUSDT 价格处于同一量级。

因此，做 BTCUSDT 数据对齐时，可以把 `sumOpenInterest` 按 BTC 数量量级、`sumOpenInterestValue` 按 USDT 名义价值量级比较，但应把这一点标为官方字段与实时返回关系的推断，不能声称 Open Interest Statistics 页面明确写了单位。

- [官方 BTCUSDT `period=1d` OI 返回](https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=1d&limit=3)
- [官方 BTCUSDT 当前 OI](https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT)
- [官方 USDⓈ-M `exchangeInfo`](https://fapi.binance.com/fapi/v1/exchangeInfo)

### 可复现 curl

取最近 30 个日周期 OI 统计点：

```bash
curl -sS 'https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=1d&limit=30' | jq .
```

取最近 500 个 5 分钟 OI 统计点：

```bash
curl -sS 'https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&limit=500' | jq .
```

固定请求 2026-08-24 UTC 一天及下一日 `00:00` 边界的 5 分钟样本；一天有 288 个 5 分钟区间，连同起止边界最多需要 289 个快照点，不超过单次上限 500：

```bash
curl -sS 'https://fapi.binance.com/futures/data/openInterestHist?symbol=BTCUSDT&period=5m&startTime=1787529600000&endTime=1787616000000&limit=500' | jq .
```

取当前单点 OI，用于核对最新值而非重建历史 OHLC：

```bash
curl -sS 'https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT' | jq .
```

## 3. 能否重建 TradingView `BTCUSDT.P_OI` 的 1D OHLC

### 不能直接或精确重建

`/futures/data/openInterestHist?period=1d` 每日只返回一个 `sumOpenInterest` 统计点。它没有 OI 的 `open`、`high`、`low`、`close` 四个字段，所以无法从日周期响应直接得到 TradingView `BINANCE:BTCUSDT.P_OI` 的一根 OI 蜡烛。

`/fapi/v1/openInterest` 也只返回查询时刻的当前 OI 单点，不提供历史 OHLC。

### 只能在最近一个月内近似聚合

可以把 `period=5m` 的 `sumOpenInterest` 样本按 UTC 自然日分组，构造近似值：

```text
open  = 最接近日界线起点的样本
high  = 当日 5m 样本最大值
low   = 当日 5m 样本最小值
close = 最接近日界线终点的样本
```

但这套结果只能称为“基于 Binance 5m OI 快照的近似日线”，原因包括：

- `timestamp` 是 period 结束时间，跨日边界样本必须按这一语义归属，不能机械地把时间戳显示日期当作 Kline 的 `openTime`。
- 5 分钟内发生后又恢复的 OI 极值不会出现在样本中，因此聚合的 `high/low` 可能偏窄。
- 官方 API 没有给出 TradingView `BTCUSDT.P_OI` 的采样频率、缺口处理和日线聚合算法，无法证明两套 OHLC 的生成规则完全一致。
- OI 历史最多只有最近 `1 month`；超出该范围的数据无法通过这个公开接口回补。
- 当前未结束的日线会随新样本变化，必须在同一截止时刻比较。

### 对主线程 CSV 比对的建议

主线程可以把验证分为两层：

1. 用 `/fapi/v1/klines` 对齐 CSV 的 BTCUSDT 永续价格 OHLC、BTC 成交量和 USDT `quoteVolume`；按 UTC `openTime` 对齐，并单独处理未收线日。
2. 用 `/futures/data/openInterestHist?period=5m` 聚合最近一个月的近似 OI 日线，再比较 TradingView OI OHLC。对不上时，应先区分“时间边界/采样差异”和“标的错误”，不能据此直接断言 TradingView 数据错误。

## 明确限制

- CSV 数值比较严格限定为 BTCUSDT 主图 OHLCV 和第一组 BTCUSDT OI；第二组其他标的 OI 已排除。
- 本文没有使用 TradingView 文档或第三方资料来补充 Binance 字段定义；全部事实来源均为 Binance 官方开发者文档或 `fapi.binance.com` 官方响应。
- `sumOpenInterest` 的 BTC 单位解释是基于 BTCUSDT 官方标的元数据与官方返回值关系的推断；官方 OI Statistics 字段描述本身没有逐字注明单位。
- 公开 REST API 可以支持价格/成交量的字段级对齐，以及最近一个月 OI 快照的近似对齐；它不能单独证明 TradingView OI 日线 OHLC 的完整历史与精确生成过程。
