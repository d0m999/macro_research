---
name: x-trader-analysis
description: 爬取 X 博主的长期历史推文并分析其交易风格、策略、风险偏好，生成结构化 Markdown 画像报告
when_to_use: 用户说"分析 X 博主 @某某 的交易风格"、"给我一份 X 博主 的交易员画像"、"研究下 @某某 的交易策略"、"扒一下 @某某 的历史推文"、"@某某 是哪种交易员" 时触发
---

# X Trader Analysis Skill

## 目标场景

把任意一位 X (Twitter) 加密/交易博主的长期历史推文（数百到数千条）转化为一份结构化的**交易员画像报告**。报告覆盖 5 个核心维度——交易品种与方向偏好、信号触发模式、风险管理风格、情绪/隐含立场、交易策略类型——每条结论都附带置信度和原文证据引用。

**核心创新**: 爬虫由 Python 脚本完成，分析由 Claude Code 当前会话直接执行——不调用任何外部 LLM API，零额外推理成本。会话本身就是分析引擎。

## 触发方式

用户在 Claude Code 中说出任何下列意图：

- "分析 X 博主 @某某 的交易风格"
- "给我一份 @某某 的交易员画像"
- "研究下 @某某 的交易策略"
- "扒一下 @某某 的历史推文"
- "@某某 是哪种交易员"
- "x-trader-analysis 分析 @某某"

只要识别出 X handle（带或不带 `@`），就启动此 skill。

## 执行流程

按下列步骤执行。每一步完成后给用户简短进度反馈，但不要 dump 中间数据。

### Step 0 — 解析输入

从用户消息抽取 X handle，规范化为不带 `@` 的字符串。例如：

- "分析 @ShanghaoJin 的交易风格" → `user = "ShanghaoJin"`
- "research @CryptoCobain" → `user = "CryptoCobain"`

询问可选时间范围（默认 `since=2023-01-01, until=today`）。如果用户没指定，使用默认值并告知。

### Step 1 — 检查数据是否就绪

按顺序检查：

```
data/raw/{user}.jsonl          # 原始爬虫输出
data/enriched/{user}.jsonl     # 清洗+实体抽取后
data/enriched/{user}_stats.json # 统计摘要
```

**情况 A** — `raw/{user}.jsonl` 不存在：
提示用户先爬虫。按优先级给三个选项：

```
该用户还没有原始数据，请选择爬虫方案：

1. twscrape 账号池方案 (推荐, 常态化主力, 零边际成本)
   首次需先加 X 小号到账号池 (推荐 cookies 模式):
     make account-add ARGS="--username u1 --cookies 'auth_token=xxx; ct0=yyy'"
   然后抓取:
     make scrape USER={user} SINCE=2023-01-01 UNTIL=2026-05-17
   查看账号池健康度:
     make account-health

2. Scweet 单号方案 (低频, 仅 1 个小号 cookies.json)
   make scrape-scweet USER={user} SINCE=2023-01-01 UNTIL=2026-05-17

3. Apify 方案 (一次性大批量兜底, 付费 ~$1-2/博主, 需 APIFY_TOKEN)
   make scrape-apify USER={user} SINCE=2023-01-01 UNTIL=2026-05-17

爬完回来再触发我，我会继续后面的分析。
```
停止，等用户回来。

**情况 B** — `raw/{user}.jsonl` 存在但 `enriched/{user}.jsonl` 缺失：
直接运行预处理：

```bash
uv run python .claude/skills/x-trader-analysis/scripts/preprocess.py \
  --in data/raw/{user}.jsonl \
  --out-enriched data/enriched/{user}.jsonl \
  --out-stats data/enriched/{user}_stats.json
```

(或在项目根直接 `make preprocess USER={user}` 走 Makefile)

**情况 C** — 全部就绪：
直接进入 Step 2。

### Step 2 — 读取统计摘要，向用户报告概况

`Read` 工具读取 `data/enriched/{user}_stats.json`，向用户简报：

```
数据已就绪 — 准备开始分析

- 总推文: N 条 (时间跨度: YYYY-MM-DD ~ YYYY-MM-DD)
- 去噪后样本: M 条 (噪音占比 X%)
- Top 5 tickers: BTC (A), ETH (B), SOL (C), ...
- 高频关键词: ...
- 平均发推频率: 每周 K 条

我将分 4 个阶段做分析，预计读取 ~300 条核心推文。开始执行...
```

### Step 3 — 阶段一: 逐条结构化抽取

按 `prompts/01_extract_per_tweet.md` 的 schema，分批读取 `enriched/{user}.jsonl` 中 `is_noise=false` 的推文：

**抽样策略**:
- 总样本控制在 300 条以内（避免上下文爆炸）
- 按时间倒序，最近 200 条全收
- 早期 1000 条随机抽样 100 条
- 必收: 含 ticker + 含数字（价格/百分比）的推文

**分批节奏**:
- 每批 50 条，用 `Read` 工具按行范围读 jsonl
- 对每条按 schema 做结构化抽取，结果写入内存 list
- **不要把抽取结果写到文件**——保留在会话上下文中即可
- 每批完成后给用户一行进度反馈，例如 `阶段 1 进度 100/300`

参考 `prompts/01_extract_per_tweet.md` 获取 schema 定义、字段约束、few-shot 示例。

### Step 4 — 阶段二: 话题聚类

按 `prompts/02_cluster_topics.md`：

1. 结合 `stats.json` 中的关键词频次 + 阶段一抽取的 `tickers` 频次
2. 归纳 5-8 个主话题群（例如 "BTC 突破跟踪", "DeFi 蓝筹轮动", "宏观利率反应"）
3. 每个话题给：标签 + 估计占比 + 3 条代表性 tweet_id

输出为内存中的 JSON 结构，供 Step 5 引用。

### Step 5 — 阶段三: 维度级聚合

按 `prompts/03_aggregate_analysis.md`：

对阶段一的逐条抽取结果，按 5 个维度聚合：

- **交易品种与方向**: tickers 频次 + long/short 占比 + 单品种方向倾斜度
- **信号触发模式**: signal_trigger 分布 + 触发关键词共现
- **风险管理风格**: 提及止损/杠杆/仓位的频率 + 数值分布
- **情绪/立场**: polarity 时间序列 + intensity 分布
- **策略类型**: strategy_style_hint 占比 + 持仓周期暗示

每个维度产出：核心结论 + 置信度 + 5-10 条 tweet_id 证据。

### Step 6 — 阶段四: 生成最终报告

按 `prompts/04_profile_report.md` 的模板，融合阶段二的话题聚类 + 阶段三的维度聚合，写出完整 Markdown 画像。

**关键约束**:
- 用 Renaissance Technologies 量化分析师的语气：精确、保留怀疑、量化证据
- 每个结论必须配置信度（0.0-1.0）和样本量
- 每个维度至少 3 条原文证据引用（≤30 字 + tweet_id + 日期）
- 显式列出"无法判断"的部分（不要硬编结论）

### Step 7 — 写报告到文件

确保目录存在: `data/reports/`

写入: `data/reports/{user}_profile_{YYYYMMDD}.md` （YYYYMMDD 用今天日期）

写完后告诉用户：

```
画像报告已生成: data/reports/{user}_profile_{YYYYMMDD}.md

核心结论 (TL;DR):
- ...
- ...

如需更深入分析，可以:
1. 跑历史 K 线对齐看言行一致性: ...
2. 增加爬虫时间范围重新分析
3. 针对某个维度深挖
```

## 可选增强

### 言行一致性验证 (K 线对齐)

如果用户进一步问 "他说看多 BTC 的那次是不是真的涨了"，可以：

1. 从报告抽取带方向判断的推文（tweet_id + 时间 + ticker + direction）
2. 用 CCXT 或 FreqTrade 已有的 `user_data/data/binance/` 历史数据拉对应时间窗 1h K 线
3. 计算预测后 24h / 7d / 30d 收益率，与方向标签做对比
4. 输出胜率 + 收益分布

此功能不在默认 pipeline 内，按需触发。

### 时间序列特征

如果数据跨度 > 1 年，附录段加入：

- 月度发推数热力图
- 月度情绪极性变化
- 关键宏观事件（半减、ETF、加息）前后 7 天的发推对比

## 限制说明

### 上下文管理

300+ 条推文不要一次性塞给会话。务必分批读取（每批 50 条），逐批做抽取后释放原文，仅保留结构化结果。

如果数据 > 1000 条非噪音推文：
- 先做粗筛（保留含 ticker 或含数字的）
- 早期数据按月份分层抽样
- 最近 30 天数据全收

### 噪音处理

`is_noise=true` 的推文不参与分析（GM、贴图、纯 RT、广告等）。但 `is_noise` 比例本身是个特征——噪音 > 50% 的账号画像可信度需打折。

### 中英文混合

很多华人加密博主中英混发，prompt 模板里有专门处理。tickers 用英文标准化（BTC 不是 比特币），但情绪/语气评估时尊重原文语言。

### 隐私 & 合规

仅分析公开推文，不调用任何需要登录态读取私信/锁推的接口。报告不暴露原始爬虫 cookies/token。

## 常见问题排查

**Q: 报告里某些维度全是 "unclear"？**
A: 样本量不足或博主该维度不发声。检查 stats.json 中相关关键词频次，可能需要扩大时间范围。

**Q: 置信度普遍偏低（< 0.5）？**
A: 该博主可能以转发/吐槽为主，缺乏明确交易信号。考虑过滤掉转推（`is_retweet=true`）后再分析。

**Q: 提示 "data/raw 不存在但 enriched 存在"？**
A: 不可能的状态。删除 enriched 重新爬。

**Q: 同一个用户多次分析？**
A: 重跑 Step 2-7。爬虫和预处理不需要重跑（除非要扩时间范围）。

**Q: 想分析多个博主对比？**
A: 单独跑每个博主的 pipeline，最后让 Claude Code 把多份报告拼到一个对比矩阵。不在 skill 默认范围内。

## 输出文件清单

成功执行后，产物：

```
data/raw/{user}.jsonl                        # 爬虫原始数据 (由 scrape_* 脚本生成)
data/enriched/{user}.jsonl                   # 清洗+抽取后 (由 preprocess.py 生成)
data/enriched/{user}_stats.json              # 统计摘要 (由 preprocess.py 生成)
data/reports/{user}_profile_YYYYMMDD.md      # 最终画像报告 (本 skill 生成)
```

只有最后一份 Markdown 报告需要呈现给用户。

## 脚本路径约定

爬虫与预处理脚本位于 `.claude/skills/x-trader-analysis/scripts/`：

- `scrape_twscrape.py` — **主力**：twscrape 账号池，常态化推荐
- `scrape_apify.py` — Apify Twitter Scraper（一次性大批量兜底，付费）
- `scrape_scweet.py` — Scweet 本地爬虫（单号备用）
- `account_pool/add_account.py` — 往 twscrape 账号池新增 X 小号
- `account_pool/health_check.py` — 检查账号池每个账号的可用性
- `preprocess.py` — 清洗 + 实体抽取 + 噪音过滤 + 统计聚合
- `_common.py` / `_entities.py` — 内部工具模块

账号池 DB 默认放在 `.claude/skills/x-trader-analysis/.account_pool/accounts.db`（已加入 `.gitignore`）。

所有路径在项目根 `vibe-trading/` 下相对引用即可。直接 `uv run python` 或通过 `make` 任一方式调用。
