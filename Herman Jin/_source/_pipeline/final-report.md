# Herman Jin 全量视频转录归档最终报告

状态：已完成。2026-09-02 按单 worker、阶段不重叠的资源策略处理完全部待处理期次；管线无待处理视频，临时完整源文件均已在对应期次发布后删除。

## 清单

- 频道：Shanghao Jin（`@shanghaojin`，`UCTAJ0JnR9oYvILu-mtNcufQ`）
- 范围：`2025-01-01` 至 `2026-08-26`
- `videos` 标签观察到 81 条；`streams`、`shorts` 标签不存在
- 范围内按 YouTube video ID 去重后：56 个
- `complete_existing`：3 个
- 新增 `complete`：53 个
- `unavailable`：0 个；`blocked/failed`：0 个
- 标题日期与 `upload_date` 不一致：5 个，差异证据位于对应 `_source/<package-id>/metadata/date-discrepancy.json`

## 已完成

- 写入 `inventory.jsonl`，按 YouTube video ID 去重并按 `upload_date` 倒序。
- `state.json` 已更新为 `pipeline_state: complete`，状态计数为 53 个 `complete`、3 个 `complete_existing`，无 active 项。
- 为 53 个新视频建立 `_source/<package-id>/{metadata,audio,transcript,frames,diagnostics}/`。
- 53 个新视频均已生成标准 agent 数据包：`manifest.json`、`transcript.jsonl`、`deck.jsonl`、`slides/`、`ocr/`。
- 四个本次续跑期次已完成：`2025-02-11`（1285 条转录、14 个 Deck 画面）、`2025-01-21`（949 条、3 个）、`2025-01-14`（721 条、11 个）、`2025-01-07`（780 条、9 个）。
- 新增包的 `manifest.related_materials.readable_html` 和索引 `readable` 均为 `null`；没有生成新的 HTML。
- 三个 `complete_existing` 包及其三个 `_readable/*.html` 保留原样；`agent-index.json` 已登记全部 56 个验收通过的包。
- 没有把签名媒体 URL 写入诊断文件。

## 资源策略

- 全程只允许 1 个视频、1 个阶段、1 个子进程，阶段不得重叠。
- 下载阶段启动门槛：CPU idle ≥ 40%，连续 3 次，每次间隔 30 秒。
- `ffmpeg`、Whisper 和 OCR 启动门槛：CPU idle ≥ 55%，连续 3 次，每次间隔 30 秒。
- 运行中 CPU idle 连续 2 次低于 35%：暂停当前子进程；恢复需连续 3 次达到对应启动门槛。
- 可用内存、Swapouts、磁盘和低优先级/单线程约束保持不变。
- 四个续跑期次均在验收通过后原子发布，再删除临时源文件；期间未发生阶段重叠。

## 历史阻塞记录

- `ZdgSfsSPnXQ`：默认客户端 `399+251`、`137+251` 和 `android_sdkless` 最高格式返回 `HTTP 403`；`web_safari` 只暴露 storyboard。
- `EnbXozQn89s`：`android_sdkless`、`android_vr`、ffmpeg 及代理分段请求无法完成媒体下载；完整请求和非首段返回 `HTTP 403`，直连 IPv4/IPv6 不可用；现有 `bgutil` provider 生成的显式 PO Token 对 `mweb`/`web` 仍只返回 storyboard，`web_embedded` 返回错误码 152。
- `YJ8cpZrdvfo`：小范围重测通过，但完整下载仍阻塞：`248+140` 默认下载返回 403；512 KiB 分段只到约 2 MiB；每次重新取 URL 请求 `2097152-3145727` 时，`248`、`137`、`399` 均返回 403；显式直连无法取得元数据，SOCKS 入口同样返回 403。

以上是历史诊断记录；相关期次现已通过 progressive format 18 完成归档。当前工具为 `yt-dlp 2025.12.08`；遵守不登录、不绕过 DRM/验证、不自动升级工具的固定边界。

## 最终验收

- 正式包目录共 56 个，`agent-index.json` 共 56 条，按日期倒序且无重复 package ID。
- 新增包顶层精确等于五项白名单；JSON/JSONL 可解析，manifest 记录数与实际行数一致。
- 新增包的 transcript ID、时间范围、章节和 Deck 时间范围均通过边界检查；所有链接均为包内相对路径并存在。
- 新增包 OCR 文件与 `deck.jsonl` 的 `ocr` 字段逐字节一致。
- 新增包全部为 PNG 原生帧，未放大；本次四期下载实际分辨率为 `640x360`。
- 正式包内没有 HTML、音频、SRT/VTT、候选帧或诊断文件；无 Deck 包保持空 `slides/` 和 `ocr/` 目录约定。
- 四期临时源目录已删除，`/tmp` 下无 `herman-jin-*` 临时目录，也没有残留视频文件。
- 三个既有 HTML 的 SHA-256 已核对，未被本次续跑改写。
- `git diff --check -- 'Herman Jin'` 已通过；未执行 commit、push、部署或发布。

## 当前总账

```text
发现总数 56 = 日期范围外 0 + complete_existing 3 + 新增 complete 53 + unavailable 0 + blocked/failed 0
```

当前 `state.json` 为 `pipeline_state: complete`，没有待处理视频。
