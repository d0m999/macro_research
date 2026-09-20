# Herman Jin 语料清洗 review（2026-09-20）

> 复核对象：`Herman Jin/market-overview/*/transcript.jsonl`（59 包 / 52,518 段）
> 复核手段：SHA 基线逐包校验、`git diff` 未提交改动核对、全库英文 token 频次扫描（`/usr/share/dict/words` 过滤）、可疑词上下文判读
> 结论先行：**第一轮全量清洗已跑完，但没有收口。有 3 个断点 + 一批可直接修的残留。**

---

## 1. 进度事实

| 项 | 状态 |
|---|---|
| 视频包 | 59（`market-overview-2025-01-07` … `2026-09-15`），`agent-index.json` 60 条（含 1 个 X 包） |
| 转录段 | 52,518 段，SHA 基线 59/59 齐全（`transcript-sha256.json`，生成于 2026-09-20 00:48:35） |
| 已提交清洗 | 3 个 commit：`363d76b`（Tier A/B/C，~5,380 替换）、`9d0b90f`（变体 sweep 15+8 行）、`e5d3251`（token-mining 26 行） |
| 已修词型抽查 | `狗门`/`Azik`/`Track Rocker`/`Basepoint`/`BeautifulBuild`/`Tale Risk`/`NED`/`dollarate`/`Andopic`/`Foreward`/`Kapax`/`Prembook`/`Volk control` → **零残留** |
| X 侧 | `posts.jsonl` 1,273 条（重复正文 1）、`replies.jsonl` 6,400 条（重复正文 258，属正常重复回复）；无空文本，ID 唯一 |

已修部分质量可信：抽查 `git diff` 的 41 行未提交改动（甲方/乙方、十年期利率、Reciprocal Tariff、PCIe→PCE、Allocore→Oracle、进价→溢价），**全部判读正确**，无反向改写。

## 2. 断点（按严重度排序）

### B1 · 41 行已改未提交，且 SHA 基线已过期（11 包）

`2025-02-25 / 03-11 / 04-01 / 04-08 / 05-13 / 07-02 / 09-09 / 10-14 / 10-28 / 11-18 / 2026-03-17` 共 11 个包的转录在工作区已改，但未 commit；基线是这批改动**之前**生成的。
后果：此刻任何人跑「基线校验」会得到 11 个 false alarm，无法区分「文件被改坏」和「基线没刷新」。

### B2 · 变体 sweep 按字面走，漏掉语音近邻（最典型的漏洞：`tel risk`）

已修 `Tale Risk → tail risk`，但**同音变体 `tel risk` 仍有 10 处**未修（4 个包）。
说明 sweep 用「已知错词字面表」做替换，而不是「语音近邻聚类 + 全库回扫」。这是本轮清洗的结构性缺陷，不是遗漏一次的问题——下次还会漏同类变体。

### B3 · 语料索引只有规范，库未落盘

`_index/CORPUS-INDEX-SPEC.md`（23.5 KB）写得完整（字段定义、行号=引用锚点、繁简归一化、增量维护），但 `_index/` 下**没有任何 `.db`**。检索仍要靠 grep，而 SPEC §0 已明确 grep 只能命中一半（繁简分叉）+ 专名被 ASR 念错会漏检。

### B4（次要）· X 侧未做清洗与去重说明

258 条重复正文未标注性质；`in_reply_to_post_id` 恒 `null`、`thread_id` 无效字段（SPEC §8.2/8.3 已知）。属已知限制，但索引若建库需显式处理，否则会被当成 258 条独立证据。

## 3. 残留清单：高置信（已执行，30 行 / 33 处替换）

只改 `text` 字段，不动 `id`/`start`/`end`/`chapter`/`source`。

| 错词 | 应为 | 位置 |
|---|---|---|
| `tel risk` | `tail risk` | 2025-01-07 L100 L101；2025-01-14 L464 L474；2025-02-11 L199 L208 L212（+1 处同行）；2025-02-18 L17 L32 |
| `BLG` | `BOJ` | 2025-01-21 L35 L40 L41(×2) L44 L50 |
| `Flatcase` | `flat case` | 2026-03-24 L732 L743；2026-04-14 L394(×2)；2026-04-21 L80 |
| `Nedrillion` | `Nvidia` | 2025-03-11 L361（原句「Nedrillion英偉達的GTC」，同义重复） |
| `Allocore` | `Oracle` | 2026-06-02 L472（换卡回本周期语境） |
| `Corecom` | `Qualcomm` | 2026-02-10 L339（与 MTK 并列、台积电 CoWoS 分配语境） |
| `假方` | `甲方` | 2025-05-13 L465（供应商/客户对举，同批已修） |
| `AutoLong` | `auto loan` | 2025-10-28 L825 |
| `Lemon Brother` | `Lehman Brothers` | 2026-06-09 L627 |
| `Bound mental` | `fundamental` | 2025-04-15 L524 |
| `CEMET` | `Summit` | 2025-07-02 L416（NATO CEMET） |
| `CTA-Resparity` | `CTA risk parity` | 2025-06-03 L110 |
| `Covif` | `Covid` | 2026-07-14 L131 |

### 3.1 执行记录（2026-09-20 03:01 已完成）

- **改动规模**：30 行 / 33 处替换（含补漏：`2025-06-03` L98、L109 的裸 `Resparity` → `risk parity`，review 时只列了 L110，近邻回扫时补出）。
- **改动范围**：18 个包。逐行 diff 校验 —— 行数不变、`id`/`start`/`end`/`chapter`/`source`/键集合**零变化**，仅 `text` 改动。
- **基线**：`market-overview/transcript-sha256.json` 已重刷（`generated: 2026-09-20T03:01:16+08:00`），59/59 包 SHA 与行数回读校验一致，总行 52,518 不变。
- **近邻回扫**：对 tail risk / Oracle / BOJ / Nvidia / risk parity / Lehman / flat case / Covid / fundamental / auto loan / Qualcomm 共 11 个词族做语音近邻（tel/teil/tale、Allocore/Auroco/Aurocross、Nedrillion、Resparity、Lemon、Flatcase、Covif、Bound mental、AutoLong、Corecom）全库回扫 → **全部清零**。
- **备份**：改前副本在 `/tmp/hj-clean-backup-20260920/`（18 个 jsonl + 旧基线），可逐字节还原。
- **未做**：41 行改动与本轮 30 行均**未 commit**（待你确认后再提交）。

## 4. 存疑 7 组：上下文 + 新闻复核后的判定（2026-09-20 03:08 已执行）

| 原词 | 判定 | 置信 | 关键证据 |
|---|---|---|---|
| `Abago` | **Avago（Broadcom）** | 高 | 同段 L392-394「track record 比较好、做时间比较长、一直拿着 Google 的 TPU」—— Google TPU 的 ASIC 总包即 Broadcom（前身 Avago）；库中另两期已有正确词形 `Avago`、`AVGO` |
| `Babao` | **Marvell** | 高 | 同段 L368「ASIC 整包方案其实只有（这两家）」，L369「弹性非常高」、L353「非常便宜、我自己买过跌很多」、L402「做的比较新、是转型」、L410-411「Microsoft 的单、Maia 3」、L378「Trinity 3/4」= Trainium 3/4。**外部佐证**：AWS Trainium v2 与 Microsoft Maia v2 的定制芯片合作方都是 Marvell；Google TPU / Meta MTIA 是 Broadcom。两家一一对应；且库中 `Marvell`、`Broadcom` 此前 **0 次**命中（ASR 从没识别对过） |
| `DPC` | **DeepSeek**（仅改 2 期） | 中高 | 2025-02-25 L153 与「OpenAI GPT 降价 97%」并列，指推理成本被打下来（DeepSeek 时刻）；2026-06-30 L633-635「不会自己部署一个…」「部署…远远落后于 Cloud」「防止蒸馏」→ 开源模型本地部署 + 蒸馏。**2026-01-06 L807 不改**：该句语义是「用 ChatGPT 对话」，与另两处不同源 |
| `BuGlox` | **Bill Gross** | 高 | 同句「讲过一个概念叫快乐 supernova、债务的红巨星/超巨星」，前后文讲 r>g 债务无限扩张。**外部佐证**：Bill Gross 2013 年 Investment Outlook 标题即 **“Credit Supernova”**，2022 年再谈 “Global Supernova”。连带的「快乐」= **Credit**、「怪太年」= 概念（L60、L74 同段一并修正） |
| `AUROCO` / `Aurocross` | **Oracle** | 中高 | 2026-03-17 L679「做 CAPEX 的公司…做土建、买地建楼」；2026-06-09 L319 与 Microsoft 并列、云端 backlog 订单。库中 `Oracle` 已有 87 次正确命中，此处为偶发误识 |
| `Aging` | **AI** | 高 | L823-828「我调用的时候往往不是人在调用，我是 AI 在调用…其实是机器在调用」—— 自解释 |
| `漫年以方` | **万年乙方** | 高 | L412-415「leaning towards 供应过剩 → 中国通缩是中国永远是…」；中国作为代工/供应方即乙方；库中「甲方/乙方」此前已修 22 处，同一 ASR 同音族 |
| `MyOption` | **不改** | — | 「卖出黑天鹅风险换一点点收益」的泛称（S&P / credit spread / sell vol 上都有），无任何候选原词能闭合 |

### 4.1 执行记录（2026-09-20 03:08）

- **改动**：10 个包 / 26 处替换（含连带修正：`2026-06-23` L60、L74 的「快乐 supernova / supermao」→ `Credit supernova`）。
- **例外不改**：`MyOption`（4 处）、`DPC`@2026-01-06 L807、`Mao`@2025-05-13 L390（单音节，无法判定）。
- **校验**：逐行 diff —— 行数、`id`/`start`/`end`/`chapter`/`source`、键集合**零变化**，仅 `text` 改动。
- **基线**：已重刷（`generated: 2026-09-20T03:08:13+08:00`），59/59 回读一致，总行 52,518 不变。
- **备份**：`/tmp/hj-clean-backup-20260920/`（25 个 jsonl + 旧基线）。

## 5. 覆盖度旁证

- 全库英文 token 2,644 型；不在词典且频次 ≥3 的 205 型，其中绝大多数是**正确**专名（CTA / capex / CoWoS / FOMC / Bessent / TACO / 自民党 LDP / MLCC / NVL72 / Lip-Bu Tan …）。真错误占比低，说明 Tier A/B/C 打中了主要病灶。
- 但错误集中在**低频长尾**（出现 1–3 次），且这批正是「检索时会漏掉证据」的那批。

## 6. 建议的收口步骤

1. 提交现有 41 行改动 → 重刷 `transcript-sha256.json`（基线必须与工作区一致，否则后续所有校验失效）。
2. 跑 §3 的 29 行修正，同一 commit 内刷新基线。
3. **改 sweep 方法论**：不要只维护「错词→正词」字面表；对每个已确认错词，做一次全库**语音近邻回扫**（如 tail 的近邻 tel/tale/teil/tail-risk 连写形态），否则 `tel risk` 这类漏洞会持续复发。
4. 建索引库（`_index/` 下 SQLite + FTS5，按 SPEC §3 执行）。清洗与索引是同一件事的两半：修完专名才能让索引查得到。
5. §4 存疑项一律保持原样，不做「合理推测填充」——这批语料会被研究文档按行号引用，改错的代价高于漏改。

## 7. 状态（2026-09-20 11:15 更新）

- §3（30 行 / 33 处）与 §4（10 包 / 26 处）已执行并随 `e129a04` 提交；复核报告随 `8047aec` 提交。
- `5dd4158`：ASR 音频验证轮（另一会话执行）——faster-whisper-small 对 232 条候选逐条重听（269 个 clip，[start−8s, end+8s]），裁定落盘 112 行（28 包），基线刷新至 `2026-09-20T03:46:21+08:00`，59/59 回读一致。
- 索引库（B3）仍未落盘；X 侧（B4）未处理。

---

## 8. ASR 音频验证轮（5dd4158）的登记与缺口

**轮次内容**（据执行方总结）：232 条候选全部机器重听，规则为「机器只当第二意见」——与原文听见相同且语义无解的保留；明确听出别的且语境吻合才落盘。战果：已修 124 / 保留 84 / 空转 25（盘内早已是正确词形的陈旧条）。亮点：`Allocore/alloc/Oroco→Oracle`（TikTok 交易 8 处、Meta 被定价成 Oracle 7 处）、`Teloff` 一词两义（2 处 Trump put、1 处 effective tariff）、`房屋→防务`×5、`NIN→earning`、`GSMG→TSMC`、`進價→溢價`、`WOW→VOL/wall`。落盘过 text-only / 行数 / seg / JSON 四项校验。

**⚠ 审计工件缺口（本仓库当前缺失）**：
- `audio-worklist.md`（84 条保留项的时间戳清单）——**不在本仓库**，全库与 /tmp 均未找到；
- `asr-results.json`（269 个 clip 的机器转写结果）——同上；
- 本报告当时的「第九节」未随落盘同步进来。

84 条保留项若要封存或移交真人耳检，**必须先把这个文件归档进 `Herman Jin/_source/` 或 `research/`**，否则封存没有载体。

## 9. 保留项深挖：三证据法抽查（2026-09-20 11:11 已执行）

对执行方推荐的 3 条做文本侧判定（不改用音频，三证据法）：

| 原词 | 判定 | 证据 |
|---|---|---|
| `ONI interest resource`（2025-07-08 L187） | **`ON RRP interest rate`** | 同段 L186-192 是 OIS / ON RRP / GC 三利率对比（「GC 是 collateralize，一个无抵押一个有抵押」）；库中 `RRP` 正确命中 7 次；2025-07 正是 RRP 余额话题期 |
| `dpsc`（2025-03-04 L453） | **`DeepSeek`** | 上下文「从 IDC 硬件转到政府采购软件、AI 软件，包括 dpsc，可让很多软件的下限变低了」= 开源模型拉低软件成本；与已闭合的 `DPC→DeepSeek` 同族；库中 `DeepSeek` 12 次 |
| `利普壇`（2026-04-21 L953） | **`Lip-Bu Tan`** | 同位语「就是那个陈立武」直接指认；库中 `Lip-Bu Tan` 已有正确词形（2025-07-08 L706） |
| `利普臺`×2（2025-12-09 L657-658） | **保留** | 前句 L656 刚说「原因是陈立武（成立武）嘛」，若利普臺也是 Lip-Bu Tan 则自相矛盾；候选 legacy / Pat Gelsinger 均读音不合，无唯一答案 |
| `MyOption`、`Mao`、`DPC`@2026-01-06 | 保留（沿用 §4 结论） | 无新增证据 |

**落盘**：3 处（3 包），只改 `text`；逐行 diff 校验其余行与 HEAD 完全一致、行数不变；基线刷新至 `2026-09-20T11:11:37+08:00`，59/59 回读一致，总行 52,518 不变。

**封存决定**：其余 ~81 条保留项就此封存——文本侧三证据法已无新增可闭合项，音频侧 small 模型能力见顶（会幻觉，如 WOW→Option Wall 需语境验证），继续深挖的边际收益低于耳检成本。封存前提：`audio-worklist.md` 归档进本仓库（见 §8 缺口）。
