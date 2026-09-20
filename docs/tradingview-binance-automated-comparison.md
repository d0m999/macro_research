# TradingView 与 Binance BTCUSDT 永续持续自动比对

研究日期：2026-08-26

## 结论

使用官方接口无法做到 TradingView 侧完全零人工：TradingView 不提供读取其图表或指标历史值的公开数据 API，Pine 也不能调用任意外部 HTTP。最少人工方案是：把 Pine 导出器加到 `BINANCE:BTCUSDT.P`，在界面创建 webhook alert；之后由服务端自动接收 TradingView 已收线数据，同时采集 Binance USDⓈ-M `BTCUSDT` 官方数据并持续比对。账户支持开放式 alert 时只需配置一次；否则仍需按到期时间人工续期。

若不要求激活前的 TradingView 历史，CSV 可完全取消。若必须核对激活前历史，仍需最后一次人工导出 CSV；官方接口不能自动回填 TradingView 历史。

固定边界：

- TradingView 价格/成交量：`BINANCE:BTCUSDT.P`
- TradingView OI：`BINANCE:BTCUSDT.P_OI`，非聚合
- Binance：USDⓈ-M `BTCUSDT` 永续
- 标准 K 线、UTC、仅比较已收线 bar
- 排除 `BTCUSD.P`、`BTCUSD_PERP`、COIN-M、连续合约和聚合 OI

## 官方能力边界

| 能力 | 官方结论 | 设计影响 |
|---|---|---|
| TradingView 历史数据 REST API | [官方明确没有向用户提供数据或指标值的 API](https://www.tradingview.com/support/solutions/43000474413-i-need-access-to-your-api-in-order-to-get-data-or-indicator-values/)；其 REST API 面向接入平台的经纪商 | 不能由服务端主动拉取 TradingView 历史或补漏 |
| Pine 出站 HTTP | 官方列出的 [`request.*()`](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/) 只读取 TradingView 管理的数据上下文，没有通用 HTTP/REST/WebSocket 客户端 | Pine 不能直接请求 Binance；只能生成 alert 事件 |
| Alert webhook | [Webhook](https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/) 可向外部 URL POST JSON | 这是 TradingView 数据自动出站的官方路径 |
| Alert 历史回填 | [Alert 仅在实时 bar 触发](https://www.tradingview.com/pine-script-docs/concepts/alerts/)；Pine 不能创建运行中的 alert，必须由用户在图表 UI 创建 | 激活前历史不会补发；改脚本、输入、主图标的或周期后须重建 alert |
| Webhook 运行限制 | 必须启用 2FA；仅端口 80/443；接收端超过 3 秒未响应会取消；官方提示偶有投递失败；接收端返回 5xx（504 除外）时会在 5 秒后重试，最多重发 3 次 | 入口应先持久化再快速确认，按幂等键去重，并监控缺口和 Webhook status；见 [Webhook resubmission](https://www.tradingview.com/support/solutions/43000735201-webhook-resubmission/) |
| Alert 有效期 | [普通 alert 最长两个月；Premium 和 Ultimate 可选择 Open-ended](https://www.tradingview.com/support/solutions/43000520149-introduction-to-tradingview-alerts/) | 要做到一次配置后持续运行，应使用支持 Open-ended 的账户；否则续期是唯一残留人工步骤 |
| Alert 频率 | [3 分钟内超过 15 次会自动停止](https://www.tradingview.com/support/solutions/43000597494-alerts-on-alert-function/) | 使用每根 bar 收线一次，不使用 every-tick 导出 |
| TradingView 手工历史 | [CSV 只能导出图表已加载的数据](https://www.tradingview.com/support/solutions/43000537255-how-to-export-chart-data/)；日内历史还受[账户 bar 数限制](https://www.tradingview.com/support/solutions/43000480679-historical-intraday-data-bars-and-limits-explained/) | 只适合作为一次性基线，不适合作为持续管线 |
| Binance Kline | [`GET /fapi/v1/klines`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#kline-candlestick-data)，`limit` 默认 500、最大 1500 | 可分页回填价格 OHLC 和成交量；官方未声明固定总保留期，不应称为无限历史 |
| Binance 当前 OI | [`GET /fapi/v1/openInterest`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest)，返回 `openInterest`、`symbol`、`time` | 定时轮询并自行长期保存，才能形成高频 OI 快照历史 |
| Binance 历史 OI | [`GET /futures/data/openInterestHist`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#open-interest-statistics)；周期 `5m` 至 `1d`，`limit` 最大 500，只保留最近 1 month | 它返回周期统计点，不是 OI OHLC；只能近似聚合且不能补回更早历史 |

TradingView 官方同时说明，单交易所 OI 的单位取决于交易所和衍生品；本设计只原样比较 `BTCUSDT.P_OI` 与 Binance `sumOpenInterest`/`openInterest`，不把它误标为 `sumOpenInterestValue`。参见 [TradingView Crypto OI](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)。

## 推荐架构

```text
TradingView Pine -> realtime alert -> HTTPS webhook -> 快速入队 -> TV 原始存储
Binance Kline WS/REST + 当前 OI REST轮询 -------------------> Binance 原始存储
TV 原始存储 + Binance 原始存储 -> UTC/精度归一 -> Comparator -> 报告与缺口告警
```

Pine 导出器固定主图 `BINANCE:BTCUSDT.P` 和 OI `BINANCE:BTCUSDT.P_OI`，不把标的做成可误选的输入；周期不符时直接报错。它读取价格 OHLCV，并用 `request.security("BINANCE:BTCUSDT.P_OI", timeframe.period, [open, high, low, close])` 读取同周期 OI。仅在 `barstate.isconfirmed` 时以 `alert.freq_once_per_bar_close` 发送 JSON。

建议 payload 固定包含：`schema_version`、`script_version`、`tickerid`、`oi_tickerid`、`timeframe`、`time`、`time_close`、`confirmed`、价格 OHLC、`volume`、OI OHLC 和单位。数值用十进制字符串传输。每次携带最近 3 根已收线 bar；即使一条 webhook 丢失，下一条也能在窗口内自动补齐。幂等键使用 `(tickerid, oi_tickerid, timeframe, time, script_version)`。

Webhook 入口只校验、持久化并入队，3 秒内返回 2xx；持久化失败时返回可重试的 5xx。比较和 Binance 查询异步执行。不要在 payload 放登录凭证、交易 API key 或密码；接收端使用 HTTPS 和来源限制。

## 一次性人工步骤

1. 保存 Pine 导出器，并将它一次性添加到 `BINANCE:BTCUSDT.P` 的目标周期；若只验收 `1D`，只需一个 `1D` alert。
2. 开启 TradingView 2FA，在 Create Alert 中选择 `Any alert() function call`，填入 HTTPS webhook URL，并做一次投递测试；账户支持时选择 Open-ended，否则记录续期日。
3. 记录 alert 的脚本版本、输入、标的和周期。任何一项变化后删除并重建 alert，因为运行中的 alert 是创建时快照。
4. 选择历史起点：推荐直接以 alert 激活时刻为 `T0`；只有必须验证 `T0` 前历史时，才最后人工导出一次含 OI plots 的 CSV。

## 实现分档

- **最小 1D 方案**：一个 `1D` TradingView alert；收线后调用 Binance Kline REST，并用 `openInterestHist?period=5m` 近似日线 OI。可立即取消持续 CSV 和 agents 比对，不需要 Kline WebSocket 或常驻 OI 采样器；代价是 OI high/low 仍为近似值。
- **高保真 OI 方案**：保留同一个 TradingView alert，另以 5--15 秒轮询当前 OI，并可选接入 Kline WebSocket。它能形成自有 OI OHLC 和覆盖率记录，适合严格核对 high/low；代价是需要常驻采集和长期原始存储。

## 持续自动步骤

1. TradingView 每根目标周期 bar 收线后发送最近 3 根已收线记录；接收端去重并保存原始 JSON。
2. 当前 `1D` 范围可在收线后直接查询 REST Kline。需要更低周期实时核对时，再订阅官方 [`btcusdt@kline_<interval>`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#kline-candlestick-streams)，只接收 `k.x=true` 的已收线 bar；REST Kline 继续用于复核和补 Binance 侧缺口。
3. 高保真档才需要每 5--15 秒轮询 `/fapi/v1/openInterest?symbol=BTCUSDT`，保存原始时间戳，按相同 UTC bar 聚合 OHLC。采样越密，高低点越接近 TradingView，但仍不是逐笔证明。
4. Comparator 等两侧数据到齐后按 bar 开盘时间连接，使用十进制定点数比较，输出绝对误差、bps、时间偏移和缺失状态。
5. 定时扫描 alert 心跳和 bar 连续性。Binance 缺口通常可由 REST 回补；TradingView 单次漏发由下一条 payload 的滚动窗口补齐，超过窗口的缺口无法通过官方 API 主动补拉，只能标记并按需人工恢复。

## 历史链路

- TradingView：一次性 CSV 或从 `T0` 开始；alert、Bar Replay 和 Pine 历史执行都不会主动补发历史 webhook。滚动窗口只能修复 `T0` 后的短期投递缺口。
- Binance 价格/成交量：按 `startTime`、`endTime` 和 `limit<=1500` 分页请求 `/fapi/v1/klines`。数组 `[0..7]` 依次包含开盘时间、OHLC、基础资产成交量、收盘时间和计价资产成交量。
- Binance OI：最近一个月可分页请求 `period=5m&limit<=500`，使用 `sumOpenInterest` 和 `timestamp`；聚合后的 OI high/low 会漏掉 5 分钟采样间的极值。
- 超过一个月的 Binance OI 不能事后从该官方接口恢复，必须从系统启用之日起自行保存当前 OI 快照。

## 实时比对规则

- 价格 OHLC 与成交量：TradingView `BINANCE:BTCUSDT.P` 对 Binance `/fapi/v1/klines` 的 `[1..5]`。
- OI close：对最近的 Binance OI 快照，同时记录时间偏移；OI open/high/low 对本地轮询快照聚合值。
- `openInterestHist` 只作为最近一个月的历史补充，不把单点误称为完整 OI candle。
- 只比较已收线、同 UTC 边界、同周期数据；未收线值单独存储，不计入一致性结果。
- 不预设 OI 必须逐点相等。先累计基线，再分别为 close 与采样敏感的 high/low 设置阈值。

## 不可行或不推荐

- 把 TradingView 经纪商 REST API 当作图表历史数据 API。
- 让 Pine 直接调用 Binance REST/WebSocket，或指望 alert 回放历史 bar。
- 抓取 TradingView 私有接口、自动化浏览器导出 CSV 或依赖非官方库；接口不受官方支持，稳定性和授权边界不可控。
- 用 Binance `continuousKlines`、COIN-M `BTCUSD_PERP`、聚合 OI 或 `sumOpenInterestValue` 替代本任务的精确标的和字段。
- 用 5 分钟 `openInterestHist` 聚合值宣称已经精确重建 TradingView OI OHLC。
- 忽略 webhook 丢失：官方明确提示投递可能失败，TradingView 侧又没有官方补拉接口。

最终建议：先上线“一个 1D TradingView alert + 持续 webhook + Binance REST + 确定性 Comparator + 缺口监控”，立即取消持续 CSV 和 agents 比对；只有要严格核对 OI high/low 时，再增加当前 OI 常驻轮询。这是官方能力范围内人工最少、边界最清楚的持续比对方案。
