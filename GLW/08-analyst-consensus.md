# GLW / Corning Inc — Analyst Consensus

> 研究状态：`SOURCE_UNAVAILABLE`（官方 IR 关联工具可定位，但本次没有取得可验证的数值共识）
> retrieved_at：`2026-08-19T20:05:00+09:00`
> issuer：`Corning Incorporated`；共识数据若存在，issuer 应登记为相应授权数据供应商
> reporting_period：截至 retrieved_at；未取得 FY2026/Q3 2026 的 Street consensus 数值

## 结论

Corning IR 的 SEC Filings 页面提供了 `Interactive Analyst Center` 入口。本次通过 Browser-like web 和 direct URL 打开该入口后，最终到达由 `iac.virtuaresearch.com` 承载的动态应用 shell，但没有取得并验证 EPS、收入、目标价、评级分布或历史共识修订数据。应用 shell 依赖动态脚本；没有把未文档化的后端路径当作稳定 API，也没有绕过登录、授权或访问控制。

因此不能输出可靠的 `beat/miss vs. Street`。Corning Q3 outlook 是公司 guidance，不能替代分析师共识。

## 获取路径、费用与自动化边界

- 获取路径：`web search` 定位 Corning IR 的 SEC Filings 页面；用 `Browser-like web` 核验 IR 关联链接；用 `direct URL` 跟随重定向到 vendor-hosted IAC 页面并保存应用 shell bytes/hash。
- 费用/权限：IR 链接本身公开；共识字段的显示、下载和再分发权限未在本次页面中确认，不能将 vendor-hosted 应用假设为免费或可再分发数据源。完整共识通常需要授权数据库、用户导出的 Excel/CSV 或有 entitlement 的 API。
- 稳定 API：本次未发现由 Corning 或 IAC 文档公开的稳定 consensus API。动态脚本中出现的内部请求路径不作为 API 合同，不纳入自动化 adapter。
- 自动抓取、缓存、再分发边界：只登记公开入口、重定向和取得状态；不逆向未文档化接口、不批量请求、不绕过授权，不缓存或再分发共识明细。若用户提供有权使用的 Excel/CSV，再由 `user-file adapter` 建立可审计快照。

## 实际摘录 / 缺失项

- [Corning SEC Filings IR 页面](https://investor.corning.com/investor-relations/financials/sec-filings/default.aspx) 可定位 `Interactive Analyst Center` 链接。
- 原始入口 [apps.indigotools.com/IR/iac](https://apps.indigotools.com/IR/iac/?exchange=NYSE&ticker=GLW) 重定向到 [iac.virtuaresearch.com](https://iac.virtuaresearch.com/?exchange=NYSE&ticker=GLW)。本次保存并核验的只是动态应用 shell，不是 consensus 数据快照。
- `SOURCE_UNAVAILABLE`：FY2026/Q3 2026 revenue consensus、EPS consensus、high/low range、price target、rating、revision history、覆盖分析师数量。
- 可用但不同类的数据：[Q2 2026 官方新闻稿](https://investor.corning.com/news-and-events/news/news-details/2026/Cornings-Strong-Second-Quarter-2026-Financial-Results1-Demonstrate-Progress-on-Recently-Upgraded-Springboard-Plan/default.aspx) 的 Q3 outlook 标为 `COMPANY_GUIDANCE`，不可用于 beat/miss。

## 来源登记

| url | official_domain | document_type | published_at | issuer | reporting_period | sha256 | 获取路径 / 实际状态 |
|---|---|---|---|---|---|---|---|
| https://investor.corning.com/investor-relations/financials/sec-filings/default.aspx | `investor.corning.com` | IR SEC Filings 页面 | 页面动态，未单独标注 | Corning Incorporated | 截至 retrieved_at | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；确认 IAC 入口 |
| https://apps.indigotools.com/IR/iac/?exchange=NYSE&ticker=GLW | `apps.indigotools.com`（IR 关联入口） | IAC launch URL / redirect | 页面动态，未单独标注 | Corning IR 关联应用 | GLW | 未保存原始 redirect bytes | `Browser-like web` → `direct URL`；发生重定向 |
| https://iac.virtuaresearch.com/?exchange=NYSE&ticker=GLW | `iac.virtuaresearch.com`（IR 关联的第三方应用域名） | 动态 IAC application shell HTML | 页面动态，未单独标注 | IAC vendor / Corning-linked app | GLW | `beb96fe8a1cd5d5b03765a11325973a2463b69c9f6fc83f870b2805829b5f89e` | `direct URL`；已下载 1,135-byte shell；未取得共识值 |

## 降级规则

- 没有经过授权或可靠公开来源验证的共识：保持 `SOURCE_UNAVAILABLE`，不计算 beat/miss、consensus dispersion 或 revisions。
- 公司 guidance、历史实际值和 SEC XBRL 事实可单独使用，但不得重命名为 Street consensus。
- 只拿到应用 shell、搜索摘要或网页可见标题：不能推断应用中存在或可下载某一具体共识字段。
- 用户提供授权 Excel/CSV 后，必须保存原文件 hash、供应商、下载时间、权限说明和 reporting period；没有这些元数据则继续降级。
