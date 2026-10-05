# Project Instructions

## Scope

本仓库有两条并行的工作线，**优先级按活跃度排列**：

1. **【当前主线】KOL 语料归档 → 观点与推理链蒸馏。** 抓取 X 主帖/回复与 YouTube 视频转录，做 ASR 纠错、观点提炼、逻辑链还原与标的价格验证。目标是「从历史语料里找出推理逻辑和主要观点」，不是做 persona 复刻或表达风格模仿。
2. **【活跃支线】美股 / AI 产业链基本面研究。**  hyperscaler CAPEX、CoWoS/HBM 供需缺口、个股快速调研；以及公开数据源通道验证。
3. **【既有研究线，当前无活跃任务】TradingView PineScript 指标与 OI 逻辑。** 27 个 `.pine` 文件与配套研究笔记仍在，但 2026-09 以来没有新提交。**新任务进来时先确认它属于哪条线，不要默认按 Pine 线解释。**

Python/FreqTrade 程序化交易引擎、回测运行环境、交易数据库、Dashboard 和 Docker 部署已经移出当前工作区。未经明确授权，不要重新引入 Python 交易执行层。

## 主要目录

### 主线：KOL 语料

- `Herman Jin/`（1.6 GB）：@ShanghaoJin 的语料仓库。顶层 `agent-index.json` 是索引入口；视频包在 `market-overview-YYYY-MM-DD/`（62 个），X 包在 `x-archive/x-YYYY-MM-DD/`（manifest + `posts.jsonl` + `replies.jsonl` + `media/` + `raw/`），**现有 3 个包：x-2026-09-19 / x-2026-09-25 / x-2026-10-02**。另有 `_index/`（含 VECTORIZATION-SPEC、derived）、`_source/`、`_review/`、`research/`（上游笔记）、`data/`（15 个标的 `*_info.csv` / `*_news.csv`）。
- `Serenity/`：@aleabitoreddit 的 X 语料仓库。**两个主体是不同的人，勿混。**
  ⚠️ **与 `Herman Jin/` 并不同构**（旧描述有误，2026-10-05 实测更正）：目录里**没有** `x-archive/` 也没有 `_source/`，只有 `agent-index.json` + `data/clean/` 下 6 个文件（`posts.jsonl`、`replies.jsonl`、`source-evidence-2026-10-02.jsonl`、两份 `cleaning-report-*.md`、`dropped-emoji-only-ids.txt`）。要建正式包时按 `Herman Jin/x-archive/x-YYYY-MM-DD/` 的 11 键 manifest 结构新建，不要假设它已存在。
- `research/Herman-Jin 观点 rollup.md`：主线交付物（59 期、52,518 条转录，覆盖 2025-01 → 2026-09）。**该文件在 git 中未跟踪**，`git restore`/`git checkout` 对它无效；编辑前必须在库外自留副本并记录基线 MD5，改完用 `diff` 验证「只新增、无删除」。**修改授权是逐次给的，不得把一次的授权推广到后续编辑。**
- `research/_agent/`：语料与基本面研究的 agent 中间产物；入口与路径索引见 `research/_agent/README.md`。日期型语料增量包按 `corpus-updates/YYYY-MM-DD/` 归档；有主文档或复现引用的其他材料保留原路径。
  - `research/_agent/corpus-updates/2026-10-02/`：Herman Jin 与 Serenity 的增量核查、证据 JSON、导入校验及包内索引。包内各文件的互链保持相对路径。

### 支线：基本面研究

- `research/_agent/intc-cpu-analysis-2026-09-26/`：**在跑的个股深研**，主文档 `README.md`（「INTC 与 CPU 行业：把需求、交付和股东收益接起来」）。它把主线蒸馏出的 Herman Jin / Serenity 方法卡套用到 INTC 上，是两条线的接口。配套 `chain-2-price-margin.md`（链条二 缺货与价格·利润）、`intel-primary.md`（一手财报/SEC 证据）。**进度：四条检查链条中仅链条二成稿，链条三（架构与份额）、链条四（代工/摊薄/估值）待做。** 另有 9/27 遗留项：美光 FY26Q4 业绩（2026-09-30 公布）是链条二的关键验证点，未回填。
  - ⚠ 易混淆：`research/Herman-Jin 观点 rollup.md` 是人物观点库（按观点编号组织），**不是** CPU 行业研究的主文档。
- `GLW/`：Corning（CIK 0000024741）的 11 类公开数据源通道验证，含 `PASS` / `PARTIAL` / `SOURCE_UNAVAILABLE` 分级。是一次性验证产物，可作「公开来源优先、付费能力可选」工作流的样板。
- `.agents/skills/`：16 个金融分析 skill（3-statement-model / comps-analysis / earnings-analysis / initiating-coverage / thesis-tracker 等），源自 Anthropic financial-services 导入。
- `fundamental-research/`：Anthropic / Claude 官方金融研究工作流的调研记录。

### 既有研究线：Pine 与 OI

- `PineScript/`：Pine v6 研究指标。按 `_L∞p/`、`Open Interest/`、`Oscillator/`、`Price_Zones/`、`Vol/` 分类。
- `strategy-notes/`：策略假设、指标组合、OI 语义和待验证事项。
- `strategy-notes/design/`：OI 面板及相关视觉研究 artifact；当前同时保留已跟踪基线与本地未跟踪版本。
- `open-interest-logic.md`：OI 方向、门限、veto 和可视化语义的补充说明。
- `docs/`：与研究流程相关的文档；不要把已移除的 Python/FreqTrade 运行说明加回来。

## 研究约束

### 语料与观点蒸馏（主线，必读）

- **交付物是「逻辑链 + 观点清单 + 验证状态 + 极性」，不是 persona。** 用户明确不要角色扮演、表达 DNA、盲测这类产物。
- **检索必须覆盖繁简两种字形。** `Herman Jin/` 60 个包里 30 个以简体为主、30 个以繁体为主，只用一种字形做关键词检索会漏掉约一半语料。一律用 `繁體|简体` 双形正则（如 `電力|电力`、`缺貨|缺货`）。
- **引用必须先回锚再落笔。** ASR 误识常见（`賣房市場`=賣方市場、`能放配入`=非农就业、`boom energy`=Bloom Energy）。
- **区分「语料命中」与「本人推荐」，并标注极性。** 例：MU 在语料出现 4 期，但社媒明确说「我覺得美光很貴」——是反例不是推荐。引用标的清单前查极性列（配 `research/_agent/herman-jin-社媒推荐标的与言论-*.md`）。
- **不要把宣传稿措辞当成他本人说的话。** 例：「蒸汽机等级的变革」出自 168X 宣传稿，转录中零命中；「token 工厂」是他明说援引黄仁勋，非原创。
- **上游笔记的可靠度分级**：`herman-jin-core-reasoning-chain.md` / `main-views-since-2025.md` 可作骨架，但 `main-views-since-2025.md` 的电力/并网腿**过度陈述**（语料里很薄，更像社媒单次表态）；`herman-jin-screen-2026-09-09.md` 是**按他的链条筛出的推导结果，不是他本人的推荐**。

### Pine 与 OI（既有研究线）

- 先确认 Pine 文件的输入源、时间周期、是否使用未收线数据和重绘边界，再修改信号逻辑。
- `ΔOI` 的符号语义、价格方向着色、幅度门限和 veto 状态必须分开，显示降噪不得改变裁决真值。
- 研究指标和设计 artifact 的状态要分开描述；打开 mockup 不代表 Pine 已实现同等功能。
- 不把 TradingView 价格/永续数据自动等同于原生交易所 OI；数据来源必须在注释或研究笔记中写清楚。
- 数据来源的确定与引用必须从 `.agents/data-sources.jsonl` 路由（本项目 skill 数据源路由的单一事实来源）；来源合规与状态语义遵循 `.agents/PUBLIC-SOURCE-POLICY.md`。

## 验证方式

- PineScript：优先做静态扫描、版本/语法检查和 TradingView 内的人工编译与图表验收。
- 研究 artifact：核对文件版本、Git 状态和数据来源，不覆盖用户的未跟踪文件。
- 图表类产物：脚本末尾打印关键数值自检，配 `*-notes-YYYY-MM-DD.md` 记录数据表、口径限制与复现命令。
- 自动化校验：`.agents/tests/` 下有一组 unittest（金融 artifact 结构校验，4 个用例）——`python3 -m unittest discover -s .agents/tests -p 'test_*.py'`。**本机没有 pytest**，不要写 pytest 命令。
- 没有程序化交易运行命令，也不要重建一套。

## Git 约束

- 保留用户已有的未跟踪 artifact；不要使用 `git add -A`、强制重置或覆盖式清理。
- 修改、提交、推送和发布是分开的授权；本仓库默认只做本地修改。

### Git 现状（2026-10-05 盘点）

- **239 项改动未提交**：`38 ?? + 93 D + 108 M`。其中 **93 个删除全在 `.agents/skills/`**（Anthropic 导入包被裁剪，剩余 16 个）。落库前先逐批确认，不要一次 `git add -A`。
- **`.git` 1.5 GB 来自 Herman Jin 整体入库**：`git ls-files | grep "Herman Jin"` = 3369 个文件（png 1717 / txt 903 / json 350 / jsonl 184 / srt 57 / m4a 57 / vtt 56 / csv 15 / md 14）。这是历史既成事实，与本条「不要 wholesale 提交语料」的约束相悖；出库方案（会重写历史、影响已推送分支）待用户确认后再动。
- **`.env` 未被跟踪**（`.gitignore` 已覆盖），但内含真实凭据：交易所 API key/secret、OKX 只读密钥、JWT/WS token、DB_URL、Telegram token —— 全部是已移出的 FreqTrade 遗留物，权限 600。**处置方式（轮换或删除）待用户决定，不得自行删除。**
- **顶层 `罗老师-2026-06-15/`**（356 KB）被 `.gitignore` 忽略、不入库，且三份文档此前均未提及；属独立本地仓库性质的目录。

## Agent skills

### Issue tracker

Issues and specs are tracked in this repository's GitHub Issues via `gh`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the five canonical triage labels defined for this repository. See `docs/agents/triage-labels.md`.

### Domain docs

This repository uses a single-context layout with root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
