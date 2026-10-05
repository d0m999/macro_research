# jev-ling-repro — 复刻「trade the news」最小闭环

对 X @wquguru 那条推文（[status/2101612397882671345](https://x.com/wquguru/status/2101612397882671345)）
所述双模型工作流的**独立最小实现**。方法与原版的拆解见
`../jev-ling-trade-the-news-2026-09-20.md`。

目标是验证一件事：**「日报 → 概率决策 → 回测 → 可回放仪表盘 → 出片」这条链路能不能自己跑通。**

## 一行跑通

```bash
node fetch_data.mjs                       # 真实行情 + 真实新闻
node decide.mjs --source rule             # 决策（规则替代源；接真 Jev 用 --source jev）
node backtest.mjs                         # 概率→仓位→盯市→净值
node make_dashboard.mjs                   # 生成 out/dashboard.html
python3 record.py                         # playwright 逐帧 → mp4
# 或：bash run.sh
```

`run.sh` 把上面五步串起来，并在结尾打印自检。

## 目录

| 文件 | 作用 |
|---|---|
| `fetch_data.mjs` | 采集。K 线走 `data-api.binance.vision`（免密钥）；新闻走公开 RSS，按 UTC 日分桶 |
| `decide.mjs` | 判断腿。`jev` = 真实调用 TypeSafe Jev 1.13；`rule` = 确定性规则替代 |
| `backtest.mjs` | 回测引擎（纯代码）。概率→目标权重→真实小时 K 线盯市→净值 |
| `make_dashboard.mjs` | 生成单文件回放仪表盘（1280×720，无外部依赖） |
| `record.py` | playwright 逐帧截图 → ffmpeg 合成 mp4 |
| `data/` | 采集产物（klines / news / briefs） |
| `out/` | 决策、回测、仪表盘、帧序列、成片 |

## 本次实跑结果（真实数据）

窗口 **2026-09-17 → 2026-09-20**（4 个持仓日），标的 BTC / ETH，本金 $100,000，
手续费 10bp 单边，小时级盯市。

| | 期末净值 | 收益 |
|---|---|---|
| 本策略（规则替代源） | $100,798.78 | **+0.80%** |
| 等权买入持有 | $107,846.68 | **+7.85%** |

超额 **−7.05%**，盈利日 4/4，最大回撤 0.00%。手续费合计 $101。

失败原因很直白：规则源给出的仓位极低（敞口 4%→8%→78%→62%），而这段行情是单边上涨，
低敞口直接导致跑输。**这与作者自己的结论同向** —— 他的动量策略也没跑赢等权买入持有
（+6.71% vs +13.2%）。

## 已实现的纪律

1. **无未来函数**。持仓日 D 的决策在 D 的 00:00 UTC 做出，只用 **D−1 日已完整发布**的标题；
   成交价取 D 日 00:00 那根小时 K 的**开盘价**；净值用 D 日的**收盘价**盯市。
2. **原始数据不伪造**。网络不通的源只记 `skipped`，不补假数据；不手写任何价格或新闻。
3. **决策源显式标注**。产物里带 `decisionSource` 字段，仪表盘页脚也照实写。
   缺密钥跑 `--source jev` 会**直接报错退出**，不会静默回退到规则源。
4. **每个脚本末尾自检**。打印关键数值（K 线条数、每日标题数、决策、净值、帧数）。

## 与原版的差异（读结论前必看）

| # | 原版 | 本实现 | 原因 |
|---|---|---|---|
| 1 | 77 个持仓日 | **4 个** | 免密钥的 RSS 只回溯到 09-16；原版靠自建 NewsHub 攒了三个月 |
| 2 | 决策 = Jev 1.13 真实调用 | **规则替代** | 本机无 `OPENROUTER_API_KEY` |
| 3 | 展示 = Ling-3.0-flash-VL 看设计稿写前端 | **脚本生成** | 同上 |
| 4 | 3 策略（动量/逆向/宏观） | 1 套规则 | 最小闭环 |
| 5 | 5 标的（BTC/ETH/SPY/QQQ/XAU） | 2 标的（BTC/ETH） | 只有这两个有 24/7 小时级真实数据 |
| 6 | state 含当日持仓 | 不含持仓 | 最小闭环简化；接真 Jev 时应在回测循环内调用以传入实时持仓 |
| 7 | 未提手续费 | 10bp 单边 | 更保守 |

**所以本目录的数字不能与作者的数字并列比较**，它只证明链路可跑。

## 接真实模型要做什么

**Jev**（判断腿）
```bash
export OPENROUTER_API_KEY=sk-or-v1-...
node decide.mjs --source jev && node backtest.mjs && node make_dashboard.mjs && python3 record.py
```
- 模型 ID `typesafe/jev-1.13`，端点 `POST https://openrouter.ai/api/alpha/decisions`。
  **不是 chat/completions**，chat SDK 调不通。
- 请求体 `{ model, state, questions }`；每个标的是一个 `choice` 型问题，
  `criteria` 给「买/不动/卖」三档的语义说明。
- 应答在 `answers.<标的>`：`choice` + `probabilities`（三档完整分布）+ `confidence`。
  下游只吃**概率**，不吃标签。
- 要拿到原版 87 秒的效率，必须用「**一个请求并行问多题**」：原版 1155 次决策 = 77 天 × 3 策略 × 5 标的，
  但调用只有 **231 次**（每次并行问 5 个标的）。本实现的 `decideWithJev()` 已是这个形状。

**Ling**（展示腿）
把 `make_dashboard.mjs` 换掉：给它一张可视化设计稿截图，让它照着重写 `out/dashboard.html`，
**保留 `window.__seek(i)` 和 `window.__total` 两个接口**，`record.py` 就能原样复用。
- 模型 ID `inclusionai/ling-3.0-flash-vl:free`（发布期免费；付费档 $0.06/M 入、$0.18/M 出）
- 它原生吃图，且带「观察→行动→验证→修正」闭环，适合设计稿→前端。

## 本机环境坑（实测）

| 现象 | 原因 | 处理 |
|---|---|---|
| `curl` 对任何域名返回 `http=000` | 沙箱只放行部分出网 | 改用 Node 内置 `fetch`（可用），或走已登录 Chrome 的 CDP |
| playwright 报 `Executable doesn't exist ... chromium_headless_shell-1194` | 本机 playwright 1.56 期望的构建号与实际下载的 1234 不符 | `record.py` 改为 `channel="chrome"` 走系统 Chrome，免下载浏览器 |
| Python 里 `subprocess` 找不到 `ffmpeg` | 该进程 PATH 不含 `/opt/homebrew/bin` | `record.py` 的 `_tool()` 逐一兜底绝对路径 |
| 标题里出现 `Glassess&#39;` | RSS 标题含 HTML 实体 | `fetch_data.mjs` 的 `decodeEntities()` 先解码，页面侧再做 HTML 转义 |
