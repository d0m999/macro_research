# GLW（Corning Incorporated）数据资产验证目录

> 验证对象：`GLW` / `Corning Incorporated` / `CIK 0000024741`
>
> 验证日期：2026-08-19（UTC）
>
> 目的：验证“公开来源优先、用户数据可插拔、付费能力可选、缺失项显式降级”的公司分析工作流能否在当前 session 获取或登记各类数据。

## 结果总览

| 数据类别 | 文档 | 状态 | 当前结论 |
|---|---|---|---|
| SEC EDGAR | [01-sec-edgar.md](./01-sec-edgar.md) | `PASS` / 通道差异 | 无 key 的 JSON API 成功；直接 archive HTML 在本地 curl 被 403，Web 读取成功 |
| 美国财政部利率 | [02-us-treasury-rates.md](./02-us-treasury-rates.md) | `PASS` | XML feed 成功取得 2026-08-18 期限结构 |
| FRED | [03-fred.md](./03-fred.md) | `PARTIAL` | API 无 key 失败；官方 CSV fallback 成功 |
| 公司 IR | [04-company-ir.md](./04-company-ir.md) | `AVAILABLE` | 官方域名限定搜索和动态页面读取可行；结构化事实优先取 SEC |
| 公司新闻稿/演示材料 | [05-company-news-presentations.md](./05-company-news-presentations.md) | `AVAILABLE` | Q2 新闻稿、8-K 附件和演示 PDF 已定位并登记 |
| 完整电话会 transcript | [06-earnings-transcript.md](./06-earnings-transcript.md) | `PARTIAL` / `SOURCE_UNAVAILABLE` | 官方页面确认 webcast；完整逐字稿不应由随机第三方网页补齐 |
| 实时/历史行情 | [07-market-data.md](./07-market-data.md) | `SOURCE_UNAVAILABLE` / `USER_UPLOAD_REQUIRED` | 未假设免费行情 entitlement；当前 session 没有券商或 TradingView 导出文件 |
| 分析师共识 | [08-analyst-consensus.md](./08-analyst-consensus.md) | `SOURCE_UNAVAILABLE` | IAC 入口可定位，但本次没有取得可验证的 Street consensus 数值 |
| 行业报告/市场份额 | [09-industry-market-share.md](./09-industry-market-share.md) | `PARTIAL` / `SOURCE_UNAVAILABLE` | 10-K 可提供业务、竞争者和公司自述；独立精确份额需授权/用户文件 |
| 客户/供应商关系 | [10-customer-supplier.md](./10-customer-supplier.md) | `PARTIAL` / `SOURCE_UNAVAILABLE` | SEC 披露可给出客户集中度和部分合同证据；不是全量关系库 |
| workflow 验证总结 | [11-workflow-test-summary.md](./11-workflow-test-summary.md) | `COMPLETE` | 汇总当前 session 的可用性、失败路径和适配器边界 |

## 统一来源登记字段

每个结果文档至少记录：

```text
url
official_domain
document_type
published_at / reporting_period
retrieved_at
sha256（若下载到原始 bytes）
issuer
权限/费用
API 稳定性
自动抓取、缓存、再分发边界
状态与降级规则
```

`sha256` 只对实际下载并保存到临时探针目录的原始响应登记。Web 搜索摘要、动态页面的索引结果和被拦截的错误页不视为源文件 bytes，也不作为报告事实来源。

## 关键边界

- 公司 guidance、公司自述的竞争地位和独立分析师 consensus 分开登记。
- 证券行情的公开可见页面不等于稳定 API，也不等于可缓存或再分发授权。
- `PARTIAL`、`SOURCE_UNAVAILABLE` 和 `USER_UPLOAD_REQUIRED` 不得在后续分析中静默升级为完整数据。
- 本目录是本地验证 artifact，不构成投资建议，也没有提交、推送或外部发布。
