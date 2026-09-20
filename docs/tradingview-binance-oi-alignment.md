# TradingView `BINANCE:BTCUSD.P_OI` 与 Binance COIN-M OI 对齐

研究日期：2026-08-26

## 结论

要把两边可靠对齐，应把 Binance 实时接口作为主证据：每 5 秒读取 `BTCUSD_PERP.openInterest`，按完整 UTC 日聚合 OHLC，再与事后导出的 TradingView `BINANCE:BTCUSD.P_OI` 日线 OHLC 比较。Binance 历史统计接口只能用于诊断，不能替代实时采样。

目前第一方证据支持以下判断：

- 合约映射有强证据：TradingView 把 `BINANCE:BTCUSD.P_OI` 作为 `BINANCE:BTCUSD.P` 加 `_OI` 后的 OI 服务符号；Binance API 中对应的 BTCUSD COIN-M 永续为 `BTCUSD_PERP`。
- Binance 规格明确：当前 `BTCUSD_PERP` 返回 `pair=BTCUSD`、`contractType=PERPETUAL`、`contractSize=100`、`quoteAsset=USD`、`quantityPrecision=0`，`LOT_SIZE.stepSize=1`。
- TradingView 没有公开逐符号说明，明确声明 `BTCUSD.P_OI` 直接映射 Binance 的哪个 API 字段、使用什么采样频率、如何回填历史或构造 OHLC。因此“同一字段、同一历史生成方法”不能由文档证明。
- TradingView 符号页会暴露一个 `trade.price` 和数据更新时间，但抓取时该页面值明显滞后于 Binance 实时响应，不能把两者当作同步快照，也不能据此确认单位。单位是否一致必须由同时间桶的前瞻采样验证。

## 两边分别是什么

| 维度 | TradingView | Binance COIN-M API | 对齐方式 |
| --- | --- | --- | --- |
| 合约 | `BINANCE:BTCUSD.P_OI`，源合约为 `BINANCE:BTCUSD.P` | `symbol=BTCUSD_PERP`、`pair=BTCUSD`、`contractType=PERPETUAL` | 只比较这一对，不混入季度合约或 USDⓈ-M |
| 单位 | 官方仅说明非聚合 OI 可能是基础币、报价币或 contracts；未发布该符号的逐字段单位表 | 实时字段为 `openInterest`；历史 `sumOpenInterest` 明示单位 `cont`，`sumOpenInterestValue` 为基础资产 | 先把 TradingView 原值作为“contracts 候选值”直接比较；只有同步样本持续接近 `1:1` 才确认该口径。不乘 `100`，不除价格，不比较 `sumOpenInterestValue` |
| 时区 | 符号页元数据为 `timezone=Etc/UTC` | `exchangeInfo.timezone=UTC` | 使用 `[00:00:00, 次日 00:00:00)` UTC 日 |
| OHLC | TradingView 第一方 `Request` 库说明 crypto OI 可返回指定周期的 O/H/L/C | 实时接口每次只给一个当前快照 | 对实时快照按时间排序：首值为 open、最大值为 high、最小值为 low、末值为 close |
| 历史 | TradingView 提供分钟级 crypto OI 和聚合后的周期 OHLC | `openInterestHist` 是周期结束时的统计快照，不是 OHLC，且只保留最近 30 天 | 历史接口只做辅助诊断；5 分钟快照聚合出的 high/low 仍是近似值 |

来源：

- [TradingView：Understanding crypto open interest](https://www.tradingview.com/support/solutions/43000762388-understanding-crypto-open-interest/)
- [TradingView：Open Interest](https://www.tradingview.com/support/solutions/43000685269-open-interest/)
- [TradingView 第一方 `Request` 库](https://www.tradingview.com/script/Rpmobpw5-Request/)
- [TradingView：`BINANCE:BTCUSD.P_OI`](https://www.tradingview.com/symbols/BTCUSD.P_OI/?exchange=BINANCE)
- [TradingView：`BINANCE:BTCUSD.P`](https://www.tradingview.com/symbols/BTCUSD.P/?exchange=BINANCE)
- [Binance COIN-M Market Data 文档](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data)
- [Binance 当前 `BTCUSD_PERP` OI](https://dapi.binance.com/dapi/v1/openInterest?symbol=BTCUSD_PERP)
- [Binance COIN-M Exchange Information](https://dapi.binance.com/dapi/v1/exchangeInfo)
- [Binance `BTCUSD` 永续 5 分钟 OI 统计](https://dapi.binance.com/futures/data/openInterestHist?pair=BTCUSD&contractType=PERPETUAL&period=5m&limit=2)

## 时间戳和日线归属

TradingView 的图表时区只影响显示，不改变 Pine 的时间计算；Pine 的 `time`、`time_close` 是与时区无关的 UNIX 毫秒时间戳。为方便人工检查，导出时仍应把图表显示时区设为 UTC。来源：[TradingView Pine 时间文档](https://www.tradingview.com/pine-script-docs/concepts/time/)。

Binance `openInterestHist.timestamp` 明确是周期结束时间。若时间戳恰好为 `00:00:00.000 UTC`，它属于刚结束的前一日，因此历史诊断应按 `timestamp - 1ms` 的 UTC 日期归属。例如 `2026-08-26 00:00:00 UTC` 代表截至该时点结束的 `2026-08-25` 日。

实时快照则使用响应中的 `time`，并按以下半开区间归日：

```text
2026-08-25 日 = [2026-08-25T00:00:00.000Z, 2026-08-26T00:00:00.000Z)
```

## 可执行方案

1. 在 TradingView 打开 `BINANCE:BTCUSD.P`，加载固定读取 `BINANCE:BTCUSD.P_OI` 的指标，周期设为 `1D`，图表显示时区设为 UTC。不要选择 Aggregated OI，也不要使用 CSV 中其他聚合 OI 列。
2. 启动实时采集。工具会从下一个完整 UTC 日开始计数，取得 7 个合格日或到达 14 个日历日后停止，并支持中断续传：

```bash
python3 tools/validation/validate_binance_coinm_oi.py collect \
  --snapshot-file data/raw/binance-oi/btcusd_perp_open_interest.csv \
  --interval-seconds 5 \
  --target-days 7 \
  --max-days 14
```

3. 采样完成后，重新从 TradingView 导出覆盖这 7 个 UTC 日的 CSV。保持当前验证器要求的 17 列布局：自定义 OI OHLC 必须连续位于第 10--13 列；第 14--17 列聚合 OI 会被忽略。TradingView 官方说明，CSV 导出的是图表当前已加载的 ticker 和指标数据：[How to export chart data](https://www.tradingview.com/support/solutions/43000537255-how-to-export-chart-data/)。
4. 运行比较：

```bash
python3 tools/validation/validate_binance_coinm_oi.py compare \
  --csv 'data/<重新导出的UTC日线CSV>.csv' \
  --snapshot-file data/raw/binance-oi/btcusd_perp_open_interest.csv \
  --timezone UTC \
  --out-dir data/reports
```

合格日要求：覆盖率至少 `99%`、最大采样缺口不超过 `30` 秒、UTC 日界线两侧最近样本不超过 `10` 秒。默认容差为 open/close `10 bps`，high/low `20 bps`。误差计算为：

```text
error_bps = abs(TradingView - Binance) / abs(Binance) * 10000
```

`PASS` 只表示 7 个合格日内，TradingView 与 Binance 公开实时 API 在上述采样和容差下相符；`FAIL` 表示覆盖充分但数值超限；覆盖或日期不足时为 `INCONCLUSIVE`。

不要用本次历史差值生成固定缩放系数。若 TradingView 原值与实时 API 在同步窗口中不是近似 `1:1`，应先判定为口径未确认；只有它稳定符合 Binance 合约规格可解释的换算关系时，才能另行定义并验证单位转换。

历史诊断可运行：

```bash
python3 tools/validation/validate_binance_coinm_oi.py historical \
  --csv 'data/OKX_BTCUSDT.P, 1D_8b8c1.csv' \
  --days 30 \
  --out-dir data/reports
```

但不能把结果当作正式通过/失败。2026-08-26 的官方响应中，附近时点的历史 `sumOpenInterest=12,226,055` 与实时 `openInterest=10,441,759` 相差约 `17.09%`；两者即使都筛选 `PERPETUAL`，也不能假设可互换。

## 文档无法证明的边界

- TradingView 没有发布 `BINANCE:BTCUSD.P_OI` 到 `/dapi/v1/openInterest?symbol=BTCUSD_PERP` 的正式字段映射表。
- TradingView 没有公开该 OI feed 的采样频率、延迟、修订、缺失值处理、历史回填来源或 OHLC 聚合算法。
- 5 秒轮询可能漏掉采样间隔内的瞬时 high/low，因此只能在覆盖率和容差约束下验证一致性，不能证明逐笔完全相同。
- Binance 历史统计接口的一条记录只是周期结束快照；把 5 分钟点聚合成日线不能恢复真实的逐时刻极值。
- 即使最终 `PASS`，也只能证明 TradingView 数据与 Binance 公开 API 一致，不能证明 Binance 内部账本绝对真实，也不能代表 Binance 全部 BTC OI。
