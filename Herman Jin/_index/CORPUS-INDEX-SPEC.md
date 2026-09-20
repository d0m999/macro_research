# Herman Jin 语料索引：建设与维护规范

> 面向对象：需要"在这批语料里查东西"的 agent。
> 本文既是**建设规范**（如何从零建索引），也是**使用规范**（如何查、如何引用）。
> 维护者：任何具备 shell 与 Python 执行能力的 agent。

---

## 0. 这份文档解决什么

仓库里有四类语料，分散在 61,000 个记录里：

| 事实 | 后果 |
|---|---|
| 视频转录是**繁体**、X 文本是**简体**，且逐包切换 | 直接 grep 只能命中一半 |
| 自动转录把专名念错（Goldman → "狗门"） | 按标准名检索会漏掉大量证据 |
| 视频每段平均只有 **10.6 字符** | 命中单段没有可读性，必须合并邻接段 |
| 现有研究用 `#L684-L715` 形式引用原文 | 索引必须能反查行号，否则接不上已有 7 份报告 |

索引存在的意义：**把"查得到"这件事一次性解决**，让后续任何检索、统计、引用都建立在同一套事实之上。

索引不负责判断。它回答"哪几条原文提到了 X"，不回答"这个判断对不对"。

---

## 1. 使用时机

遇到下列任一情形，按下表走：

| 情形 | 读哪些节 |
|---|---|
| 要查语料里某话题/标的/专名的原文 | §5 查询接口、§6 引用格式 |
| 要从零建索引（首次或 db 丢失） | §3 全部步骤 |
| 有新抓的语料要并入（新一期视频、新一批 X） | §7 增量维护 |
| 检索结果不对（漏检、噪声） | §8 陷阱排查 |
| 要改索引结构 | §4 目标结构 + §9 硬性规则 |

---

## 2. 数据源事实

四类来源，路径均相对仓库根 `Herman Jin/`。

### 2.1 清单

| # | 来源 | 路径模式 | 规模 | 时间覆盖 |
|---|---|---|---|---|
| 1 | X 主帖 | `x-archive/x-2026-09-19/posts.jsonl` | 1,273 条 | 2026-01-01 → 09-19 |
| 2 | X 回复 | `x-archive/x-2026-09-19/replies.jsonl` | 6,400 条 | 同上 |
| 3 | 视频转录 | `market-overview/market-overview-YYYY-MM-DD/transcript.jsonl` | 52,518 段 / 59 包 | 2025-01-07 → 2026-09-15 |
| 4 | 幻灯片 | `market-overview/market-overview-YYYY-MM-DD/deck.jsonl` | 814 条 / 59 包 | 同上 |
| 5 | 研究报告 | `research/*.md` | 7 份 / 87,086 字符 / 133 个标题 | — |

合计 60,191 条一手语料 + 814 条幻灯片元数据 + 7 份结论文档。

### 2.2 字段定义（原样，不要改名）

**posts.jsonl**
```
id            "post-000001"         包内序号
post_id       "2006583997053415576" X 侧 ID
created_at    "2026-01-01T04:31:20.000Z"   UTC
text          正文
thread_id     无效字段，见 §8.2
source        "x-web-capture"
```

**replies.jsonl**
```
id, reply_id, created_at, text, thread_id, source   同 posts
in_reply_to_post_id  恒为 null（抓取限制，见 §8.3）
in_reply_to_user     他回复的对象；2026-01 全月为空（见 §8.4）
author_handle        恒为 "ShanghaoJin"
media_count          0 或 1
```

**transcript.jsonl**
```
id            "seg-000001"     与文件物理行号 1:1 对应（见 §8.1）
start / end   秒，浮点
text          正文（繁体或简体，逐包统一）
chapter       "chapter-01".."chapter-06"，少数语义化名（"momentum"、"ai-value-chain"）
source        "faster-whisper-small" 等
```

**deck.jsonl**
```
id            "slide-001"
time_ranges   [[秒, 秒], ...]   该幻灯片在视频中出现的多个时间点
title         幻灯片标题（OCR 质量差）
image         "slides/slide-001.png"
ocr_file      "ocr/slide-001.txt"
ocr           OCR 全文（噪声大，见 §8.5）
visual_type / summary / source_file / image_format
```

**research/*.md**
标准 Markdown，两级标题分节，正文用 `[转录 L684–L715](../market-overview/.../transcript.jsonl#L684-L715)` 形式引用原文。

### 2.3 manifest.json 的位置与用途

每个包有 `manifest.json`（11 键），含 `video.date`、`video.title`、采集方式等元数据。
**日期以目录名为准**，manifest 标题偶有笔误（已知：2025-03-04 标题写成"2025年4月3日"、2025-12-30 写成"2026年12月30日"、2026-05-05 写成"2026年4月21日"），不要据标题改写日期。

---

## 3. 技术前提（已验证，不必重新摸索）

以下结论均已实测，直接采用。

### 3.1 环境

```
Python   /Users/d0m999/.workbuddy/binaries/python/versions/3.13.12/bin/python3
SQLite   3.50.4（Python 内置），FTS5 可用 ✓
venv     /Users/d0m999/.workbuddy/binaries/python/envs/default
```

装依赖（仅 zhconv 一个）：

```bash
/Users/d0m999/.workbuddy/binaries/python/versions/3.13.12/bin/python3 \
  -m venv /Users/d0m999/.workbuddy/binaries/python/envs/default
/Users/d0m999/.workbuddy/binaries/python/envs/default/bin/pip install zhconv
```

### 3.2 中文检索方案

**采用「汉字逐字空格分离 + phrase 匹配」，不用 trigram、不用 jieba。**

理由：trigram 最短匹配 3 字符，中文双字词（存储、芯片、关税）查不到；jieba 引入外部依赖且需维护词典。逐字分离是纯标准库方案，支持任意长度词，phrase 保证字符相邻因而不产生碎片误命中。

分词函数（存入 FTS 前调用）：

```python
import re

def seg(text: str) -> str:
    """汉字逐字空格分离；英文、数字、标点保持原样。"""
    out = []
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf':
            out.append(' ' + ch + ' ')
        else:
            out.append(ch)
    return re.sub(r'\s+', ' ', ''.join(out)).strip()
```

查询构造（把用户输入转成 FTS5 MATCH 表达式）：

```python
def build_match(query: str) -> str:
    """空格分词，中文词转 phrase，各词之间 AND。"""
    parts = []
    for tok in query.split():
        if not tok:
            continue
        s = seg(tok)
        # 分词后超过一个 token 的，用 phrase 锁相邻
        if ' ' in s:
            parts.append('"%s"' % s)
        else:
            parts.append(s)
    return ' AND '.join(parts)
```

已实测（8/8 通过）：`存储`、`长鑫`、`芯片`、`定价`（中文双字词）· `INTC`、`HBM`（英文）· `存储 价格`（多词 AND）· `中国 公司`。

### 3.3 行号即锚点

`transcript.jsonl` 中**物理行号 = `seg-NNNNNN` 的编号 = 研究文档引用的 L 号**（1-based，已验证两处）。因此索引只需记录 `source_line`，就能生成与现有报告完全一致的引用锚点。

X 的 `posts.jsonl` / `replies.jsonl` 同理，行号可直接作为锚点。

### 3.4 繁简分布

59 个视频包中，**仅 3 个包内部繁简混用**，其余每包 100% 单一字形。全仓繁体 34,602 字次 / 简体 35,277 字次，约各半。

结论：归一化必须在**索引期**做（逐包判定无意义，统一转简最省事且无信息损失）。

---

## 4. 目标结构

### 4.1 库文件

```
Herman Jin/_index/herman-jin-corpus.db
```

### 4.2 主表 records

```sql
CREATE TABLE records (
  id           INTEGER PRIMARY KEY,
  origin       TEXT NOT NULL,   -- x-post | x-reply | yt-segment | yt-slide | research-doc
  layer        TEXT NOT NULL,   -- evidence | meta | conclusion
  rec_id       TEXT NOT NULL,   -- 源内唯一 ID（post_id / reply_id / seg id / slide id）
  source_path  TEXT NOT NULL,   -- 仓库相对路径
  source_line  INTEGER,         -- 1-based 起始行号
  source_line_end INTEGER,      -- 仅 research-doc 用（章节结束行）
  pkg_id       TEXT,            -- market-overview-YYYY-MM-DD / x-2026-09-19 / 报告文件名
  created_at   TEXT,            -- ISO UTC；yt-segment 由 pkg 日期 + start 推算
  date_bj      TEXT,            -- YYYY-MM-DD（UTC+8）
  month_bj     TEXT,            -- YYYY-MM
  text         TEXT NOT NULL,   -- 原文，永不修改
  text_norm    TEXT NOT NULL,   -- 繁→简归一化，用于检索与展示对齐
  text_seg     TEXT NOT NULL,   -- seg(text_norm)，供 FTS
  reply_to     TEXT,            -- in_reply_to_user（仅 x-reply）
  chapter      TEXT,            -- 仅 yt-segment
  start_sec    REAL,            -- 仅 yt-segment
  end_sec      REAL,            -- 仅 yt-segment
  char_len     INTEGER,
  tier         TEXT,            -- noise | short | mid | long
  noise_flags  TEXT             -- 逗号分隔，见 §4.4
);

CREATE INDEX idx_rec_date    ON records(date_bj);
CREATE INDEX idx_rec_month   ON records(month_bj);
CREATE INDEX idx_rec_origin  ON records(origin);
CREATE INDEX idx_rec_pkg     ON records(pkg_id);
CREATE INDEX idx_rec_layer   ON records(layer);

CREATE VIRTUAL TABLE fts USING fts5(
  text_seg,
  content='records',
  content_rowid='id',
  tokenize='unicode61 remove_diacritics 2'
);
```

### 4.3 归一化规则

**繁简**：`text` 保留原文；`text_norm = zhconv.convert(text, 'zh-cn')`；`text_seg = seg(text_norm)`。
索引与查询都在**归一化空间**比对，因此搜简体「存储」可命中繁体包里的「存儲」，反之亦然。

**别名**：见 §4.5 的 `aliases` 表。它也存归一化后的形式（"農狂配合" → "农狂配合"）。

### 4.4 分层与噪声标记

`layer` 三值，用于隔离不同可信度的材料：

| layer | origin | 含义 | 检索默认 |
|---|---|---|---|
| `evidence` | x-post, x-reply, yt-segment | 一手原文，可作引用依据 | 纳入 |
| `meta` | yt-slide | 幻灯片标题与 OCR，噪声大 | **排除**（`--include-slides` 才纳入） |
| `conclusion` | research-doc | 已有结论，二手 | 纳入但**标注**，不可当作原文 |

`tier` 按 `char_len` 划分：`noise`（<4 或全符号）· `short`（4–29）· `mid`（30–79）· `long`（≥80）。

`noise_flags` 取值：

| flag | 判定 |
|---|---|
| `emoji-only` | 去除标点空白后为空 |
| `ocr-garbage` | 仅 yt-slide：含连续 3 个以上单字符间隔，或非文字符号占比 > 60% |
| `asr-suspect` | 仅 yt-segment：整段长度 ≤ 2 字符 |

### 4.5 别名表

```sql
CREATE TABLE aliases (
  alias      TEXT NOT NULL,   -- 归一化后的误识别形态
  canonical  TEXT NOT NULL,   -- 标准名
  kind       TEXT,            -- entity | concept
  evidence   TEXT             -- 出处（如 "reading.md#L305"）
);
```

数据来源见 §10 附录 A，**照抄即可**，不要自行发明映射。

检索时把查询词扩展为 `canonical OR alias1 OR alias2 ...`，再合并结果。

### 4.6 派生视图

```sql
-- 可分析语料（排除噪声层）
CREATE VIEW v_substantive AS
  SELECT * FROM records WHERE layer != 'meta' AND tier IN ('mid','long');

-- 标的 × 期数（对齐现有报告的"来源 × 节目期"口径）
CREATE VIEW v_entity_by_pkg AS
  SELECT a.canonical AS entity, r.pkg_id, COUNT(*) AS hits, MIN(r.date_bj) AS first_seen
  FROM records r JOIN aliases a ON r.text_norm LIKE '%' || a.alias || '%'
  GROUP BY a.canonical, r.pkg_id;
```

> `v_entity_by_pkg` 用 LIKE 全表扫，仅用于离线统计，不要放进交互查询路径。

---

## 5. 执行步骤

**每步都有完成标准；未达标不要进入下一步。**

### 步骤 1 · 装依赖

```bash
VENV=/Users/d0m999/.workbuddy/binaries/python/envs/default
PY3=/Users/d0m999/.workbuddy/binaries/python/versions/3.13.12/bin/python3
[ -d "$VENV" ] || $PY3 -m venv "$VENV"
"$VENV/bin/pip" install zhconv
"$VENV/bin/python" -c "import zhconv; print(zhconv.convert('存儲價格','zh-cn'))"
```

**完成标准**：末行输出 `存储价格`。

### 步骤 2 · 建别名表

从 §10 附录 A 抄入 `aliases`（A.1 实体 11 条 + A.2 概念 14 条，共 25 条），逐条录入。

**完成标准**：`SELECT COUNT(*) FROM aliases;` = 25。

### 步骤 3 · 写构建脚本

脚本落点：`~/.workbuddy/skills/herman-jin-x-archive/scripts/hj-corpus-build-index.py`

要点：

- 用 `argparse` 接收 `--repo`（默认 `~/Desktop/vibe-trading/Herman Jin`）与 `--out`
- 视频包用 `sorted(glob('market-overview/market-overview-*'))` 遍历，跳过缺文件的包
- **逐行读 jsonl 并记录行号**（`enumerate(f, 1)`），行号写入 `source_line`
- research-doc 按**二级标题（`##`）切分**，不是一个文件一条；`source_line` 记该节起始行
- 每类来源单独统计，写完打印各来源条数

**完成标准**：`python -m py_compile` 通过。

### 步骤 4 · 建库

```bash
"$VENV/bin/python" .../hj-corpus-build-index.py --repo "$HOME/Desktop/vibe-trading/Herman Jin"
```

建完必须跑 FTS 重建：

```sql
INSERT INTO fts(fts) VALUES('rebuild');
```

**完成标准**（逐项核对，数字必须精确相等）：

| 检查项 | 期望值 |
|---|---|
| `origin='x-post'` | 1,273 |
| `origin='x-reply'` | 6,400 |
| `origin='yt-segment'` | 52,518 |
| `origin='yt-slide'` | 814 |
| `origin='research-doc'` | ≈133（= 二级标题数，允许 ±5 因标题层级判断） |
| 总行数 | 61,138 ± 5 |

### 步骤 5 · 验证行号锚点

任取 3 条 `yt-segment`，用其 `source_line` 打开源文件对应行，比对 `text`。

**完成标准**：3/3 一致。任一条不符则说明行号偏移，回到步骤 3 修正后再建。

### 步骤 6 · 验证繁简通搜

抽 20 个**繁体包**（如 `market-overview-2025-01-21`），对每个包搜简体词 `存储`，限定 `pkg_id` 与该包。

**完成标准**：20/20 包有命中。任一包零命中即归一化失效。

### 步骤 7 · 验证别名

```sql
SELECT COUNT(*) FROM records WHERE text_norm LIKE '%狗门%';   -- 期望 > 0
SELECT COUNT(*) FROM records WHERE text_norm LIKE '%J-PAL%';  -- 期望 > 0
```

**完成标准**：两条均 > 0。

### 步骤 8 · 写查询脚本

落点：`~/.workbuddy/skills/herman-jin-x-archive/scripts/hj-corpus-query.py`
接口见 §5.1。

**完成标准**：§5.1 表中 8 个示例全部返回合理结果。

### 步骤 9 · 挂指针

在 `agent-index.json` 的 `conventions` 中加一项：

```json
"corpus_index": {
  "db": "_index/herman-jin-corpus.db",
  "spec": "_index/CORPUS-INDEX-SPEC.md",
  "note": "跨来源语料检索。查原文、查标的、查专名前先读 spec。"
}
```

**完成标准**：`json.load()` 能解析，且原有 60 条 packages 未被改动。

---

## 5.1 查询接口

| 参数 | 作用 |
|---|---|
| `QUERY...` | 位置参数，空格分词 AND；中文自动 phrase |
| `--entity NAME` | 按标的查，自动展开别名 |
| `--from YYYY-MM-DD` / `--to` | 日期范围（本地时间） |
| `--origin LIST` | 逗号分隔，筛来源类型 |
| `--pkg ID` | 限定某个包/期 |
| `--layer LIST` | 默认 `evidence,conclusion` |
| `--include-slides` | 纳入 meta 层 |
| `--context N` | **邻接合并**，命中段 ±N 段（默认 3） |
| `--limit N` | 默认 20 |
| `--show` | 输出全文而非摘要 |
| `--cite` | 输出可复制的引用锚点 |
| `--stats` | 只出统计（命中数、按月分布、按包分布） |
| `--export PATH` | 导出 CSV/JSONL |

**必须实现的示例调用**：

```bash
hj-corpus-query.py "存储 涨价"
hj-corpus-query.py "HBM" --from 2026-05 --to 2026-07 --cite
hj-corpus-query.py "长鑫" --origin x-reply --limit 20 --show
hj-corpus-query.py --entity INTC --stats
hj-corpus-query.py "CPO" --pkg market-overview-2026-01-06 --context 5
hj-corpus-query.py "关稅" --stats          # 繁体查询词，须等价于"关税"
hj-corpus-query.py "Goldman" --stats       # 须同时计入"狗门"等别名
hj-corpus-query.py "AI" --layer evidence,conclusion --export /tmp/ai.jsonl
```

### 5.2 邻接合并（必做，不是可选）

视频每段平均 10.6 字符，单段命中没有可读性。命中后**必须**把相邻 `±--context` 段拼成连续文本再输出，并标注合并后的行号区间。

同一包内按 `source_line` 排序即得正确顺序（行号连续）。

---

## 6. 引用格式

索引输出必须能直接落进现有报告的引用体例。两种形态：

```
视频：[转录 L684–L715](../market-overview/market-overview-2025-01-21/transcript.jsonl#L684-L715)
X   ：[X 2026-05-13](../x-archive/x-2026-09-19/posts.jsonl#L123)
报告：[报告 herman-jin-core-views-transcript-draft L34](../research/herman-jin-core-views-transcript-draft.md#L34)
```

`--cite` 参数直接打印上面格式，路径**相对仓库根**，锚点用 `source_line`（合并结果用 `source_line`–`source_line_end`）。

引用附带原文时，短引文控制在 20 字以内（沿用现有报告的口径）。转述 ASR 数字（如"数据中心占比 60%"）时必须标注需回听。

---

## 7. 增量维护

新抓一批语料后：

1. 确认新数据已按既有约定落盘（视频进 `market-overview/`，X 进 `x-archive/`）
2. 重跑步骤 4 的构建脚本（**全量重建**，脚本按 `rec_id` 覆盖同 ID 记录）
3. 重跑步骤 5–7 的验证
4. 若新增了专名误识别，追加进 §10 附录 A 并重建

全量重建耗时估计：52,518 + 7,673 条，含分词与归一化，约 1–3 分钟。

**完成标准**：建库后各来源条数等于 §4 期望值 + 新增量。

---

## 8. 已知陷阱

每条都实际踩过或已核实，不要重新发现。

### 8.1 行号会因文件重写而失效

`source_line` 锚定的是**当时的文件状态**。若某包的 `transcript.jsonl` 被重新生成（重转写、补段落），行号全部偏移，已有报告的引用会指向错误位置。

**处置**：重建索引后发现行号变化，说明有源文件被重写，需同步修正引用过该包的 research 文档（或至少报告这一事实）。

### 8.2 thread_id 不可用

X 包的 `thread_id` 是抓取时机械配对的产物。实测：6,400 个 thread 中，含 2 条的恰好 1,273 个（= 主帖数），含 1 条的 5,127 个，**含 >5 条的 0 个**。真实讨论串不可能如此。

**处置**：索引照常收录该字段，但任何会话重建都不要依赖它。

### 8.3 in_reply_to_post_id 恒为空

6,400 条回复该字段全部为 null。我们只有"他回复了谁"，没有"他回复的是哪条"。

**处置**：不要在查询接口里暴露这个字段。

### 8.4 2026-01 的回复对象全缺

该月 438 条 `in_reply_to_user` 100% 为空，因抓取时脚本尚未修中文「回复 @xxx」正则；2 月起缺失率 0–6.7%。

**处置**：涉及 1 月回复指向的分析，明确标注该月无此信息。补齐需重新抓取，属抓取任务。

### 8.5 deck 的 OCR 噪声

`deck.jsonl` 的 `title`/`ocr` 普遍是 OCR 碎片，例：`"一 一 一 A Credibility H"`。`summary` 字段可用，`ocr` 需打 `ocr-garbage` 标记。

**处置**：`meta` 层默认排除在检索之外。

### 8.6 别名表无法穷尽

同一实体的误识别形态会持续出现（Nonfarm 已知就有"能防配肉""飞龙就业""能放配入""農狂配合"四种）。别名表只能覆盖**已确认**的项。

**处置**：对英文专名做音近召回（如 `Goldman` 同时试 `guomen`/`拱门`），并把新发现的形态追加进附录 A。**不要**因为别名表存在就假定检索无漏。

### 8.7 视频段的绝对时间为推算值

`transcript.jsonl` 只有段内相对秒数。`created_at` 由"包日期 + start 秒"推算，精度到天，用于**排序**足够，用作精确时间点不可靠。

### 8.8 卡片式短文本占比高

X 语料 62% 短于 30 字符，含 447 条纯表情。检索命中大量 😂/👍 属正常，用 `tier` 过滤而非人工排查。

### 8.9 仓库基线是脏的，不能直接读 git status

执行建库前，仓库**已有未提交改动**：`_readable/` 下 3 个 html 处于被删状态、`_source/_pipeline/` 4 个文件被修改、3 个包的 manifest 被改、`agent-index.json` 已修改，另有大量 untracked 的新包与研究报告。

**处置**：判断"是否误伤原文"必须用**增量比对**——建库前后各跑一次 `git status --short -- "Herman Jin"` 并 diff 两次输出，看新增了什么，而不是看绝对状态。见 §11 第 10 项。

---

## 9. 硬性规则

1. **原始文件只读**。任何 `posts.jsonl`/`replies.jsonl`/`transcript.jsonl`/`deck.jsonl`/`manifest.json`/`research/*.md` 都不得修改。索引是派生物，删了可重建；原文删了不可恢复。
2. **不改仓库顶层结构**。索引库与本文档放 `_index/`。正式包顶层严格 5 项（manifest.json、posts.jsonl、replies.jsonl、media/、raw/），视频包同理，不得增删。
3. **不把结论当证据**。`layer='conclusion'` 的记录是二手材料，引用时必须标注是报告结论而非他的原话。
4. **引用必须可回溯**。任何引用都要带 `source_path` + `source_line`，能回到原文。
5. **短引文 ≤20 字**，数字需回听标注。
6. **行号验证是建库的强制步骤**，跳过会导致全部引用静默错位。

---

## 10. 附录 A：别名表（照抄）

两组来源，均已由现有研究确认。

### A.1 实体与专名

| 归一化后的误识别形态 | 标准名 | 出处 |
|---|---|---|
| 狗门 | Goldman Sachs | audit §2.2 |
| 拱门 | Goldman Sachs | audit §2.2 |
| 国门 | Goldman Sachs | audit §2.2 |
| prambo | prime broker (GS Prime) | reading §附 |
| j-pal | Powell | audit §2.2 |
| jpal | Powell | audit §2.2 |
| wash | Warsh | reading §附 |
| water | Waller | reading §附 |
| celicon 百里版 | SVB | reading §附 |
| andopic | Anthropic | reading §附 |
| anthopia | Anthropic | reading §附 |

### A.2 概念与指标

| 归一化后的误识别形态 | 标准名 | 出处 |
|---|---|---|
| 能防配肉 | Nonfarm Payrolls | audit §2.2 |
| 飞龙就业 | Nonfarm Payrolls | audit §2.2 |
| 能放配入 | Nonfarm Payrolls | reading §附 |
| 农狂配合 | Nonfarm Payrolls | reading §附 |
| 小石心 | 时薪 | reading §附 |
| 小石的薪水 | 时薪 | reading §附 |
| 硬潜 | 印钱 | reading §附 |
| 硬体 | 印钱 | reading §附 |
| normano gdp | Nominal GDP | reading §附 |
| 贺皮书 | 褐皮书 | reading §附 |
| 个别脸 | billion | reading §附 |
| 55 开 | 五五开 | reading §附 |
| volvix | VIX | audit §2.2 |
| 卖房 | 卖方 | draft §证据口径 |

> 表内形态均已是**归一化后**（繁→简）的写法。"農狂配合"→"农狂配合"、"硬潛"→"硬潜"、"賀皮書"→"贺皮书"、"個別臉"→"个别脸"、"開"→"开"。

---

## 11. 附录 B：验收清单（一次性跑完）

建库完成后，逐条执行并记录结果：

| # | 检查 | 命令/方法 | 期望 |
|---|---|---|---|
| 1 | 依赖可用 | `import zhconv` | 成功 |
| 2 | 别名数 | `SELECT COUNT(*) FROM aliases` | ≥ 25（A.1+A.2 共 25 条） |
| 3 | 各来源条数 | §4.2 五个 origin 分别 count | 见步骤 4 表 |
| 4 | 行号锚点 | 3 条随机抽样回源核对 | 3/3 一致 |
| 5 | 繁简通搜 | 20 个繁体包搜「存储」 | 20/20 命中 |
| 6 | 别名召回 | 搜「狗门」「j-pal」 | 均 > 0 |
| 7 | 邻接合并 | 视频查询结果含合并文本 | 是 |
| 8 | 引用可回溯 | `--cite` 输出的锚点能打开 | 是 |
| 9 | 指针已挂 | `agent-index.json` 含 `corpus_index` | 是，且 packages 仍为 60 |
| 10 | 原文未改（**增量比对**） | 建库前后各跑 `git status --short -- "Herman Jin" > /tmp/gs-before.txt`（及 after），`diff` 两者 | 增量**仅含** `_index/` 与 `agent-index.json` |

第 10 项是最后一道防线。注意用**增量**而非绝对状态——仓库基线已含 25 项既有改动（见 §8.9）。若增量里出现任何 `jsonl`/`md` 数据文件，说明构建脚本写错了目标路径，立即 `git restore` 回退。

---

*文档版本：v1 · 2026-09-19*
*对应语料快照：X 至 2026-09-19、视频至 2026-09-15*
