# GLW — 实时/历史行情

状态：`SOURCE_UNAVAILABLE`；可登记官方入口，但本次为 `USER_UPLOAD_REQUIRED` / `ENTITLEMENT_REQUIRED`

## 为什么没有直接填入一个“免费行情”

行情的公开可见性、稳定 API、实时 entitlement、历史回溯权利、缓存和再分发权限是不同问题。本次 session 没有连接券商账户、TradingView 导出、行情供应商 key 或用户上传的 CSV，因此不把随机网页价格当作可复现的 GLW 行情资产。

## 实际尝试

### 官方 Corning IR stock page

| 字段 | 值 |
|---|---|
| `url` | https://investor.corning.com/stock-info/default.aspx |
| `official_domain` | `investor.corning.com` |
| `document_type` | 动态 HTML stock quote / chart / historical quote UI |
| 获取方式 | Web open + click 探针 |
| 结果 | 页面确认存在 `Stock Quote`、`Stock Chart`、`Historical Stock Quote` 和 investment calculator，但当前 Web HTML payload 没有可登记的报价数据行 |
| `sha256` | 未登记；没有下载到可验证的报价 payload bytes |

Corning 的 Investor FAQ 也只把当前/历史价格指向 stock quote/history 页面；这证明官方入口存在，不证明本次 session 拥有一个稳定、无 key 的数据 API。

### TradingView GLW page

```text
https://www.tradingview.com/symbols/NYSE-GLW/
```

Web 搜索可以发现 GLW 图表页，但搜索摘要不能直接进入报告；页面没有向本次工作流提供一个可登记的原始历史 OHLCV 文件或公开稳定 API。TradingView 画面和 Pine feed 也不能自动等同于券商 API 或可再分发数据。

### 本地用户文件

当前仓库没有本次验证专用的 GLW 券商/TradingView 导出 CSV 或 Excel；因此没有进行 beta、波动率、收益曲线或事件窗口计算。

## 降级规则

| 需要的输出 | 当前状态 | 允许的下一步 |
|---|---|---|
| 实时价格/盘口 | `ENTITLEMENT_REQUIRED` | 用户提供有权限的 broker/vendor adapter；不从网页复制填充 |
| 历史 OHLCV | `USER_UPLOAD_REQUIRED` | 上传券商或 TradingView CSV，记录原始文件 SHA-256、时区、复权口径 |
| beta / 事件收益 | `BLOCKED_BY_INPUT` | 先取得已验证的历史序列，再按指定基准和窗口计算 |
| 分钟级或 tick 数据 | `ENTITLEMENT_REQUIRED` | 需要明确供应商、市场数据权限和缓存/再分发条款 |

## 推荐的 user-file schema

```text
date,time,open,high,low,close,adj_close,volume
source,exchange,symbol,timezone,adjustment_method,retrieved_at,sha256
```

## 来源

- [Corning official stock info](https://investor.corning.com/stock-info/default.aspx)
- [Corning Investor FAQ](https://investor.corning.com/resources/investor-faqs/default.aspx)
- [TradingView GLW page](https://www.tradingview.com/symbols/NYSE-GLW/)
