# 阶段三: 维度级聚合分析

## 任务说明

阶段一产出了每条推文的结构化字段（list of extracted JSONs）。
阶段二归纳了话题聚类。
阶段三的目标是把这些数据聚合成**5 个维度的量化结论**，为最终报告（阶段四）提供论据。

每个维度产出：核心结论 + 置信度 + 5-10 条 tweet_id 证据 + 关键数字。

## 聚合的整体原则

1. **不臆测**: 样本量 < 5 的子分类只标"低样本"，不下结论
2. **显式不确定性**: 任何置信度都来自样本量 + 一致性两个因素
3. **量化语言**: 用 "占比 32%" 而不是 "经常"，用 "样本 N=87" 而不是 "很多"
4. **保留反例**: 主结论 + 至少 1 条矛盾证据，体现真实性

## 置信度计算规则

```
样本量分级:
  N ≥ 50  → 上限 0.95
  N ≥ 20  → 上限 0.85
  N ≥ 10  → 上限 0.70
  N ≥ 5   → 上限 0.50
  N < 5   → 标 "unclear" (不输出结论, 仅描述样本不足)

一致性折减:
  主选项占比 > 70%      → -0.0
  主选项占比 50-70%    → -0.10
  主选项占比 30-50%    → -0.20
  主选项占比 < 30%     → -0.30 (考虑标 "不明显倾向")

最终 confidence = min(样本量上限, 1.0 - 一致性折减)
四舍五入到 0.1
```

## 维度 1: 交易品种与方向偏好

### 聚合输入

阶段一所有非噪音推文的 `tickers` 和 `direction` 字段。

### 计算

```python
# 伪代码
ticker_counter = {}                # ticker -> 出现次数
ticker_direction = {}              # ticker -> {long: int, short: int, neutral: int, unclear: int}

for tweet in non_noise_tweets:
    if not tweet.tickers: continue
    primary_ticker = tweet.tickers[0].symbol   # 取置信度最高的
    ticker_counter[primary_ticker] += 1
    direction = tweet.direction
    ticker_direction[primary_ticker][direction] += 1

# Top 5 tickers
top_tickers = sorted(ticker_counter.items(), key=lambda x: -x[1])[:5]

# 每个 top ticker 的方向倾斜
for ticker, total in top_tickers:
    d = ticker_direction[ticker]
    long_share = d['long'] / total
    short_share = d['short'] / total
    skew = long_share - short_share   # > 0.3 多头倾向, < -0.3 空头倾向, 否则中性
```

### 输出结构

```json
{
  "dimension": "trading_targets_and_direction",
  "top_tickers": [
    {
      "symbol": "BTC",
      "count": 142,
      "share_in_universe": 0.47,
      "direction_distribution": {"long": 0.62, "short": 0.18, "neutral": 0.08, "unclear": 0.12},
      "directional_skew": 0.44,
      "verdict": "明显多头倾向"
    },
    ...
  ],
  "overall_confidence": 0.85,
  "summary": "BTC 主导 (47% 份额), 整体多头偏好 (long/short = 3.4x)。次主 ETH/SOL 同样多头, 但 SOL 中性度更高。",
  "evidence_tweet_ids": ["1011", "2034", "3119", "4221", "5018"]
}
```

## 维度 2: 信号触发模式

### 聚合输入

`signal_trigger` 字段。

### 计算

```python
trigger_counter = {breakout: 0, pullback: 0, event: 0, technical_pattern: 0, macro: 0, unclear: 0}
for tweet in non_noise_tweets:
    trigger_counter[tweet.signal_trigger] += 1

# 过滤 unclear 后看其余分布
clear_triggers = {k: v for k, v in trigger_counter.items() if k != 'unclear'}
total_clear = sum(clear_triggers.values())
shares = {k: v/total_clear for k, v in clear_triggers.items()}
```

### 衍生分析

- **进场偏好**: breakout 占比 vs pullback 占比 — 哪种更主导？
  - breakout > pullback * 1.5 → "追势型"
  - pullback > breakout * 1.5 → "逆势型"
  - 接近 → "混合型"
- **基本面 vs 技术面**: (event + macro) 占比 vs (technical_pattern + breakout + pullback) 占比

### 输出结构

```json
{
  "dimension": "signal_trigger_patterns",
  "trigger_distribution": {
    "breakout": 0.34,
    "pullback": 0.12,
    "event": 0.08,
    "technical_pattern": 0.21,
    "macro": 0.18,
    "unclear": 0.07
  },
  "primary_trigger": "breakout",
  "primary_share": 0.34,
  "entry_style": "追势型 (breakout 占比 2.8x pullback)",
  "fundamental_vs_technical": "技术主导 (技术 55% vs 基本面 26%)",
  "overall_confidence": 0.80,
  "summary": "以技术派 breakout 跟随为主, 辅以宏观叙事。事件驱动占比低。",
  "evidence_tweet_ids": ["1011", "2034", "5018", "6122"]
}
```

## 维度 3: 风险管理风格

### 聚合输入

`risk_signals` 子结构。

### 计算

```python
# 杠杆使用
leverage_mentions = [t for t in tweets if t.risk_signals.leverage is not None]
leverage_share = len(leverage_mentions) / len(non_noise_tweets)
if leverage_mentions:
    leverage_values = [t.risk_signals.leverage for t in leverage_mentions]
    median_leverage = median(leverage_values)
    p90_leverage = percentile(leverage_values, 90)

# 止损纪律
sl_mentions = sum(1 for t in tweets if t.risk_signals.stop_loss_mentioned)
sl_share = sl_mentions / len(non_noise_tweets)

# 仓位分布
position_counter = {light: 0, medium: 0, heavy: 0, all_in: 0, unclear: 0}
```

### 风险等级判定

```
止损提及率 sl_share:
  > 0.20  → 高纪律 (主动谈风控)
  0.05-0.20 → 中纪律
  < 0.05  → 低纪律或风控隐式

杠杆中位数:
  ≥ 10x → 激进
  3-10x → 中等
  < 3x  → 保守
  null  → 不使用杠杆 或 现货为主

heavy + all_in 占比:
  > 0.15 → 倾向重仓
  < 0.05 → 倾向轻仓
```

### 输出结构

```json
{
  "dimension": "risk_management_style",
  "leverage_usage": {
    "mention_rate": 0.18,
    "median": 5.0,
    "p90": 10.0,
    "max": 25.0,
    "verdict": "中等杠杆 (5x 中位数)"
  },
  "stop_loss_discipline": {
    "mention_rate": 0.22,
    "verdict": "高纪律"
  },
  "position_sizing": {
    "distribution": {"light": 0.12, "medium": 0.58, "heavy": 0.18, "all_in": 0.02, "unclear": 0.10},
    "verdict": "常规仓位为主, 偶有重仓"
  },
  "overall_risk_profile": "中等风险偏好 + 高纪律 — 谈杠杆也谈止损",
  "overall_confidence": 0.75,
  "summary": "杠杆使用率 18%, 中位 5x。止损提及率 22% 高于行业均值。重仓率 18% 中等。",
  "evidence_tweet_ids": ["1011", "3119", "4221", "7012", "8045"]
}
```

## 维度 4: 情绪 / 隐含立场

### 聚合输入

`sentiment.polarity` 和 `sentiment.intensity`。

### 计算

```python
# 总体极性
polarities = [t.sentiment.polarity for t in non_noise_tweets]
mean_polarity = mean(polarities)
median_polarity = median(polarities)
std_polarity = stdev(polarities)

# 极性分桶
buckets = {
    "extreme_bear": (-1.0, -0.5),
    "mild_bear": (-0.5, -0.1),
    "neutral": (-0.1, 0.1),
    "mild_bull": (0.1, 0.5),
    "extreme_bull": (0.5, 1.0)
}
bucket_shares = ...

# 时间序列 (按月)
monthly_polarity = {}  # YYYY-MM -> mean polarity

# 强度分布
intensity_counter = {calm: 0, excited: 0, fomo: 0, panic: 0}
```

### 隐含立场判定

```
mean_polarity > 0.3  → 偏多
mean_polarity 0.1-0.3 → 略偏多
mean_polarity -0.1-0.1 → 中性
mean_polarity -0.3 ~ -0.1 → 略偏空
mean_polarity < -0.3 → 偏空

std_polarity > 0.5 → 情绪波动大
std_polarity < 0.3 → 情绪稳定
```

### 输出结构

```json
{
  "dimension": "sentiment_and_implicit_stance",
  "polarity_stats": {
    "mean": 0.32,
    "median": 0.40,
    "std": 0.45
  },
  "polarity_buckets": {
    "extreme_bear": 0.05,
    "mild_bear": 0.12,
    "neutral": 0.21,
    "mild_bull": 0.38,
    "extreme_bull": 0.24
  },
  "intensity_distribution": {
    "calm": 0.42,
    "excited": 0.38,
    "fomo": 0.15,
    "panic": 0.05
  },
  "implicit_stance": "整体偏多 (62% bullish vs 17% bearish)",
  "emotional_volatility": "情绪波动中等 (std 0.45)",
  "monthly_polarity_trend": {
    "2024-01": 0.18,
    "2024-02": 0.35,
    "...": "..."
  },
  "overall_confidence": 0.85,
  "summary": "长期看多偏好明显, 但保留 17% 看空表达, 不是无脑多。FOMO 占比 15% 适中。",
  "evidence_tweet_ids": ["1012", "2034", "5018", "9001", "9002"]
}
```

## 维度 5: 交易策略类型

### 聚合输入

`strategy_style_hint` 字段 + 阶段二的话题聚类结果。

### 计算

```python
style_counter = {scalping: 0, swing: 0, long_term: 0, macro: 0, technical: 0, orderflow: 0, unclear: 0}
for tweet in non_noise_tweets:
    style_counter[tweet.strategy_style_hint] += 1

clear_styles = {k: v for k, v in style_counter.items() if k != 'unclear'}
total = sum(clear_styles.values())
shares = {k: v/total for k, v in clear_styles.items()}

# 主导风格 = 占比最高的
primary_style = max(shares, key=shares.get)
primary_share = shares[primary_style]

# 副风格 = 第二高且 > 15%
secondary_styles = [k for k, v in shares.items() if k != primary_style and v > 0.15]
```

### 持仓周期推断

通过 strategy_style_hint 反推持仓周期：

```
scalping → 分钟-小时
swing    → 数天-数周
long_term → 数月-数年
macro    → 数月-数年
其他 → unclear
```

### 输出结构

```json
{
  "dimension": "trading_strategy_type",
  "style_distribution": {
    "scalping": 0.05,
    "swing": 0.28,
    "long_term": 0.12,
    "macro": 0.18,
    "technical": 0.32,
    "orderflow": 0.05,
    "unclear": 0.00
  },
  "primary_style": "technical",
  "primary_share": 0.32,
  "secondary_styles": ["swing", "macro"],
  "inferred_holding_period": "数天-数周 (swing) 为主, 部分宏观长周期",
  "style_blend_label": "技术派波段 + 宏观叙事",
  "overall_confidence": 0.80,
  "summary": "策略主体是技术派波段, 32% 技术分析 + 28% swing 持仓。宏观叙事占 18% 作为方向背书。订单流类型仅 5%。",
  "evidence_tweet_ids": ["1011", "2034", "3119", "5018"]
}
```

## 跨维度衍生指标

### 时间序列特征（可选, 数据跨度 > 6 月再做）

```json
{
  "tweet_frequency": {
    "by_month": {"2024-01": 45, "2024-02": 62, ...},
    "by_dayofweek": {"Mon": 0.12, ..., "Sun": 0.10},
    "by_hour_utc": {"00": 0.02, ..., "23": 0.05}
  },
  "active_periods": ["2024-03 ETF 通过期", "2024-11 美选举前后"],
  "quiet_periods": ["2024-07 长尾"]
}
```

### 自相矛盾点（关键洞察）

扫描以下情况：

1. **方向反转**: 同一 ticker 在 ≤ 7 天内 long → short 切换 ≥ 2 次
2. **言行不一**: 风险维度说 "重仓+无止损"，情绪维度同期 panic
3. **风格漂移**: 6 个月窗口看 strategy_style_hint 主导项变化

输出列表：

```json
{
  "contradictions": [
    {
      "type": "direction_reversal",
      "ticker": "BTC",
      "evidence": [
        {"tweet_id": "1011", "created_at": "2024-05-12", "direction": "long"},
        {"tweet_id": "1098", "created_at": "2024-05-15", "direction": "short"}
      ],
      "interpretation": "3 天内 BTC 方向反转, 可能是短期 swing 调整"
    }
  ]
}
```

## 阶段三输出格式

整体在会话内存中构造一个聚合 JSON：

```json
{
  "dimensions": {
    "trading_targets_and_direction": { ... },
    "signal_trigger_patterns": { ... },
    "risk_management_style": { ... },
    "sentiment_and_implicit_stance": { ... },
    "trading_strategy_type": { ... }
  },
  "time_series": { ... },
  "contradictions": [ ... ],
  "topic_clusters": (引用阶段二输出),
  "meta": {
    "total_tweets": 856,
    "non_noise_tweets": 612,
    "noise_share": 0.285,
    "date_range": {"start": "2023-01-15", "end": "2026-05-14"},
    "analysis_date": "2026-05-17"
  }
}
```

## 自检清单

- [ ] 5 个维度都有 verdict + confidence
- [ ] 每个 verdict 配 5-10 个 evidence_tweet_ids
- [ ] 置信度遵循样本量公式
- [ ] 没有把 "占比 32%" 写成 "经常" 这种模糊表达
- [ ] contradictions 至少扫了 direction_reversal

## 用户反馈

阶段三完成后向用户报一行：

```
阶段 3 完成: 5 个维度聚合完毕
- 品种偏好: BTC 多头 (置信度 0.85)
- 信号模式: 追势 breakout 主导 (0.80)
- 风险风格: 中杠杆 + 高纪律 (0.75)
- 情绪立场: 偏多 + 波动中等 (0.85)
- 策略类型: 技术派波段 (0.80)
正在生成最终报告...
```
