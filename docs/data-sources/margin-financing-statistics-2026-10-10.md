# 融资余额数据源：FINRA Margin Statistics 与 A 股两融——上游、字段与口径边界

核验日期：2026-10-10。范围：官方网页与公开接口实测（未登录、未调用任何鉴权接口）；本文记录来源与口径，不提供交易建议，不代表完整供应商审计。

## 与现有集合的关系

- 路由入口仍为 [data-sources.jsonl](../../.agents/data-sources.jsonl)，合规状态仍由 [PUBLIC-SOURCE-POLICY.md](../../.agents/PUBLIC-SOURCE-POLICY.md) 定义。
- 本轮新增两条 free 来源，均按固定字段顺序追加，不改动既有条目：
  - `finra-margin-statistics`（US，regulator，`PUBLIC_NO_AUTH`，月频）——FINRA 客户融资余额（debit balances）与两项 free credit balances；
  - `cn-margin-daily`（CN_A，aggregator，`PUBLIC_NO_AUTH`，日频）——A 股融资融券余额，程序化通道为东方财富 datacenter REST API，上游为沪深交易所每日披露的券商申报。
- 与既有条目的分界：`finra-short-interest` 是空头持仓（short interest），与融资余额是多空两个不同维度，不得互相替代；A 股做空侧的对应检查仍走既有 `eastmoney-f10`（其 `use_when` 已含融券余额），本轮 `cn-margin-daily` 专注融资/两融存量。
- **港股未纳入本轮**：没有与 FINRA debit balances 等价的「券商客户融资余额」公开序列。已公开的替代是 HKMA 月度「股票经纪」贷款（银行→券商，上游供给端代理）与 HKEX 每日沽空成交（借券流）。两者与客户余额既不同口径也不同步，需要时再单独立行并写清代理关系，当前不并入融资余额路由。

## 实测记录（2026-10-10 访问）

### 美股 FINRA Margin Statistics

入口：`finra.org/investors/learn-to-invest/advanced-investing/margin-statistics`（`PUBLIC_NO_AUTH`）。页面直接给出表格与 Excel 下载，无需登录。Rule 4521(d) 要求会员券商在月末最后一个营业日申报：全部 margin accounts 的 debit balances 合计，以及 cash accounts 与 margin accounts 的 free credit balances 合计。FINRA 于参考月之后第三个星期发布。

单位：百万美元。最近三期（访问时页面可见值）：

| 月份 | Debit Balances（客户融资余额） | Free Credit（现金账户） | Free Credit（Margin 账户） |
|---|---:|---:|---:|
| Aug-26 | 1,453,832 | 207,641 | 217,499 |
| Jul-26 | 1,417,225 | 205,132 | 217,305 |
| Jun-26 | 1,502,072 | 217,441 | 223,412 |

派生读数（`MODEL_DERIVED`）：Jul→Aug 环比 +36,607（+2.58%）；Jun→Jul 环比 -84,847（-5.65%）。7 月为单月大幅去杠杆月，8 月回补至接近前高。

### A 股两融余额

官方入口：上交所融资融券汇总页 `sse.com.cn/market/othersdata/margin/sum/`（页面可达，口径说明文字可见：本日融资融券余额＝本日融资余额＋本日融券余量金额；数据由券商申报），数值表动态加载。本轮数值实测走东方财富 datacenter API（`reportName=RPTA_RZRQ_LSHJ`，无鉴权、直连返回 JSON）。

最近三个交易日（访问时返回的最新三条）：

| 日期 | 融资余额（元） | 融资融券余额（元） | 占流通市值 | 融券余额（元） |
|---|---:|---:|---:|---:|
| 2026-10-08 | 2,544,596,119,081 | 2,574,159,557,685 | 2.66% | 29,563,438,604 |
| 2026-09-30 | 2,540,456,896,977 | 2,569,852,631,466 | 2.62% | 29,395,734,489 |
| 2026-09-29 | 2,579,689,104,835 | 2,608,990,447,105 | 2.67% | 29,301,342,270 |

派生读数（`MODEL_DERIVED`）：10 日融资净买入（`RZJME10D`）= -634.9 亿元，即近两周融资盘净偿还。融券余额仅 296 亿元、占比长期低于 0.2%。

## 字段口径

FINRA 三项序列均为**存量**（月末时点）：

- `Debit Balances in Customers' Securities Margin Accounts`：客户融资买入的未偿还借款，即 margin debt；
- `Free Credit Balances in Customers' Cash Accounts` 与 `…in Securities Margin Accounts`：客户未投入使用现金。「现金↔融资」的迁移方向本身即是风险偏好读数。

A 股 API 主要字段（`ALL` 返回）：`RZYE` 融资余额、`RZMRE` 融资买入额、`RZCHE` 融资偿还额、`RZJME` 融资净买入、`RQYE` 融券余额、`RQYL` 融券余量、`RZRQYE` 融资融券余额、`RZYEZB` 融资余额占流通市值百分比、`LTSZ` 流通市值。金额单位为元；`RZYEZB` 为百分数。

## 跨市场口径警告

| 市场 | 测的东西 | 统计层级 | 频率 |
|---|---|---|---|
| US | 券商**客户**融资余额 | 下游需求端（客户欠券商） | 月频，滞后 2-3 周 |
| CN_A | 信用账户**融资+融券**余额 | 下游需求端 | 日频，T+1 |

绝对水平不可横比（美元/元、客户范围、标的范围均不同）。可用的是各自的 MoM 变化方向与占市值比。港股链条（HKMA→券商贷款、HKEX 沽空）位置另论，见上文「与现有集合的关系」。

## 局限与失效场景

1. **杠杆读数在系统性去杠杆中滞后且失真。** 序列是存量，月频更慢；强平发生后才体现。把「余额回落」当作见底信号会倒因为果——它是结果，不是前瞻。
2. **口径台阶。** FINRA 明示券商申报方法变更会造成月度不可比；A 股标的调入调出影响汇总余额。跨期比较前核对口径变动，不把台阶读成情绪变化。
3. **覆盖不全。** 两者都不含 prime broker gross margin、基金与自营杠杆、期权保证金杠杆、境外信用余额。读「全市场杠杆」时这是下限。
4. **融资余额回落有非情绪解释。** 上涨后主动降杠杆、标的调整、机构行为都会造成下降，不能一律解读为看空。

## 复现方式

- FINRA：打开入口页读取表格，或下载 `margin-statistics.xlsx`（1997-01 起）。
- A 股：`GET https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPTA_RZRQ_LSHJ&columns=ALL&pageNumber=1&pageSize=5&sortColumns=dim_date&sortTypes=-1`，取最新记录。注意该源是聚合层，引用口径时向上回源交易所披露页。

## 核验状态与复用检查

- 2026-10-10 实测：FINRA 页面与表格可读、Excel 下载路径在页面可见；东财 API 直连返回 JSON 成功（`success: true`）。均为当日页面/接口状态，不证明长期稳定。
- 未做：FINRA 历史 Excel 逐值复核；交易所披露页动态数值表抓取；两市场与官方申报值的逐笔对账。这些缺项保留为未核验，不以聚合层数值冒充交易所申报。
- 复用时：确认页面/接口可达 → 固定参考月或交易日 → 记录单位与是否为存量 → 区分 fact（申报值）与 `MODEL_DERIVED`（环比、占比推算）→ 缺失即标 `SOURCE_UNAVAILABLE`，不以内插或估算填充。
