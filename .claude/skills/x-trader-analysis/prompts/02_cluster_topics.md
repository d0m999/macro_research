# 阶段二: 话题聚类与代表性样本标注

## 任务说明

阶段一抽取了每条推文的结构化字段。阶段二的目标是从 stats.json 的高频关键词 + 阶段一的 ticker 频次中，**归纳 5-8 个主话题群**，并为每个话题选 3 条最有代表性的推文。

这是为最终报告的"附录：关键推文摘录"和"6. 时间序列特征"段落服务的中间产物。

## 输入

- `data/enriched/{user}_stats.json` — 含关键词频次、ticker 频次、月度发推量
- 阶段一的内存结构化结果（list of extracted JSONs）
- 原始 jsonl 中对应的 tweet_id 文本（按需读）

## 话题归纳方法

### Step 1: 候选话题源

从下列信号源汇总成"候选话题词袋"：

1. **stats.json 中的 Top 30 关键词**（已去停用词、去 ticker）
2. **阶段一的 ticker 频次** — 主导品种本身可以独立成话题（如 "BTC 主线"）
3. **signal_trigger 高频值** — 比如 `macro` 占比 > 20%，独立成"宏观叙事"话题
4. **strategy_style_hint 高频值** — 比如 `technical` 高频则有"技术派分析"话题

### Step 2: 合并相似词

把同义/相关词归到同一桶：

| 桶名 | 包含词举例 |
|---|---|
| 突破跟踪 | 突破 / break / 站上 / 攻克 / 新高 |
| 回踩布局 | 回踩 / pullback / 回调 / 二次确认 |
| 宏观叙事 | Fed / 美联储 / 加息 / CPI / 流动性 |
| 链上数据 | 鲸鱼 / 链上 / 资金费率 / OI / funding |
| ETF & 机构 | ETF / 贝莱德 / blackrock / 灰度 / institutional |
| Altcoin 轮动 | 山寨 / alt / season / 轮动 / rotation |
| 防御与避险 | 减仓 / 离场 / 空仓 / 观望 / 风控 |
| 情绪宣泄 | 牛市 / 熊市 / 狂欢 / 投降 / 屠杀 |

允许加项目特定话题（如 "MEME 季"、"DeFi 复兴"）如果数据明确支持。

### Step 3: 估算话题占比

对每个话题，扫描阶段一结果：

```
topic_share = (该话题相关推文数) / (非噪音推文总数)
```

判定"相关"的规则：

- 推文 text 含话题桶里的任意关键词 (≥1 个)
- 或 `signal_trigger` / `strategy_style_hint` 匹配
- 同一推文可归多个话题（不互斥）

### Step 4: 挑选代表性样本

每个话题挑 3 条 tweet_id：

- **最高 `confidence_overall`** 的 1 条（典型样本）
- **互动量最高**（likes + retweets * 2 最大）的 1 条（影响力样本）
- **最近一条**（时间最新）的 1 条（当前态度样本）

如果话题相关推文 < 3 条，全收，不强求 3 条。

## 输出结构

阶段二的输出存在会话内存里，结构如下：

```json
{
  "topics": [
    {
      "topic_id": "T1",
      "label": "BTC 突破跟踪",
      "share": 0.32,
      "tweet_count": 96,
      "keywords": ["突破", "70k", "新高", "break"],
      "dominant_tickers": ["BTC"],
      "representative_tweets": [
        {
          "tweet_id": "1011",
          "role": "highest_confidence",
          "excerpt": "BTC 突破 70k 阻力, 3x 杠杆开多",
          "created_at": "2024-05-12"
        },
        {
          "tweet_id": "2034",
          "role": "highest_engagement",
          "excerpt": "...",
          "created_at": "2024-06-03"
        },
        {
          "tweet_id": "3119",
          "role": "most_recent",
          "excerpt": "...",
          "created_at": "2025-12-08"
        }
      ]
    },
    {
      "topic_id": "T2",
      "label": "宏观叙事 (Fed/流动性)",
      "share": 0.18,
      ...
    }
  ],
  "topic_count": 7,
  "coverage": 0.86
}
```

`coverage` = 至少归到一个话题的推文 / 非噪音推文总数。理想 > 0.8。

如果 coverage < 0.6，说明话题归纳颗粒度太粗，增加 1-2 个"其他"细分话题。

## 中英文混合处理

很多华人加密博主中英混发。处理策略：

1. **关键词归一**: 中文"突破"和英文 "breakout" 归到同一话题桶 `T_breakout`
2. **话题 label 双语**: 输出 label 用中文为主，括号附英文，如 `"BTC 突破跟踪 (Breakout)"`
3. **代表性样本不翻译**: `excerpt` 保留原始语言，不要做机翻

## 质量检查清单

阶段二完成前自检：

- [ ] 5 ≤ 话题数 ≤ 8（< 5 太粗，> 8 太碎）
- [ ] 所有话题占比之和不需要 = 1（允许重叠），但单个话题 share < 0.05 应合并掉
- [ ] coverage > 0.6（否则增加细分话题）
- [ ] 每个话题至少 1 条代表性推文
- [ ] 主话题的 dominant_tickers 与 ticker 频次榜前列对得上

## 输出节奏

阶段二只需要在会话内存中构建好上述 JSON 结构，**不写文件**。直接进入阶段三。

向用户报告一行：

```
阶段 2 完成: 识别 7 个主话题, coverage 86%
T1 BTC 突破跟踪 (32%) | T2 宏观叙事 (18%) | T3 链上数据 (12%) | ...
```
