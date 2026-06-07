# X Trader Analysis

爬取 X (Twitter) 加密/交易博主的长期历史推文，由 Claude Code 当前会话直接做结构化分析，输出量化分析师风格的交易员画像报告。

## 核心特点

- **零额外推理成本**: 分析由 Claude Code 当前会话完成，不调用任何外部 LLM API
- **结构化输出**: 5 个维度 × 置信度 × 原文证据引用
- **Renaissance Tech 量化风格**: 精确、保守、量化导向、显式标注不确定性
- **可复现 pipeline**: 爬虫 → 预处理 → 分析 三段解耦

## 5 分钟上手

### 1. 准备环境

```bash
# 已有 vibe-trading 仓库根目录的 .venv 即可
uv sync

# 配置爬虫凭证
cp .env.example .env
vim .env  # 填 APIFY_TOKEN 或准备 cookies.json
```

### 2. 爬取一个博主

```bash
# 方案 A: twscrape 账号池 (主力, 常态化推荐, 零边际成本)
#   首次需先添加至少 1 个 X 小号到账号池:
make account-add ARGS="--username u1 --cookies 'auth_token=xxx; ct0=yyy'"
make scrape USER=ShanghaoJin SINCE=2023-01-01 UNTIL=2026-05-17

# 方案 B: Scweet (本地单号, 需 X 登录 cookies.json)
make scrape-scweet USER=ShanghaoJin SINCE=2023-01-01 UNTIL=2026-05-17

# 方案 C: Apify (一次性大批量兜底, 付费, 需 APIFY_TOKEN)
make scrape-apify USER=ShanghaoJin SINCE=2023-01-01 UNTIL=2026-05-17
```

### 3. 预处理

```bash
make preprocess USER=ShanghaoJin
```

### 4. 触发分析

在 Claude Code 中说：

> 用 x-trader-analysis skill 分析 ShanghaoJin 的交易风格

会话会自动按 skill 流程执行，5-10 分钟后产出 `data/reports/ShanghaoJin_profile_YYYYMMDD.md`。

## 三种爬虫方案对比

| 方案 | 成本 | 稳定性 | 历史深度 | 维护 | 适用场景 |
|---|---|---|---|---|---|
| **twscrape 账号池** (主力) | 零边际 (自养 3-5 号) | 高 (多号轮询) | 无上限 (按月分片) | 每月重导 cookies | **常态化主力**：月度 1-3 博主长期复用 |
| **Scweet 单号** | 免费 | 中 (单号易封) | 受 3200 限制 | cookies 易过期 | 临时分析单个博主 |
| **Apify** | ~$1-2/博主 | 高 | 无上限 | 零维护 | **一次性大批量兜底**：年度全量回溯 |
| ~~X API v2~~ | $100-5000/月 | 高 | Basic 7d / Pro 半年 | 官方 SLA | 不适合本 skill 长历史分析 |

## Pipeline 流程图（文字版）

```
                     ┌──────────────────────┐
                     │  User: "分析 @xxx"    │
                     └──────────┬───────────┘
                                ↓
                     ┌──────────────────────┐
                     │ Claude Code 触发 skill │
                     └──────────┬───────────┘
                                ↓
                     ┌──────────────────────┐
                     │  检查 data/raw/*.jsonl │
                     └──────┬─────────┬─────┘
                            ↓不存在    ↓存在
                  ┌────────────────┐   │
                  │ 提示用户跑爬虫  │   │
                  │ make scrape-*   │   │
                  └────────┬───────┘   │
                           ↓           ↓
                  ┌──────────────────────────┐
                  │ scripts/scrape_*.py      │
                  │ → data/raw/{user}.jsonl  │
                  └──────────┬───────────────┘
                             ↓
                  ┌─────────────────────────────┐
                  │ scripts/preprocess.py       │
                  │ → data/enriched/{user}.jsonl│
                  │ → data/enriched/{user}_stats│
                  └──────────┬──────────────────┘
                             ↓
                  ┌──────────────────────────────┐
                  │ Claude Code 阶段一: 逐条抽取  │
                  │ (prompts/01_extract_per_tweet)│
                  └──────────┬───────────────────┘
                             ↓
                  ┌──────────────────────────────┐
                  │ 阶段二: 话题聚类               │
                  │ (prompts/02_cluster_topics)   │
                  └──────────┬───────────────────┘
                             ↓
                  ┌──────────────────────────────┐
                  │ 阶段三: 维度聚合               │
                  │ (prompts/03_aggregate_analysis)│
                  └──────────┬───────────────────┘
                             ↓
                  ┌──────────────────────────────┐
                  │ 阶段四: 生成报告               │
                  │ (prompts/04_profile_report)   │
                  └──────────┬───────────────────┘
                             ↓
                  ┌─────────────────────────────────┐
                  │ data/reports/{user}_profile_*.md│
                  └─────────────────────────────────┘
```

## 文件结构

```
.claude/skills/x-trader-analysis/
├── SKILL.md                          # Claude Code skill 入口 (核心)
├── README.md                         # 本文件
├── Makefile                          # 一键命令
├── .env.example                      # 凭证模板
├── prompts/
│   ├── 01_extract_per_tweet.md       # 阶段一: 单条抽取 schema
│   ├── 02_cluster_topics.md          # 阶段二: 话题聚类
│   ├── 03_aggregate_analysis.md      # 阶段三: 维度聚合
│   └── 04_profile_report.md          # 阶段四: 最终报告模板
└── examples/
    └── sample_report.md              # 示例输出
```

配套 Python 脚本 (位于本 skill 目录下 `scripts/` 子目录):

```
.claude/skills/x-trader-analysis/scripts/
├── scrape_twscrape.py     # 主力：twscrape 账号池 (常态化推荐)
├── scrape_apify.py        # 一次性大批量兜底 (付费)
├── scrape_scweet.py       # 单号本地备用
├── account_pool/          # twscrape 账号池管理
│   ├── add_account.py     # 添加 X 小号
│   ├── health_check.py    # 检查账号池健康度
│   └── README.md          # 账号池详细说明
├── preprocess.py          # 清洗 + 实体抽取 + 噪音过滤 + 统计
├── _common.py             # 共享工具 (jsonl IO, 时间处理, 字段标准化)
└── _entities.py           # 实体抽取规则 (ticker, 杠杆, 止损等)
```

账号池 DB (`.account_pool/accounts.db`) 默认放本 skill 目录下，已加入 `.gitignore`。

数据落到项目根的 `data/` 目录:

```
data/
├── raw/{user}.jsonl                # 爬虫原始输出
├── enriched/{user}.jsonl           # 预处理后
├── enriched/{user}_stats.json      # 统计摘要
└── reports/{user}_profile_*.md     # 最终画像报告
```

## 已知限制

1. **上下文窗口**: 单次会话精读 ~300 条推文为安全上限。> 1000 条非噪音的账号需分层抽样
2. **中英文混合**: 中文推文的情绪/语气抽取依赖 LLM 上下文，对纯中文风格短句可能欠准
3. **删除推文**: 已删除的推文无法回溯，分析窗口只能覆盖现存的
4. **图表内容**: 推文里的图表（K 线截图、PNL 截图）目前不解析，仅做文本分析
5. **加密 alpha 群组泄露**: 不接入 Telegram / Discord 私群数据，仅公开推文
6. **言行验证缺失**: 报告本身不验证博主预测的胜率，需手动触发 K 线对齐增强

## FAQ

**Q: 为什么不直接让 Claude Code 同时做爬虫+分析？**
A: 爬虫涉及外部 API、网络重试、反爬规避、cookies 管理，更适合用确定性的 Python 脚本完成。Claude Code 擅长理解非结构化文本，但不该浪费 token 做 HTTP 请求重试。

**Q: 为什么不调外部 LLM API（GPT-4/Claude API）做分析？**
A: 当前会话已经是一个强力 LLM。分析任务的算力完全可以由本会话承担，调外部 API 反而引入：
- 额外金钱成本
- API key 管理负担
- 网络延迟
- 厂商锁定

**Q: 报告能直接做交易决策吗？**
A: 不能。报告是研究输入，揭示一位博主的历史风格分布，不构成对其未来预测准确性的背书。任何决策必须叠加：
- 言行一致性验证（K 线对齐）
- 多博主交叉验证
- 自有量化信号过滤

**Q: 支持非加密博主吗（股票/外汇）？**
A: prompt 模板偏加密语境（ticker 格式、术语）。换股票/外汇需要调整 `prompts/01_extract_per_tweet.md` 的 ticker 规范化部分。

**Q: 报告里的置信度怎么算的？**
A: 简化方案：
- 样本量 ≥ 20 条相关推文: 置信度上限 0.9
- 10-20 条: 上限 0.7
- 5-10 条: 上限 0.5
- < 5 条: 标 "unclear"
- 内部矛盾（同一维度证据互相打架）: 再扣 0.2
