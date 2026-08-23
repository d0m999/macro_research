# GLW / Corning Inc — 客户与供应商关系

> 研究状态：`PARTIAL`；完整客户/供应商关系图：`SOURCE_UNAVAILABLE`
> retrieved_at：`2026-08-19T20:05:00+09:00`
> issuer：`Corning Incorporated`（含 SEC filing 与 Corning 官方合作/供应链页面）
> reporting_period：FY2025 10-K；截至 2026-06-30 的 Q2 2026 10-Q；2026-05/06 官方合作披露

## 结论

可靠公开证据可以确认部分客户/合作关系和客户集中度风险，但不足以建立全量客户名单、供应商名单或逐层关系图：

- Corning 官方页面明确披露与 Amazon 的多年期协议、与 NVIDIA 的长期合作；这证明公开披露的合作关系存在，但不证明它们覆盖所有分部、全部收入或全部供应链角色。
- FY2025 10-K 给出了各报告分部的终端客户集中度百分比，但没有列出客户名称。
- Q2 2026 10-Q 披露长期供货协议下的客户押金、合同负债和 warrant；相关叙述本身不提供完整客户/供应商图谱。
- 10-K 和 Corning Supplier Responsibility 页面说明部分关键材料/专有设备存在单一来源或有限供应商风险，但没有可靠公开的完整供应商名单。

## 获取路径、费用与自动化边界

- 获取路径：`web search` 限定 Corning/SEC 官方域名；用 `Browser-like web` 核验 Amazon、NVIDIA 和供应链页面；用 `direct URL` 下载 SEC `10-K`、`10-Q`、Q2 `8-K` 附件和 earnings release PDF。
- 费用/权限：SEC filing 和 Corning 新闻/供应链页面可公开阅读；客户合同、供应商主数据和关系数据库通常属于公司内部、授权数据库或用户数据资产。不能把公开新闻稿再分发成完整商业关系库。
- 稳定 API：SEC filing/XBRL API 可稳定取得申报事实；没有发现 Corning 的客户/供应商关系 API，也没有可靠免费的全量替代。
- 自动抓取、缓存、再分发边界：只登记官方公开关系、披露期间、原始 URL 和 hash；低频访问并遵守 SEC Fair Access/站点条款；不从搜索摘要推断关系，不用供应链新闻、招聘或随机网页补齐未知名称，不绕过登录或付费墙。

## 实际摘录

### 客户侧

- [FY2025 10-K](https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm) 披露 2025 年各分部合并终端客户占该分部净销售额的比例：Optical Communications 为 `2 / 28%`，Display 为 `3 / 59%`，Specialty Materials 为 `2 / 43%`，Automotive 为 `3 / 61%`，Life Sciences 为 `2 / 45%`。这些是集中度事实，不是客户名称或完整关系图。
- [Amazon 与 Corning 官方公告](https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2026/06/amazon-announces-agreement-with-corning-to-boost-us-fiber-optics-manufacturing-creating-1000-advanced-manufacturing-jobs-in-north-carolina.html)（2026-06-08）称 Amazon 与 Corning 达成数十亿美元级协议，Corning 将供应光纤、光缆和连接产品，用于 Amazon 美国数据中心基础设施；公告还称将在 North Carolina 创造约 1,000 个先进制造岗位。金额和未来执行仍以公司披露为准。
- [NVIDIA 与 Corning 官方公告](https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2026/05/nvidia-and-corning-announce-long-term-partnership-to-strengthen-us-manufacturing-for-ai-infrastructure.html)（2026-05-06）称双方建立长期、多年度商业/技术合作，涉及美国光连接制造扩产。该页面是合作关系的一手证据，但不能单独推导完整订单、分部归属或客户集中度。
- [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/24741/000002474126000255/glw-20260630.htm) 披露截至 2026-06-30 合同负债约 `$2.7B`；Q2 记录约 `$0.7B` 净合同负债变动，其中包括一笔约 `$1.0B`、期限至 2029-12-31 的长期供货协议客户押金，部分被向客户发行的约 `$296M` warrant 抵销。相关叙述不提供完整客户关系名单；XBRL 上下文出现 `glw:NVIDIAMember` 只能作为结构化线索，不能在未完成上下文绑定时把全部金额唯一归因给 NVIDIA。

### 供应商侧

- 10-K 的原材料/供应风险披露称，许多材料有替代供应安排，但某些关键材料和专有设备存在单一来源或有限供应商。申报没有提供可复核的全量供应商名称及采购金额。
- [Supplier Responsibility](https://www.corning.com/worldwide/en/sustainability/processes/supply-chain-social-responsibility/supplier-responsibility.html) 称供应商是关键合作伙伴，公司依赖广泛供应商网络，并通过 Supplier Code of Conduct、传导要求和监测管理供应链；页面没有列出供应商名录。
- [Supply Chain Social Responsibility](https://www.corning.com/worldwide/en/sustainability/processes/supply-chain-social-responsibility.html) 说明供应链还包括运输伙伴和合同制造商，并强调责任采购、风险监测和可见性；这仍不是可用于建模的命名关系库。
- `SOURCE_UNAVAILABLE`：完整供应商名单、供应商层级、采购份额、客户—产品—工厂映射和可验证的全量客户关系图。

## 来源登记

| url | official_domain | document_type | published_at | issuer | reporting_period | sha256 | 获取路径 / 实际状态 |
|---|---|---|---|---|---|---|---|
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000124/glw-20251231.htm | `sec.gov` | Form 10-K HTML | 2026-02-12 | Corning Incorporated | FY ended 2025-12-31 | `4e4ef36fd33448c16195cf4f924dcfc3e6f5c5ecdc827558aa9ac63f4f58d847` | `direct URL`；已下载 bytes，核验客户集中度和供应风险 |
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000255/glw-20260630.htm | `sec.gov` | Form 10-Q HTML | 2026-07-29 | Corning Incorporated | Quarter ended 2026-06-30 | `5ce0dc355e9ec6c0d9131ad9e698e8a2bd9951426ee3ce8f51d9b7d0c8980ac5` | `direct URL`；已下载 bytes，核验客户押金/合同负债披露 |
| https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2026/06/amazon-announces-agreement-with-corning-to-boost-us-fiber-optics-manufacturing-creating-1000-advanced-manufacturing-jobs-in-north-carolina.html | `corning.com` | 公司合作新闻稿 HTML | 2026-06-08 | Corning Incorporated / Amazon | 2026 合作公告 | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；确认 Amazon 合作，非完整客户表 |
| https://www.corning.com/worldwide/en/about-us/news-events/news-releases/2026/05/nvidia-and-corning-announce-long-term-partnership-to-strengthen-us-manufacturing-for-ai-infrastructure.html | `corning.com` | 公司合作新闻稿 HTML | 2026-05-06 | Corning Incorporated / NVIDIA | 2026 合作公告 | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；确认 NVIDIA 合作，非完整客户表 |
| https://www.corning.com/worldwide/en/sustainability/processes/supply-chain-social-responsibility/supplier-responsibility.html | `corning.com` | Supplier Responsibility 页面 | 页面未单独标注 | Corning Incorporated | 截至 retrieved_at | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；无命名供应商清单 |
| https://www.corning.com/worldwide/en/sustainability/processes/supply-chain-social-responsibility.html | `corning.com` | Supply Chain Social Responsibility 页面 | 页面未单独标注 | Corning Incorporated | 截至 retrieved_at | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；无完整关系库 |
| https://www.sec.gov/Archives/edgar/data/24741/000002474126000253/glw-20260728xex99xq22026.htm | `sec.gov` | Form 8-K Exhibit 99.1 HTML | 2026-07-28 | Corning Incorporated | Q2 2026 | `a2c7d546b7a4e47e985c95c3431ac49ccf94c1c5ee44115cff1a53d8e3b1ef0e` | `direct URL`；已下载 bytes，作为 Q2 新闻稿/合作披露的 SEC 备案副本 |

## 降级规则

- 只有客户集中度百分比、匿名客户押金或公司合作新闻时，输出 `PARTIAL`；不得生成完整客户清单或客户—供应商关系图。
- 客户名称必须由同一份文件或可明确绑定的官方一手文件支持；XBRL member、时间接近或产品相似不能单独完成归因。
- 没有命名供应商和采购金额时，标 `SOURCE_UNAVAILABLE`，不从“单一来源/有限供应商”推断具体公司。
- 若需要全量关系库，要求用户提供授权的 ERP/采购导出、合同、供应商数据库或客户数据；每个文件需记录权限、原始 hash、期间和字段定义后再接入。
