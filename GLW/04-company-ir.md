# GLW / Corning Inc — 公司 IR 与基础申报通道

> 研究状态：`AVAILABLE`（官方 IR 通道可定位；结构化事实优先取 SEC）
> retrieved_at：`2026-08-19T20:05:00+09:00`
> issuer：`Corning Incorporated`（NYSE: `GLW`，CIK `0000024741`）
> reporting_period：截至 retrieved_at；覆盖 FY2025 年报、2026-06-30 季报和 2026-07-28 业绩披露

## 结论

Corning 的官方 IR 入口、Events & Presentations、Quarterly Results 和 SEC Filings 页面均可定位。IR 页面是动态网页，适合人工确认文档入口；没有发现一个由 Corning 公开、稳定且统一覆盖全部 IR 文件的 API。对建模所需的 filing 元数据和 XBRL 事实，本次成功使用 SEC 的 `submissions` 与 `companyfacts` JSON API，无 API key。

本次可验证的最新申报元数据包括：2026-07-29 的 2026-06-30 季报（`10-Q`）、2026-07-28 的业绩披露（`8-K`），以及 2026-02-12 提交的 FY2025 `10-K`。IR 侧的动态索引可能晚于 SEC，因此不能把 IR 页面当前展示内容当成完整 filing 清单。

## 获取路径、费用与自动化边界

- 获取路径：先用限定官方域名的 `web search` 定位入口，再用 `Browser-like web` 打开并核验页面正文；对 SEC JSON/Archive HTML 使用 `direct URL` 下载并计算 SHA-256。
- 费用/权限：Corning IR 页面和 SEC filing 页面可公开阅读；SEC `submissions` 与 XBRL API 不需要认证或 API key。公开可读不等于允许无条件再分发全部网页、PDF 或第三方托管内容。
- 稳定 API：SEC `data.sec.gov/submissions/CIK...json` 与 `data.sec.gov/api/xbrl/companyfacts/CIK...json` 可作为稳定 API 通道；Corning IR 没有发现统一稳定 API。
- 自动抓取、缓存、再分发边界：SEC 自动访问应使用描述性 `User-Agent`、低速率、缓存和退避，并遵守 SEC Fair Access（当前文档说明上限为每秒 10 次）；只保存内部研究所需的响应和哈希，不据此推断再分发权。IR 动态页面不做大范围通用爬虫，发现最终 HTML/PDF 后登记 URL；遇到验证码、登录或明确限制时停止并转为用户上传。
- API 规则依据：[SEC EDGAR Application Programming Interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)、[SEC Developer Resources](https://www.sec.gov/about/developer-resources)。

## 实际摘录

1. [Corning Investor Relations 首页](https://investor.corning.com/investor-relations/default.aspx) 可作为公司 IR 总入口；[Events & Presentations](https://investor.corning.com/news-and-events/events-and-presentations/default.aspx) 展示包括 `Q2 2026 Earnings Call`（2026-07-28）在内的事件；[Quarterly Results](https://investor.corning.com/financials/quarterly-results/default.aspx) 和 [SEC Filings](https://investor.corning.com/investor-relations/financials/sec-filings/default.aspx) 提供财务资料入口。
2. SEC `submissions` JSON 的当前快照列出：`2026-07-29 / 10-Q / accession 0000024741-26-000255 / reportDate 2026-06-30`；`2026-07-28 / 8-K / accession 0000024741-26-000253`；`2026-02-12 / 10-K / accession 0000024741-26-000124`。
3. [FY2025 10-K HTML](https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm) 的报告期为 2025-12-31，提交日为 2026-02-12；它提供分部、竞争、客户集中度和供应链风险等公司一手披露。

## 来源登记

| url | official_domain | document_type | published_at | issuer | reporting_period | sha256 | 获取路径 / 实际状态 |
|---|---|---|---|---|---|---|---|
| https://investor.corning.com/investor-relations/default.aspx | `investor.corning.com` | 公司 IR 首页 | 页面动态，未单独标注 | Corning Incorporated | 截至 retrieved_at | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；入口可用 |
| https://investor.corning.com/news-and-events/events-and-presentations/default.aspx | `investor.corning.com` | Events & Presentations 索引 | 页面动态，未单独标注 | Corning Incorporated | 2026 年事件索引 | 未保存 bytes（动态页面） | `web search` → `Browser-like web`；可定位 Q2 2026 业绩电话会 |
| https://investor.corning.com/financials/quarterly-results/default.aspx | `investor.corning.com` | Quarterly Results 索引 | 页面动态，未单独标注 | Corning Incorporated | Q1/Q2 2026 等季度资料 | 未保存 bytes（动态页面） | `web search` → `Browser-like web`；页面可读但不作为完整清单 |
| https://investor.corning.com/investor-relations/financials/sec-filings/default.aspx | `investor.corning.com` | SEC Filings IR 索引 | 页面动态，未单独标注 | Corning Incorporated | 截至 retrieved_at | 未保存 bytes（动态页面） | `web search` → `Browser-like web`；链接到 SEC 和 Interactive Analyst Center |
| https://data.sec.gov/submissions/CIK0000024741.json | `data.sec.gov` | SEC submissions JSON API | 2026-08-19 快照 | SEC / Corning Incorporated | 最新申报元数据 | `52f611cf4305ea50f0343cb9ba503534bddbed394a5b91cfa8c86df5a50c7025` | `direct URL`；已下载临时 bytes，API 无 key |
| https://data.sec.gov/api/xbrl/companyfacts/CIK0000024741.json | `data.sec.gov` | SEC XBRL companyfacts JSON API | 2026-08-19 快照 | SEC / Corning Incorporated | 多年度 XBRL 事实 | `024d80faa83a89b7b73d16e3a0914f9f8a65eda0c90c7f93bd4974fa7d5e9411` | `direct URL`；已下载临时 bytes，API 无 key |
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm | `sec.gov` | Form 10-K HTML | 2026-02-12 | Corning Incorporated | FY ended 2025-12-31 | `4e4ef36fd33448c16195cf4f924dcfc3e6f5c5ecdc827558aa9ac63f4f58d847` | `direct URL`；已下载临时 bytes并核验报告期 |

## 降级规则

- SEC API 可用时优先用 SEC 的 accession、report date 和 XBRL 事实；IR 页面只用于发现、交叉核验和取得公司材料。
- IR 动态索引无法打开或未展示某一文件时，标记 `SOURCE_UNAVAILABLE`，不以搜索摘要代替正文；改用 SEC filing 或请用户提供文件。
- 申报元数据存在不等于所有经营指标可比；遇到 XBRL 标签、期间或单位不一致时保留原始上下文，不强行拼接。
- 本文只验证获取通道，不把“公开可读”升级为“免费数据授权”或“可再分发授权”。
