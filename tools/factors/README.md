# tools/factors — 多因子研究流水线

本目录承载**离线统计分析**：采集公开行情、构造因子矩阵、做单因子检验与去冗余。

## 边界（先读这条）

按 `CLAUDE.md`，本仓库禁止重新引入 **Python 交易执行层**（FreqTrade、下单接口、账户签名、Docker 部署、交易数据库）。
本目录属于**离线分析层**：只读公开行情、只写本地 CSV 与报告，不接触订单、仓位、账户或私钥。

不要在本目录引入以下内容：交易所私有 API、API key/secret、下单函数、回测撮合引擎、实盘调度器。

## 目录结构

```
tools/factors/
  README.md                      本文件
  crypto-perp/collect.py         加密线采集器（Binance 永续 + 现货）
  ai-supply-chain/               美股 AI 产业链线（待建）
```

因子清单与检验口径登记在：

- `strategy-notes/factors-crypto-perp.md`
- `strategy-notes/factors-ai-supply-chain.md`（待建）

清单先登记后跑。改动因子定义或门槛要在登记表里另起一节标注，不得静默修改。

## 加密线

### 运行

```bash
python3 tools/factors/crypto-perp/collect.py              # 全量：长历史 + 30 天窗口
python3 tools/factors/crypto-perp/collect.py --only window # 只刷 30 天窗口（建议每日）
python3 tools/factors/crypto-perp/collect.py --no-proxy    # 直连
```

依赖：仅 Python 标准库（采集器零第三方依赖）。因子计算脚本使用 `pandas`/`numpy`。

### 输出

数据落在 `data/raw/binance-futures/`（`data/.gitignore` 已忽略，不入库）：

| 文件 | 内容 | 窗口 |
|---|---|---|
| `BTCUSDT_perp_1d.csv` | 永续日线 OHLCV + taker 买量 | 长历史 |
| `BTCUSDT_spot_1d.csv` | 现货日线 OHLCV + taker 买量 | 长历史 |
| `BTCUSDT_funding.csv` | 资金费结算（8h 一条） | 长历史 |
| `BTCUSDT_oi_1d.csv` | 未平仓量 | **30 天窗口，累积** |
| `BTCUSDT_lsr_global.csv` | 全体账户多空比 | 30 天窗口，累积 |
| `BTCUSDT_lsr_top_account.csv` | 大户账户比 | 30 天窗口，累积 |
| `BTCUSDT_lsr_top_position.csv` | 大户仓位比 | 30 天窗口，累积 |
| `BTCUSDT_taker_ratio.csv` | taker 买卖量比 | 30 天窗口，累积 |
| `_state.json` | 各数据集行数与最后采集时间 | — |

### 窗口约束（关键）

Binance 的 `/futures/data/*` 系列（OI、多空比、taker 比）**只保留最近 30 天**。

⇒ 这些数据集是**累积型**：每次运行把新窗口并入本地文件，历史随时间增长。**不启动采集，这些序列永远只有 30 天。**

### 网络

`fapi.binance.com` 与 `api.binance.com` 需经本机代理，默认 `http://127.0.0.1:7897`。
`data-api.binance.vision` 可直连，但只镜像现货 `/api/v3/*`，不含期货 `/fapi/*`。

代理地址可用 `--proxy` 覆盖；换网络环境后先跑一次探测（脚本启动时会打印 `probe:` 行确认可达性）。

## 美股 AI 产业链线

状态：**未建**。数据源待定。

已探明的候选（2026-09-20 实测）：

| 源 | 状态 |
|---|---|
| AlphaVantage `TIME_SERIES_DAILY` | 200（demo key 仅限 IBM，正式用需免费注册 key，额度约 500 次/日） |
| `api.nasdaq.com/api/quote/<sym>/historical` | 200，但需 `fromdate` 参数 |
| Yahoo Finance chart API | 429/403，当前不可用 |
| Stooq CSV | 返回 JS 反爬挑战页，取不到数据 |
| FRED `fredgraph.csv` | 200，宏观序列可直接用（已验证 DGS10） |

建线前需先决定：标的池（从 `research/` 的 AI 产业链标的取）、因子域（基本面 vs 价格行为）、数据源与授权。
