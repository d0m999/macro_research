# GLW 数据获取 workflow 验证总结

验证对象：`GLW` / `Corning Incorporated` / `CIK 0000024741`
验证日期：2026-08-19（UTC）

## 结论

本次 session 验证了这套 workflow 可以获取一部分公开、结构稳定的一手数据，也可以把公司 IR 等没有统一 API 的来源登记为半自动结果；但它不能把所有数据都变成“免费、稳定、可自动抓取、可缓存和可再分发”的统一资产。

因此，当前结果支持以下定位：

> 公开来源优先、用户数据可插拔、付费能力可选、缺失项显式降级的 Codex 公司分析工作流。

## 逐类结果

| 类别 | 本次验证结果 | 是否允许继续推导 |
|---|---|---|
| SEC EDGAR | `PASS`：submissions 和 XBRL JSON 无 key 成功；archive HTML 在本地 curl 与 Web 通道存在差异 | 可以，需保留 filing、期间、accession 和访问通道 |
| 美国财政部利率 | `PASS`：官方 XML 成功取得 2026-08-18 的 2Y/5Y/10Y/30Y | 可以，绑定 observation date 和源文件 hash |
| FRED | `PARTIAL`：无 key REST API 返回 400；官方 CSV export 成功 | 可以做受限序列；不能声称 REST API 无凭证 |
| 公司 IR | 以官方域名限定搜索、打开页面、校验文档的半自动流程可行 | 可以，逐个登记 URL、发布日期、期间和获取时间 |
| 公司新闻稿/演示材料 | 官方 Q2 新闻稿和投资者活动材料可定位；动态页面或大 PDF 仍需记录访问通道和 bytes 状态 | 可以，但不得把搜索摘要当源文件 |
| 完整电话会 transcript | 官方 IR 可确认 webcast；本次没有取得可验证的完整逐字稿 | 不得评价 Q&A、语气或回避问题 |
| 实时/历史行情 | 本次没有券商/供应商 entitlement 或用户导出文件 | 不计算 beta、事件收益或可信历史价格序列 |
| 分析师共识 | 公司 guidance 与 Street consensus 可分开；本次没有取得授权 consensus 数据 | 不输出可靠 beat/miss vs. Street |
| 行业报告/市场份额 | 10-K 可提供业务、竞争者和公司自述；没有独立权威的完整份额数据库 | 不伪造精确 TAM 或市场份额 |
| 客户/供应商关系 | SEC 可提供客户集中度和部分合同/供应链披露；不是全量关系库 | 只能输出披露范围内的关系证据，缺失处标记不充分 |

## 统一降级规则测试

```text
AUTH_REQUIRED             -> FRED REST API 无 key
SOURCE_UNAVAILABLE        -> 没有可验证的完整 transcript、行情或 consensus
USER_UPLOAD_REQUIRED      -> 券商/TradingView CSV、付费 Excel、行业报告等
PARTIAL                   -> 官方 CSV fallback、公司自述、有限客户/供应商披露
PASS                      -> SEC JSON、Treasury XML，以及可验证的官方文档发现路径
```

任何一个降级状态都不能在后续分析中静默升级为完整数据。尤其不能用搜索结果摘要、随机第三方 transcript、网页展示价格或公司 guidance 代替其对应的授权/原始数据。

## 适配器结论

```text
确定性 API adapter  -> SEC / Treasury / 已登记 key 的 FRED / 用户自有 API
Web document adapter -> 公司 IR / 政府页面 / 行业协会的 discover → open → validate → register → extract
User-file adapter    -> 行情导出 / transcript / consensus / 行业报告 / 用户研究材料
```

本次不引入 MCP server、交易执行层、数据库或后台爬虫；先用可审计的本地 JSON/Markdown 输出验证边界。

## 一手来源入口

- [SEC EDGAR API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [Treasury Daily Interest Rate XML Feed](https://home.treasury.gov/treasury-daily-interest-rate-xml-feed)
- [FRED API key requirements](https://fred.stlouisfed.org/docs/api/fred/v2/api_key.html)
- [Corning Q2 2026 financial results](https://investor.corning.com/news-and-events/news/news-details/2026/Cornings-Strong-Second-Quarter-2026-Financial-Results1-Demonstrate-Progress-on-Recently-Upgraded-Springboard-Plan/default.aspx)
- [Corning events and presentations](https://investor.corning.com/investor-relations/news-and-events/events-and-presentations/default.aspx)

本报告只记录验证结果；未提交、未推送，也未修改仓库中既有的 `fundamental-research/` 工作。
