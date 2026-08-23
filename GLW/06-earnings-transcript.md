# GLW / Corning Inc — Earnings Transcript

> 研究状态：`PARTIAL`；完整逐字 transcript：`SOURCE_UNAVAILABLE`
> retrieved_at：`2026-08-19T20:05:00+09:00`
> issuer：`Corning Incorporated`
> reporting_period：Q2 2026（2026-07-28）及 Q4 2025（2026-01-28）电话会

## 结论

本次在 Corning 官方 IR 事件页面和官方 webcast 入口确认了电话会存在，但没有从官方页面或 replay 入口取得并验证可引用的完整文本 transcript、字幕文本或 Q&A 逐字稿。因此，当前只能确认“电话会 / webcast 入口”，不能评价 Q&A、管理层语气、回避问题、逐句指引或问答中的新信息。

没有使用随机第三方 transcript 页面补齐缺失数据。`SOURCE_UNAVAILABLE` 只针对完整文本 transcript，不表示官方业绩新闻稿或演示材料不可用；后者记录在 [05-company-news-presentations.md](./05-company-news-presentations.md)。

## 获取路径、费用与自动化边界

- 获取路径：`web search` 定位 Corning IR event；用 `Browser-like web` 打开事件页并核验 Webcast/Press Release/Presentation 链接；用 `direct URL` 打开官方 webcast replay 入口。没有下载音频，也没有将音频播放器 HTML 当作 transcript。
- 费用/权限：官方事件页和 webcast 入口当前公开可达；完整 transcript 可能由公司公开，也可能需要授权数据库、用户上传或付费 API，不能假设免费或可再分发。
- 稳定 API：没有发现 Corning 官方 transcript API；webcast 播放器 URL 不是稳定文本 API。
- 自动抓取、缓存、再分发边界：只登记事件 URL、发布时间和页面状态；不绕过登录、验证码、付费墙或播放器限制，不批量抓取音频，不保存或再分发录音/字幕，除非用户拥有相应权限且条款允许。

## 实际摘录 / 缺失项

- [Q4 2025 Earnings Call event page](https://investor.corning.com/news-and-events/events-and-presentations/event-details/2026/Corning-Incorporated-Quarter-4-2025-Earnings-Call-2026-TTxrjbQKDu/default.aspx) 显示 2026-01-28 8:30 AM ET，并列出 Webcast、Press Release、Financial Statement & Exhibits 和 Presentation。该页面没有提供可核验的完整文字 transcript。
- [Q2 2026 Events & Presentations](https://investor.corning.com/news-and-events/events-and-presentations/default.aspx) 的动态索引列出 2026-07-28 的 `Q2 2026 Earnings Call`。本次没有把搜索摘要当作 transcript 内容。
- [Q4 webcast replay/landing URL](https://edge.media-server.com/mmc/p/kz96wbqc) 可打开 HTML 播放入口；实际保存的是 landing/replay HTML 的 hash，不是音频或文字记录。
- `SOURCE_UNAVAILABLE`：完整 transcript、逐句字幕、Q&A 发言者/问题映射、管理层语气评分。

## 来源登记

| url | official_domain | document_type | published_at | issuer | reporting_period | sha256 | 获取路径 / 实际状态 |
|---|---|---|---|---|---|---|---|
| https://investor.corning.com/news-and-events/events-and-presentations/event-details/2026/Corning-Incorporated-Quarter-4-2025-Earnings-Call-2026-TTxrjbQKDu/default.aspx | `investor.corning.com` | earnings call event page | 2026-01-28 | Corning Incorporated | Q4 2025 | 未保存 bytes（Browser-like web 正文已核验） | `web search` → `Browser-like web`；确认 webcast 等官方链接，无 transcript |
| https://investor.corning.com/news-and-events/events-and-presentations/default.aspx | `investor.corning.com` | events index | 2026-07-28（索引条目） | Corning Incorporated | Q2 2026 | 未保存 bytes（动态页面） | `web search` → `Browser-like web`；确认电话会条目，无 transcript |
| https://edge.media-server.com/mmc/p/kz96wbqc | `edge.media-server.com`（IR 事件页指向的 webcast host） | webcast landing/replay HTML | 2026-01-28 | Corning Incorporated / webcast host | Q4 2025 | `7e18ae820699ec8ee4f22cdebb86322012afcb431e016ab14b8eb8f4d47fd9d0` | `Browser-like web` → `direct URL`；仅保存 landing HTML hash，未保存音频/字幕 |
| https://s203.q4cdn.com/212458750/files/doc_financials/2026/q2/Corning-Incorporated-Second-Quarter-2026-Earnings-Release-with-Financials-2026-07-28.pdf | `s203.q4cdn.com`（Corning IR Q4 CDN） | earnings release PDF（非 transcript） | 2026-07-28 | Corning Incorporated | Q2 2026 | `90343ca05cb5ed748d9772acfda228c7f813d8ad8c2adec989cf3d05b1fe4eed` | `direct URL`；业绩材料可用，但没有把它当逐字稿 |

## 降级规则

- 没有官方逐字稿或用户授权文件：输出 `SOURCE_UNAVAILABLE`，不生成 Q&A 结论、语气结论或“管理层回避”判断。
- 只有 webcast 入口：可记录事件存在和链接，不得把音频可播放等同于文本已取得。
- 用户上传 transcript 后，仍需登记来源、获取权限、文件 hash、issuer 和 reporting period；未验证的用户文件只能标为待核验。
- 任何付费数据库或受限播放器均不绕过；可改走用户上传或具有授权的 API adapter。
