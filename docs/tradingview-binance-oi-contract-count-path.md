# TradingView 实现 Binance BTC OI 合约张数的技术路径

研究日期：2026-08-24

研究范围：Binance USDⓈ-M 与 COIN-M BTC 合约、TradingView 对应的非聚合 OI 服务符号，以及 Pine Script v6 可用的数据接入方式。

## 结论

1. **TradingView 内存在可直接读取的 Binance 原生合约张数路径：`BINANCE:BTCUSD.P_OI`。** 它对应 Binance COIN-M `BTCUSD_PERP`。Binance 官方历史接口明确把 COIN-M `sumOpenInterest` 的单位定义为 `cont`（contracts），当前合约规格为 `contractSize=100`、`quantityPrecision=0`；TradingView 符号页的原始数值与 Binance `/dapi/v1/openInterest` 返回的整数 `openInterest` 同量级且同期接近。
2. **`BINANCE:BTCUSDT.P_OI` 不是离散合约张数。** TradingView 第一方页面把该 USDⓈ-M OI feed 标为 `currency_code=BTC`、`measure=currency`，其数值与 Binance `/fapi/v1/openInterest?symbol=BTCUSDT` 的 BTC 数量口径相符。它可以叫“BTC OI 数量”，不应改名为“合约张数”。
3. **推荐的 v1 指标只统计 `BTCUSD_PERP` 的原生张数。** Pine 直接读取 `BINANCE:BTCUSD.P_OI`，不除价格、不乘汇率、不使用开仓价，因此没有估值换算误差。
4. **若只看当前截面，可以再加 COIN-M 当前季度和下一季度。** 2026-08-24 实测 TradingView 服务符号为 `BINANCE:BTCUSDU2026_OI` 与 `BINANCE:BTCUSDZ2026_OI`，对应 Binance `BTCUSD_260925` 与 `BTCUSD_261225`；当前三者均为 `100 USD/张`，张数可以直接相加。
5. **当前三个 COIN-M 符号之和不是完整历史聚合序列。** 季度合约会到期并滚动；只把当前季度符号写进 Pine，会使更早历史漏掉当时活跃的旧季度合约。完整历史需要维护季度符号映射，或者使用 Pine 之外的数据采集。Binance 官方聚合历史接口只提供最近 30 天，Pine 也不能直接调用任意 REST API。
6. **不能把 USDⓈ-M 与 COIN-M 的原始数字直接相加。** 前者是 BTC 数量口径，后者是固定 `100 USD/张` 的整数 contracts。若以后要做全 Binance BTC OI，只能选统一名义价值口径，或明确标注为“标准化合约等价数”，不能称为原生总张数。

## 官方证据

### TradingView 的 OI 规则

TradingView 官方说明：

- `Non-aggregated` OI 表示单一交易所的具体衍生品；
- 非聚合值可能以基础币、报价币或 contracts 表示，取决于交易所和具体衍生品；
- 官方 OI 指标会显示其实际使用的 OI 服务符号；
- Pine 的 `request.security()` 可以读取另一个 TradingView 符号和时间周期的数据。

来源：

- [TradingView：Understanding crypto open interest](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)
- [TradingView：Open Interest](https://www.tradingview.com/support/solutions/43000685269-open-interest/)
- [TradingView：New crypto derivatives indicators](https://www.tradingview.com/blog/en/crypto-derivatives-indicators-on-tradingview-53558/)
- [TradingView Pine：Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

### USDⓈ-M：`BTCUSDT.P_OI` 是 BTC 数量口径

TradingView 第一方符号页当前元数据：

| 字段 | 值 |
| --- | --- |
| `pro_symbol` | `BINANCE:BTCUSDT.P_OI` |
| `currency_code` | `BTC` |
| `measure` | `currency` |

来源：[TradingView：`BINANCE:BTCUSDT.P_OI`](https://www.tradingview.com/symbols/BTCUSDT.P_OI/?exchange=BINANCE)

Binance 当前 OI 端点：

```http
GET https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT
```

它返回带小数的 `openInterest`；当前 `BTCUSDT` 交易规格以 BTC 为 `baseAsset`，数量精度为 3，最小/步长为 `0.001`，没有 COIN-M 那种固定 `contractSize=100` 的离散张定义。

来源：

- [Binance USDⓈ-M Market Data：Open Interest](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest)
- [Binance USDⓈ-M Exchange Information API](https://fapi.binance.com/fapi/v1/exchangeInfo)
- [Binance USDⓈ-M 当前 BTCUSDT OI](https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT)

因此，`BINANCE:BTCUSDT.P_OI` 可以直接用于观察 Binance 主流线性永续的 BTC OI，但它不是本研究所说的整数“张数”。

### COIN-M：`BTCUSD.P_OI` 是原生 contracts 路径

Binance COIN-M 官方资料给出：

- `/dapi/v1/openInterest` 返回具体 `symbol` 的 `openInterest`；
- `/futures/data/openInterestHist` 把 `sumOpenInterest` 明确定义为 `unit: cont`，把 `sumOpenInterestValue` 定义为 `unit: base asset`；
- `/dapi/v1/exchangeInfo` 当前对 `BTCUSD_PERP` 返回 `contractSize=100`、`quantityPrecision=0`，即 BTCUSD COIN-M 一张为 `100 USD` 名义面值，数量按整数张计。

来源：

- [Binance COIN-M Market Data：Open Interest / Statistics / Exchange Information](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data)
- [Binance COIN-M 当前 BTCUSD_PERP OI](https://dapi.binance.com/dapi/v1/openInterest?symbol=BTCUSD_PERP)
- [Binance COIN-M Exchange Information API](https://dapi.binance.com/dapi/v1/exchangeInfo)

TradingView 第一方符号页确认存在：

```text
BINANCE:BTCUSD.P_OI
```

来源：[TradingView：`BINANCE:BTCUSD.P_OI`](https://www.tradingview.com/symbols/BTCUSD.P_OI/?exchange=BINANCE)

2026-08-24 的交叉核对中，TradingView 页面 `trade.price` 与 Binance `BTCUSD_PERP.openInterest` 都约为 1,100 万，数值会因页面缓存、API 时间戳和实时仓位变化略有差异，但数量级与整数口径一致。当前季度和下一季度的核对更接近：

| TradingView OI 符号 | Binance 合约 | TradingView 页面快照 | Binance API 快照 | `contractSize` |
| --- | --- | ---: | ---: | ---: |
| `BINANCE:BTCUSD.P_OI` | `BTCUSD_PERP` | 约 1,100 万 | 约 1,100 万 | `100 USD` |
| `BINANCE:BTCUSDU2026_OI` | `BTCUSD_260925` | `822,208` | `821,941` | `100 USD` |
| `BINANCE:BTCUSDZ2026_OI` | `BTCUSD_261225` | `375,940` | `375,930` | `100 USD` |

季度合约快照仅用于验证 TradingView 原始值的 contracts 口径，不应永久写死为未来的活跃季度映射。

## 推荐实现：v1 只画 COIN-M 永续原生张数

### 无代码路径

1. 打开 `BINANCE:BTCUSD.P`；
2. 添加 `Indicators → Fundamentals → Derivatives → Crypto open interest`；
3. 选择 `Non-aggregated`；
4. 确认指标标题显示服务符号 `BINANCE:BTCUSD.P_OI`。

### Pine Script v6 最小草案

```pine
//@version=6
indicator("Binance BTCUSD COIN-M OI Contracts", overlay = false, format = format.volume)

string oiSymbol = input.symbol("BINANCE:BTCUSD.P_OI", "OI source")

float oiContracts = request.security(
    oiSymbol,
    timeframe.period,
    close,
    gaps = barmerge.gaps_off,
    lookahead = barmerge.lookahead_off,
    ignore_invalid_symbol = true)

plot(oiContracts, "OI contracts", color = color.blue, linewidth = 2)
```

这段代码没有进行单位换算；`oiContracts` 直接采用 TradingView 的 COIN-M OI 服务符号。它是实现草案，尚未在 TradingView Pine Editor 中编译或做图表验收。

实现时应检查：

- 服务符号仍为 `BINANCE:BTCUSD.P_OI`；
- 数值与 Binance `/dapi/v1/openInterest?symbol=BTCUSD_PERP` 同量级；
- 分钟、小时、日线的历史可用性；
- 实时未收线柱与已确认柱的变化；
- `lookahead_off` 没有未来数据泄漏；
- 指标标题明确写 `COIN-M` 和 `Contracts`，避免误解为 Binance 全部 BTC OI。

## 可选实现：当前 COIN-M BTC 总张数

当前可用公式为：

```text
currentCoinMContracts
    = BTCUSD_PERP contracts
    + BTCUSD current-quarter contracts
    + BTCUSD next-quarter contracts
```

2026-08-24 对应 TradingView 符号：

```text
BINANCE:BTCUSD.P_OI
BINANCE:BTCUSDU2026_OI
BINANCE:BTCUSDZ2026_OI
```

因为当前三个 BTCUSD COIN-M 产品的 `contractSize` 都是 `100 USD`，它们的原生张数可以直接相加。建议把两个季度符号做成 `input.symbol()`，每次季度滚动时人工更新，并在数据窗口分别显示三个来源。

限制：

- 当前活跃符号之和只在这些合约共同存在的时间区间完整；
- 进入更早历史后，会漏掉当时的旧季度合约；
- 不应使用 `nz()` 把完全缺失的数据静默当作有效的零 OI；
- 若要完整滚动历史，必须维护旧季度映射，并受 Pine `request.*()` 数量限制；
- Binance REST 的 COIN-M 聚合历史接口在省略 `contractType` 时可聚合各合约类型，但官方只提供最近 30 天，而且 Pine 不能直接调用该端点。

## 不推荐路径

1. **不要用 `BINANCE:BTCUSDT.P_OI / BTC价格`。** `BTCUSDT.P_OI` 已是 BTC 数量口径，再除价格会造成量纲错误。
2. **不要把 `BTCUSDT.P_OI` 与 `BTCUSD.P_OI` 直接相加。** 一个是 BTC 数量，一个是 `100 USD/张` 的 contracts。
3. **不要把当前季度符号永久硬编码成完整历史。** `U2026`、`Z2026` 会到期。
4. **不要把 COIN-M 永续 OI 标成“Binance 总 OI”。** 它不包括 USDⓈ-M `BTCUSDT`、`BTCUSDC` 等线性合约，也不自动包括季度交割合约。
5. **不要用开仓价恢复张数。** 原生张数由交易所当前未平仓数量与产品合约规格决定，开仓价影响持仓成本和盈亏，不影响当前 contracts 数量。

## 推荐决策

- 第一阶段实现独立指标 `Binance BTCUSD COIN-M OI Contracts`，数据源固定为 `BINANCE:BTCUSD.P_OI`；这是 TradingView 内最简单、语义最干净的原生张数路径。
- 若图表验收通过，再增加可选的当前/下一季度输入与分项显示；默认仍只显示永续，避免滚动历史不完整。
- 若最终目标是 Binance 全部 BTC 衍生品，应改用统一名义价值或分别展示 `USDⓈ-M BTC OI` 与 `COIN-M contracts`，不要制造一个不存在的“原生总张数”。
