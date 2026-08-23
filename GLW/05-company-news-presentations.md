# GLW / Corning Inc — 公司新闻稿与演示材料

> 研究状态：`AVAILABLE`（Q2 2026 官方新闻稿、8-K 附件和演示 PDF 已取得；网页正文以 Browser-like web 核验）
> retrieved_at：`2026-08-19T20:05:00+09:00`
> issuer：`Corning Incorporated`
> reporting_period：Q2 2026（截至 2026-06-30，业绩发布 2026-07-28）；补充 FY2025/Q4 2025

## 获取路径、费用与自动化边界

- 获取路径：用官方域名 `web search` 发现新闻和事件，再用 `Browser-like web` 核验正文；对 Corning/Q4 CDN PDF 与 SEC `8-K` 使用 `direct URL` 下载并计算 SHA-256。
- 费用/权限：Corning 新闻稿、IR 页面、SEC 8-K 和公开演示材料可公开阅读；这不自动授予将完整 PDF、图表或演示内容再分发给第三方的权利。
- 稳定 API：Corning 新闻/IR 页面没有发现统一稳定 API；SEC filing 元数据和 XBRL 有稳定 API，但新闻稿和演示仍按文档处理。
- 自动抓取、缓存、再分发边界：可在低频、描述性 `User-Agent` 下登记 URL、下载内部验证所需的 PDF 并保存 hash；遵守 SEC Fair Access 和 Corning/Q4 CDN 的站点条款。不要把搜索摘要当事实，不做绕过 Cloudflare、验证码或登录的大范围抓取，不公开转存完整材料。

## 实际摘录

[Corning 的 Q2 2026 官方新闻稿](https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2026/07/cornings-strong-second-quarter-2026-financial-results-demonstrate-progress-on-recently-upgraded-springboard-plan.html) 与 [IR 版本](https://investor.corning.com/news-and-events/news/news-details/2026/Cornings-Strong-Second-Quarter-2026-Financial-Results1-Demonstrate-Progress-on-Recently-Upgraded-Springboard-Plan/default.aspx) 的可核验事实如下：

- Q2 core sales 为约 `$4.74B`，同比增长 `17%`；core EPS 为 `$0.78`，同比增长 `30%`。
- Optical Communications sales 为 `$2.072B`，同比增长 `32%`；其中 Enterprise Networks 增长 `65%`；Solar 增长 `90%`。
- 公司给出的 Q3 2026 outlook 为 core sales `$4.9B–$5.0B`、core EPS `$0.85–$0.89`。这是公司 guidance，不是 analyst consensus。
- Q2 GAAP sales 为 `$4.505B`，net income 为 `$559M`，diluted EPS 为 `$0.64`；core net income 为 `$680M`。
- 新闻稿披露了与 Amazon 的多年期、数十亿美元级协议，以及与 NVIDIA 的长期合作；披露内容涉及光纤、光缆、连接产品和美国制造扩产。合作关系事实可以登记，但不能据此推断全部订单金额、利润率、客户集中度或未来实现结果。
- `2026-07-28` 的 [Q2 earnings call presentation with appendix PDF](https://s203.q4cdn.com/212458750/files/doc_financials/2026/q2/2026-07-28-Second-Quarter-Earnings-Call-Presentation-with-Appendix.pdf) 已下载并核验为 PDF；它可作为管理层演示材料，但不替代逐字 transcript。

## 来源登记

| url | official_domain | document_type | published_at | issuer | reporting_period | sha256 | 获取路径 / 实际状态 |
|---|---|---|---|---|---|---|---|
| https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2026/07/cornings-strong-second-quarter-2026-financial-results-demonstrate-progress-on-recently-upgraded-springboard-plan.html | `corning.com` | 公司新闻稿 HTML | 2026-07-28 | Corning Incorporated | Q2 2026 | 未保存 bytes（Browser-like web 正文已核验；direct curl 返回 challenge，未将 challenge 计为源文件） | `web search` → `Browser-like web`；正文可核验 |
| https://investor.corning.com/news-and-events/news/news-details/2026/Cornings-Strong-Second-Quarter-2026-Financial-Results1-Demonstrate-Progress-on-Recently-Upgraded-Springboard-Plan/default.aspx | `investor.corning.com` | IR 新闻稿 HTML | 2026-07-28 | Corning Incorporated | Q2 2026 | 未保存 bytes（动态页面） | `web search` → `Browser-like web`；与公司新闻页交叉核验 |
| https://s203.q4cdn.com/212458750/files/doc_financials/2026/q2/Corning-Incorporated-Second-Quarter-2026-Earnings-Release-with-Financials-2026-07-28.pdf | `s203.q4cdn.com`（Corning IR Q4 CDN） | earnings release PDF | 2026-07-28 | Corning Incorporated | Q2 2026 | `90343ca05cb5ed748d9772acfda228c7f813d8ad8c2adec989cf3d05b1fe4eed` | `web search` → `direct URL`；已下载 20 页 PDF并提取文本 |
| https://s203.q4cdn.com/212458750/files/doc_financials/2026/q2/2026-07-28-Second-Quarter-Earnings-Call-Presentation-with-Appendix.pdf | `s203.q4cdn.com`（Corning IR Q4 CDN） | earnings call presentation PDF | 2026-07-28 | Corning Incorporated | Q2 2026 | `4473e528330e699796aca5aa5d608337ffb8161bec7040ce62c56adb9fb07d08` | `web search` → `direct URL`；已下载并核验 PDF |
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000253/glw-20260728xex99xq22026.htm | `sec.gov` | Form 8-K Exhibit 99.1 HTML | 2026-07-28 | Corning Incorporated | Q2 2026 | `a2c7d546b7a4e47e985c95c3431ac49ccf94c1c5ee44115cff1a53d8e3b1ef0e` | `direct URL`；已下载并核验为 8-K 业绩附件 |
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000253/glw-20260728.htm | `sec.gov` | Form 8-K primary HTML | 2026-07-28 | Corning Incorporated | Q2 2026 | `d0f49f7e7ad856885c8977fc9e3029605f886b20fb94d3c02983f4f7f57f8428` | `direct URL`；已下载并核验 filing |
| https://s203.q4cdn.com/212458750/files/doc_financials/2025/q4/Corning-Incorporated-Fourth-Quarter-2025-Earnings-Release-with-Financials-2026-01-28.pdf | `s203.q4cdn.com`（Corning IR Q4 CDN） | earnings release PDF | 2026-01-28 | Corning Incorporated | Q4/FY 2025 | `81a437bd638c4dd27bd484aa6a279d833edb5a8b236215e2101ff791c4f4410c` | `web search` → `direct URL`；已下载并核验 PDF |

## 降级规则

- 公司 guidance 只能标记为 `COMPANY_GUIDANCE`，不能转换为 Street consensus、beat/miss 或分析师预期。
- 搜索摘要、转载页面或无法验证 issuer/period 的附件不进入事实层；若官方正文和 SEC 附件不一致，保留冲突并回到原始 filing。
- 演示材料可以支持管理层叙述和图表，但没有逐字稿时不得把演示页扩展成 Q&A、语气或未披露因果。
- PDF 只有在实际下载 bytes 并计算 hash 后才登记为可校验文件；动态页面和被拦截页面记为“未保存 bytes”，不伪造 hash。
