# GLW / Corning Inc — 行业与市场份额

> 研究状态：`PARTIAL`；当前独立数值市场份额：`SOURCE_UNAVAILABLE`
> retrieved_at：`2026-08-19T20:05:00+09:00`
> issuer：`Corning Incorporated`、SEC、TIA/FBA（按来源分别登记）
> reporting_period：FY2025 公司披露；行业协会页面为 2026 年行业背景；没有采用过时历史份额作为当前值

## 结论

官方 2025 `10-K` 可提供 Corning 的业务边界、竞争者和公司自述地位，但没有给出本次需要的当前、独立、可复核的 Optical Communications 或 Display 数值市场份额。Corning 自己的“leader”或“largest worldwide producer”属于公司披露，应标为 `COMPANY_CLAIM`，不能自动转换成第三方市场份额百分比。

本次还核验了 TIA 和 Fiber Broadband Association 的行业页面：它们能证明 Corning 处于行业联盟/技术协作背景，但没有提供 GLW 当前市场份额数字。没有使用随机商业市场研究网页补齐精确百分比，也没有把历史 USITC 材料当作当前市场份额。

## 获取路径、费用与自动化边界

- 获取路径：`web search` 限定 Corning、SEC、政府和行业协会域名；用 `Browser-like web` 打开官方正文；SEC `10-K` 用 `direct URL` 下载并计算 hash。
- 费用/权限：SEC、Corning、TIA 和 FBA 页面可公开阅读；行业协会页面的全文、图表和再分发仍受各站点条款约束。公开阅读不等于授权建立商业数据库。
- 稳定 API：没有发现官方、稳定、持续更新且直接给出 Corning 当前市场份额的 API。SEC API 能提供公司申报事实，但不能凭空生成行业份额。
- 自动抓取、缓存、再分发边界：只抓取/登记官方页面和已授权文件；采用低频访问、缓存 URL 与 hash；不抓取随机市场研究站、不绕过限制，不把公司自述或行业成员名单再加工成未经来源支持的百分比。

## 实际摘录

- [Corning FY2025 10-K](https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm) 披露 Optical Communications 的竞争者包括 Amphenol、Fujikura/AFL、Sumitomo、Prysmian；Display 部分称 Corning 是平板显示玻璃基板的“largest worldwide producer”，并列出 AGC、Nippon Electric Glass 等竞争者。这里的份额相关措辞是公司申报，不是独立测量。
- [Corning Optical Communications market page](https://www.corning.com/worldwide/en/markets/Optical-Communications-Market.html) 使用“leader”等公司定位语言；这可作为公司自述背景，不能作为当前百分比。
- [TIA Fiber Optics Technology Consortium](https://standards.tiaonline.org/resources/fiber-optics-technology-consortium-tia) 说明其为行业技术协作/信息平台并列出成员，包括 Corning；没有给出 Corning 份额。
- [Fiber Broadband Association 2026 MSA collaboration](https://fiberbroadband.org/2026/03/11/fiber-optics-industry-leaders-announce-collaboration-to-define-a-new-multicore-fiber-design-optimized-for-ai-data-center-campuses/) 披露 AFL、Corning、Sumitomo、TeraHop 的行业合作；合作成员和技术协作不等于市场份额。
- `SOURCE_UNAVAILABLE`：当前、独立、按地区/产品线可复核的 GLW market share percentage；可用降级项是公司自述、竞争者列表和行业背景，不能输出精确数值 TAM/share。

## 来源登记

| url | official_domain | document_type | published_at | issuer | reporting_period | sha256 | 获取路径 / 实际状态 |
|---|---|---|---|---|---|---|---|
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm | `sec.gov` | Form 10-K HTML | 2026-02-12 | Corning Incorporated | FY ended 2025-12-31 | `4e4ef36fd33448c16195cf4f924dcfc3e6f5c5ecdc827558aa9ac63f4f58d847` | `web search` → `direct URL`；已下载 bytes，核验竞争和公司定位披露 |
| https://www.corning.com/worldwide/en/markets/Optical-Communications-Market.html | `corning.com` | 公司市场/产品页 HTML | 页面未单独标注 | Corning Incorporated | 截至 retrieved_at | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；仅公司自述 |
| https://standards.tiaonline.org/resources/fiber-optics-technology-consortium-tia | `standards.tiaonline.org` | 行业协会 consortium 页面 | 页面未单独标注 | TIA | 行业背景 | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；无份额数字 |
| https://fiberbroadband.org/2026/03/11/fiber-optics-industry-leaders-announce-collaboration-to-define-a-new-multicore-fiber-design-optimized-for-ai-data-center-campuses/ | `fiberbroadband.org` | 行业协会新闻稿 | 2026-03-11 | Fiber Broadband Association | 2026 行业协作 | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；无份额数字 |

## 降级规则

- 只有公司自述时，状态保持 `PARTIAL / COMPANY_CLAIM`；不输出“GLW 占 X%”等独立结论。
- 没有当前独立百分比时，标 `SOURCE_UNAVAILABLE`，不使用随机网页、SEO 摘要或无法验证方法论的商业报告补齐。
- 历史市场份额即使来自政府/USITC，也必须单独标明历史期间、产品边界和不可代表当前；本次不将其并入当前估值输入。
- 若用户提供有许可的行业报告或 Excel/CSV，应登记供应商、发布日期、覆盖区域、定义、原文件 hash 和再分发边界后再使用。
