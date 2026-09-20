# TradingView 以合约张数显示 Open Interest 的技术路径

研究日期：2026-08-24

研究对象：TradingView 官方 `Crypto Open Interest`、`OKX:BTCUSDT.P`、其 OI 服务符号 `OKX:BTCUSDT.P_OI`，以及 OKX `BTC-USDT-SWAP` 原生 Open Interest API。

## 结论

1. **TradingView 当前的 `OKX:BTCUSDT.P_OI` 不是合约张数，而是 USD OI。** 第一方符号页面元数据为 `currency=USD`、`measure=currency`，同期数值与 OKX `oiUsd` 约同为 `2.342B`，而不是约 `3,009,174` 的 `oi` 合约张数。[TradingView 符号页面](https://www.tradingview.com/symbols/BTCUSDT.P_OI/?exchange=OKX)；[OKX Open Interest API](https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP)
2. **TradingView 官方指标不能依靠一个已公开的“单位切换”把该 feed 改成 contracts。** 官方只说明 `Aggregated`/`Non-aggregated` 的数据范围，以及 Non-aggregated 的单位由交易所和衍生品决定；官方资料没有给出同一服务符号在 USD、币数和 contracts 之间切换的设置或 API。[TradingView：Understanding crypto open interest](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)；[TradingView 官方博客](https://www.tradingview.com/blog/en/crypto-derivatives-indicators-on-tradingview-53558/)
3. **在 Pine 内可实现“估算张数”，但不能宣称为 OKX 原生精确张数。** 技术路径是通过 `request.security()` 读取 `OKX:BTCUSDT.P_OI` 的 USD OI，再用同周期 BTC 合约价格以及当前合约面值反推。[TradingView Pine：Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)
4. **精确张数应直接取 OKX API 的 `oi`。** `oi` 是 contracts，`oiCcy` 是币数，`oiUsd` 是 USD OI；对于当前 `BTC-USDT-SWAP`，`ctVal=0.01`、`ctMult=1`、`ctValCcy=BTC`。[OKX：Get open interest](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-open-interest)；[OKX：Get instruments](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-instruments)
5. **Pine 的公开 API 不能直接调用 OKX REST/WebSocket。** `request.security()` 只能请求 TradingView 可用符号/上下文；`request.seed()` 只能读取既有 Pine Seeds 数据，且新 Pine Seeds 仓库当前暂停创建。因此，精确 API 路径必须在 Pine 之外采集和展示。[TradingView Pine：Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

## 已确认事实

### TradingView 的 Aggregated / Non-aggregated 规则

- `Aggregated`：显示该资产在 TradingView 可用交易所范围内的聚合 OI。现货图只能使用 Aggregated。
- `Non-aggregated`：显示单一交易所的 OI；要使用它，应选择具体期货或永续合约。
- TradingView 明确说明：Non-aggregated 值可能以基础币、报价币或 contracts 表示，取决于交易所和具体衍生品。
- TradingView 的一般 OI 帮助页说明，官方 OI 指标会显示它实际使用的 Open Interest 服务符号；OKX 属于受支持的加密衍生品交易所。

来源：[TradingView：Understanding crypto open interest](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)；[TradingView：Open Interest](https://www.tradingview.com/support/solutions/43000685269-open-interest/)

TradingView 没有公开 Aggregated OI 的完整归一化和聚合公式。不同交易所的“1 张合约”可能代表不同面值，因此即使能得到各交易所张数，也不能把张数直接相加并称为有统一经济含义的 Aggregated contracts。

### `OKX:BTCUSDT.P_OI` 服务符号

当前第一方页面确认存在 `OKX:BTCUSDT.P_OI`，其类型为 derivative metric。页面元数据为：

| 字段 | 当前值 |
| --- | --- |
| `pro_symbol` | `OKX:BTCUSDT.P_OI` |
| `currency` / `currency_code` | `USD` |
| `measure` | `currency` |
| `trade.price` | 约 `2.342B` |

来源：[TradingView：`BTCUSDT.P_OI`，指定 `exchange=OKX`](https://www.tradingview.com/symbols/BTCUSDT.P_OI/?exchange=OKX)

必须在 Pine 里写完整交易所前缀 `OKX:`。只打开不带 `exchange=OKX` 的通用网页路径，网页可能解析到同名的其他交易所符号；这不影响 Pine 中显式使用 `OKX:BTCUSDT.P_OI`。

### OKX 原生字段与当前证据快照

同期 OKX 第一方 API 快照约为：

| 来源/字段 | 当前值 | 官方含义 |
| --- | ---: | --- |
| `open-interest.oi` | `3,009,174` | 合约张数 contracts |
| `open-interest.oiCcy` | `30,091.7 BTC` | OI 对应的币数 |
| `open-interest.oiUsd` | `2.342B USD` | OI 对应的 USD 价值 |
| `instruments.ctVal` | `0.01` | 一张合约的面值参数 |
| `instruments.ctMult` | `1` | 合约乘数 |
| `instruments.ctValCcy` | `BTC` | 合约面值币种 |
| `instruments.ctType` | `linear` | 线性合约 |

直接端点：

- [`GET /api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP`](https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP)
- [`GET /api/v5/public/instruments?instType=SWAP&instId=BTC-USDT-SWAP`](https://www.okx.com/api/v5/public/instruments?instType=SWAP&instId=BTC-USDT-SWAP)

当前合约满足：

```text
oiCcy = oi × ctVal × ctMult
       ≈ 3,009,174 × 0.01 × 1
       ≈ 30,091.7 BTC

oiUsd = oiCcy × OKX 用于 USD 折算的估值价格
```

TradingView 服务符号的 `currency=USD`、`measure=currency`、约 `2.342B` 的数值，与 OKX 同期 `oiUsd≈2.342B` 一致；它与 `oi≈3,009,174` 的数量和量纲都不一致。因此可确认：**当前 `OKX:BTCUSDT.P_OI` 对应 OKX 的 USD OI 口径，而不是 contracts 口径。**

`ctVal`、`ctMult` 和 `ctValCcy` 确定每张合约对应的基础币面值；对当前 `BTC-USDT-SWAP`，一张对应 `0.01 BTC`。OKX 没有在上述 OI 字段说明中公开 `oiUsd` 逐时点采用哪一种价格，因此 Pine 只能使用同周期合约价格作代理。[OKX：Get instruments](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-instruments)

## 推荐的 TradingView / Pine 路径：估算 contracts

### 公式

对当前 OKX 线性合约：

```text
contractsApprox = oiUsdFromTradingView
                  / (proxyPrice × ctVal × ctMult)

BTC-USDT-SWAP 当前参数：
contractsApprox = oiUsdFromTradingView
                  / (proxyPrice × 0.01 × 1)
```

这里的 `proxyPrice` 是 TradingView 同周期 `OKX:BTCUSDT.P` 的价格。OKX 的 `oiUsd` 使用的估值价格与 TradingView K 线 close 的采样时间或口径可能不同，因此结果只能标记为 `contractsApprox`。

### 最小 Pine Script v6 代码片段

```pine
//@version=6
indicator("OKX BTCUSDT.P OI contracts estimate", overlay = false, format = format.volume)

string oiSymbol = "OKX:BTCUSDT.P_OI"
string priceSymbol = "OKX:BTCUSDT.P"

float ctVal = input.float(0.01, "ctVal (BTC)", minval = 0.00000001)
float ctMult = input.float(1.0, "ctMult", minval = 0.00000001)

float oiUsd = request.security(
    oiSymbol,
    timeframe.period,
    close,
    gaps = barmerge.gaps_off,
    lookahead = barmerge.lookahead_off,
    ignore_invalid_symbol = true)

float proxyPrice = request.security(
    priceSymbol,
    timeframe.period,
    close,
    gaps = barmerge.gaps_off,
    lookahead = barmerge.lookahead_off,
    ignore_invalid_symbol = true)

float contractsApprox = not na(oiUsd) and proxyPrice > 0 ? oiUsd / (proxyPrice * ctVal * ctMult) : na

plot(contractsApprox, "OI contracts (estimated)", color = color.blue, linewidth = 2)
```

`request.security()` 可请求另一个 TradingView 符号的序列；`ignore_invalid_symbol=true` 可在服务符号不存在时返回 `na`，而不是让脚本直接停止。[TradingView Pine：Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

该片段是推荐实现草案，仍需在 TradingView Pine Editor 中编译，并在代表性时间周期核对：

- 当前服务符号仍可用；
- 指标标题和数据窗口明确写 `estimated`；
- 日线与分钟线的 OI 时间对齐；
- 实时未收线值与收线后值的差异；
- `ctVal`、`ctMult` 是否仍与 OKX 当前 instruments 响应一致。

## 精确 contracts 路径

精确当前张数无需换算，直接读取：

```http
GET https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=BTC-USDT-SWAP
```

响应中的：

```text
data[0].oi
```

就是 OKX 定义的 contracts 数量。[OKX：Get open interest](https://www.okx.com/docs-v5/en/#rest-api-public-data-get-open-interest)

如果需要持续的实时精确张数，也可以在 Pine 之外订阅 OKX 公共 WebSocket 的 `open-interest` channel；其消息同样返回 `oi`、`oiCcy` 和 `oiUsd`。生产环境公共地址为 `wss://ws.okx.com:8443/ws/v5/public`，具体域名仍应按账户地区采用 OKX 当前文档指定值。[OKX API 文档](https://www.okx.com/docs-v5/en/)

这一端点适合由 Pine 之外的采集器、研究脚本或 Dashboard 使用。若要形成精确的历史 contracts 曲线，必须在外部按固定频率采集 `oi` 并保存时间序列；当前端点本身是当前快照接口。

Pine 公开接口没有通用 HTTP、REST 或 WebSocket 客户端，不能直接请求该 URL。`request.seed()` 也不是实时替代方案：它只能读取既有 Pine Seeds GitHub 数据源，而且新仓库当前暂停创建。[TradingView Pine：Other timeframes and data](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

## 限制、推断与未知项

### 已确认

- 当前 `OKX:BTCUSDT.P_OI` 的单位是 USD，并与 OKX `oiUsd` 对应。
- OKX `oi` 是精确 contracts；`oiCcy` 是币数；`oiUsd` 是 USD OI。
- 当前 `BTC-USDT-SWAP` 的 `ctVal=0.01`、`ctMult=1`、`ctValCcy=BTC`。
- `request.security()` 可以读取 TradingView 已提供的 `_OI` 服务符号。

### 推断

- 用户图中约 `25.56B` 的 OI 明显高于同期 OKX 单交易所约 `2.342B`，因此该面板很可能选择了 Aggregated，而不是 `OKX:BTCUSDT.P_OI` 的 Non-aggregated 数据。必须在指标设置中实际确认后才能定论。
- 用 TradingView OI USD 除以 TradingView 合约 close，可近似恢复张数；由于估值价格和时间戳不完全同步，无法保证逐 bar 等于 OKX 原生 `oi`。
- Pine 公共文档列出的数据请求入口不包含通用网络客户端，因此 Pine 无法直接调用任意外部 REST/WebSocket。该结论针对公开 Pine API。

### 未知

- TradingView 未公开 Aggregated OI 的完整交易所纳入、归一化和历史变更公式，不能把 Aggregated USD OI可靠地反推成统一的“总张数”。
- 未发现 TradingView 第一方资料提供 `OKX:BTCUSDT.P` 的另一个 contracts 单位 OI 服务符号。
- 官方资料没有记录把同一个 `OKX:BTCUSDT.P_OI` 在 USD、BTC 和 contracts 之间切换的设置；因此实现方案不能依赖未文档化的单位切换。
- `_OI` 服务符号的单位、可用历史和交易所映射可能随数据供应更新而变化，使用前应重新核验。

## 现有仓库风险与实施边界

1. 当前仓库策略已明确偏好 TradingView 官方原始 OI。新增 `contractsApprox` 属于自定义换算，不能静默替换现有“官方原始 OI”，也不能标注为 native/exact。
2. 本研究只定义技术路径，不证明 Pine 代码已编译或图表效果已验收；实现时仍需 TradingView Pine Editor 编译和图表核对。
3. 不应把 Aggregated OI 除以 OKX 合约面值。Aggregated 包含多个交易所，各交易所合约面值和单位可能不同。
4. 不应把 `oiUsd / price` 直接称为合约张数。该结果先得到 BTC 数量；还必须除以当前 `ctVal × ctMult`。
5. `ctVal=0.01` 是当前 `BTC-USDT-SWAP` 的产品参数，不应未经 API 复核永久硬编码到其他品种或未来版本。
6. 实时柱使用未收线的价格和 OI；即使 `lookahead_off`，当前柱仍可能变化。告警或研究统计必须区分实时值与已确认柱。
7. 精确 API 采集属于当前 Pine 研究仓库之外的数据采集/runtime 范畴。未经额外授权，不应为此重新引入 Python、数据库、Docker 或交易执行层。

## 推荐决策

- 若目标是继续使用 TradingView：新增一个独立研究指标，名称明确包含 `estimated`，使用上述公式显示 `contractsApprox`；不要改变现有官方原始 OI 指标。
- 若目标是精确张数：使用 OKX `open-interest` API 的 `oi`，并在 Pine 之外采集和展示。
- 若目标是跨交易所 Aggregated OI：继续使用 TradingView 官方 Aggregated 数据，但保持其原始单位，不把它转换或标注成统一 contracts。
