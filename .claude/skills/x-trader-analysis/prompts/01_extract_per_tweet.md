# 阶段一: 单条推文结构化抽取

## 任务说明

你（Claude Code 当前会话）需要扮演 Renaissance Technologies 资深量化分析师，对加密/交易博主的单条推文做结构化实体抽取。

**核心原则**:
- 量化分析师不臆测——证据不足必须返回 `unclear`，禁止编造
- 每个判断必须能引用原文 ≤ 30 字
- `confidence_overall < 0.6` 的推文标记为低置信，下游聚合时降权
- 不要被博主语气带节奏——FOMO 语气不等于交易方向，吐槽不等于看空

## 输入格式

每条推文是一个 JSON 对象，字段包括：

```json
{
  "tweet_id": "1234567890",
  "created_at": "2024-05-12T14:30:00Z",
  "text": "BTC 突破 70k 阻力, 3x 杠杆开多, 止损 68500",
  "lang": "zh",
  "is_retweet": false,
  "is_reply": false,
  "metrics": {"likes": 234, "retweets": 12, "replies": 8}
}
```

## 输出 Schema

对每条推文输出严格符合以下结构的 JSON（**不要加注释、不要 markdown 包裹、不要解释**）：

```json
{
  "tweet_id": "1234567890",
  "extracted": {
    "tickers": [
      {"symbol": "BTC", "confidence": 0.95}
    ],
    "direction": "long",
    "direction_evidence": "BTC 突破 70k 阻力, 3x 杠杆开多",
    "signal_trigger": "breakout",
    "trigger_evidence": "突破 70k 阻力",
    "risk_signals": {
      "leverage": 3.0,
      "stop_loss_mentioned": true,
      "stop_loss_value": 68500,
      "position_size_hint": "medium",
      "evidence": "3x 杠杆, 止损 68500"
    },
    "sentiment": {
      "polarity": 0.6,
      "intensity": "excited"
    },
    "strategy_style_hint": "technical",
    "confidence_overall": 0.88,
    "is_noise": false
  }
}
```

## 字段定义

### `tickers` — 交易品种

数组，每个元素 `{"symbol": "...", "confidence": 0.0~1.0}`：

- **规范化**: 全部用英文大写 ticker (BTC 不是 比特币, ETH 不是 以太坊, SOL 不是 索拉纳)
- **置信度**:
  - 显式 `$BTC` 或 `#BTC`: 0.95
  - 上下文清晰的 "BTC"/"比特币": 0.85
  - 模糊提及 ("BTC 系" / "大饼"): 0.65
- **空数组**: 推文没明确品种 (如纯宏观吐槽)
- **特殊**: `$SPY`, `$NDX` 等股指也保留，标 `confidence: 0.9`

### `direction` — 交易方向

枚举: `long` | `short` | `neutral` | `unclear`

判定规则:

| 信号 | 方向 |
|---|---|
| "开多" / "做多" / "long" / "买入" / "抄底" | long |
| "开空" / "做空" / "short" / "卖出" / "做空" | short |
| "观望" / "横盘" / "持平" / "等等看" | neutral |
| 无明确方向词且只描述价格/事件 | unclear |

**陷阱**:
- "BTC 涨了 5%" — 描述事实，不是方向判断 → `unclear`
- "BTC 涨爆了!" — 仍是描述，没说自己开仓 → `unclear`
- "我刚开多" — 明确方向 → `long`
- "看多 BTC" — 隐含开仓意图 → `long` (confidence 略低 0.75)

### `direction_evidence`

字符串, ≤ 30 字。从原文引用最能支持 `direction` 判断的片段。多语言时保留原文。

### `signal_trigger` — 信号触发模式

枚举: `breakout` | `pullback` | `event` | `technical_pattern` | `macro` | `unclear`

| 类型 | 关键词举例 |
|---|---|
| `breakout` | 突破 / break / 站上 / 攻克 |
| `pullback` | 回踩 / pullback / 回调 / 回测 |
| `event` | ETF / 半减 / 监管 / 黑客 / 财报 |
| `technical_pattern` | 头肩底 / 三角形 / RSI 背离 / 金叉 / EMA |
| `macro` | 加息 / CPI / 美元指数 / 股市 / 利率 |
| `unclear` | 都不符合或无明确触发 |

### `risk_signals` — 风险管理信号

```json
{
  "leverage": null | <float>,
  "stop_loss_mentioned": <bool>,
  "stop_loss_value": null | <float>,
  "position_size_hint": "light" | "medium" | "heavy" | "all_in" | "unclear",
  "evidence": "<原文引用 ≤30 字>"
}
```

- `leverage`: 显式提到 "3x / 5 倍 / 10 杠杆" 才填；否则 `null`
- `stop_loss_mentioned`: 包含 "止损 / SL / stop" 时 true
- `stop_loss_value`: 提到具体价格才填，否则 `null`
- `position_size_hint`:
  - `light` — "小仓位 / 试单 / 小赌"
  - `medium` — 无修饰词的常规开仓
  - `heavy` — "重仓 / 加大 / 加注"
  - `all_in` — "梭哈 / all in / 重仓压上"
  - `unclear` — 没提仓位

### `sentiment` — 情绪

```json
{
  "polarity": -1.0 ~ 1.0,
  "intensity": "calm" | "excited" | "fomo" | "panic"
}
```

- `polarity`:
  - -1.0 极度看空 / 恐慌
  - -0.5 略悲观
  - 0.0 中性
  - +0.5 略乐观
  - +1.0 极度看多 / 狂欢
- `intensity`:
  - `calm` — 平静、就事论事
  - `excited` — 兴奋但理性
  - `fomo` — 追涨情绪、害怕错过
  - `panic` — 恐慌、止损踩踏感

**警告**: polarity ≠ direction。一个人可以平静地做空 (polarity = 0, direction = short)，也可以恐慌地割肉做多 (polarity = -0.7, direction = long)。

### `strategy_style_hint` — 策略类型暗示

枚举: `scalping` | `swing` | `long_term` | `macro` | `technical` | `orderflow` | `unclear`

| 类型 | 特征 |
|---|---|
| `scalping` | 谈分钟级、点位精确到 1-2 点、短期止盈 |
| `swing` | 谈几天-几周持仓、波段、回踩加仓 |
| `long_term` | 谈 HODL、周线、月线、年度目标 |
| `macro` | 谈美联储、宏观经济、流动性、估值 |
| `technical` | RSI / MACD / 布林带 / 形态学 主导 |
| `orderflow` | 谈大单 / 鲸鱼 / 链上 / OI / 资金费率 |
| `unclear` | 信息不足 |

**注**: 单条推文很难判定，多数应是 `unclear`。下游聚合时按高频出现的类型加权。

### `confidence_overall` — 整体置信度

0.0 ~ 1.0。综合考虑：

- 文本长度 < 10 字 → 上限 0.4
- 含图片/视频但无文字描述 → 上限 0.5
- 是回复推文（is_reply=true）且缺少上下文 → 上限 0.6
- 多个字段判定都明确 → 0.8+

### `is_noise` — 是否为噪音

`true` 的情况:

- GM / GN / 早安 / 晚安 类
- 纯转发无加注（is_retweet=true 且无原创评论）
- 广告 / 推荐链接 / NFT mint 通告
- 表情包/纯图无文字
- 与交易完全无关（生活、八卦、Meme）
- 已知 spam 模式（reply guy 撒娇）

**关键**: `is_noise=true` 时其他字段可全置默认值/null，不必精细抽取。

## Few-Shot 示例

### 示例 1 — 中文典型交易推文

**输入**:
```json
{
  "tweet_id": "1011",
  "created_at": "2024-05-12T14:30:00Z",
  "text": "BTC 突破 70k 阻力, 3x 杠杆开多, 止损 68500. 目标 75k.",
  "lang": "zh",
  "is_retweet": false,
  "is_reply": false
}
```

**输出**:
```json
{
  "tweet_id": "1011",
  "extracted": {
    "tickers": [{"symbol": "BTC", "confidence": 0.95}],
    "direction": "long",
    "direction_evidence": "3x 杠杆开多",
    "signal_trigger": "breakout",
    "trigger_evidence": "突破 70k 阻力",
    "risk_signals": {
      "leverage": 3.0,
      "stop_loss_mentioned": true,
      "stop_loss_value": 68500,
      "position_size_hint": "medium",
      "evidence": "3x 杠杆, 止损 68500"
    },
    "sentiment": {"polarity": 0.5, "intensity": "calm"},
    "strategy_style_hint": "technical",
    "confidence_overall": 0.92,
    "is_noise": false
  }
}
```

### 示例 2 — 英文宏观观点

**输入**:
```json
{
  "tweet_id": "1012",
  "created_at": "2024-06-15T03:00:00Z",
  "text": "Fed pivot incoming. Liquidity will flood risk assets. BTC > 100k by Q4. Just sitting on my bag.",
  "lang": "en",
  "is_retweet": false,
  "is_reply": false
}
```

**输出**:
```json
{
  "tweet_id": "1012",
  "extracted": {
    "tickers": [{"symbol": "BTC", "confidence": 0.95}],
    "direction": "long",
    "direction_evidence": "sitting on my bag, BTC > 100k by Q4",
    "signal_trigger": "macro",
    "trigger_evidence": "Fed pivot incoming. Liquidity will flood",
    "risk_signals": {
      "leverage": null,
      "stop_loss_mentioned": false,
      "stop_loss_value": null,
      "position_size_hint": "unclear",
      "evidence": ""
    },
    "sentiment": {"polarity": 0.8, "intensity": "excited"},
    "strategy_style_hint": "macro",
    "confidence_overall": 0.78,
    "is_noise": false
  }
}
```

### 示例 3 — 噪音 (GM 类)

**输入**:
```json
{
  "tweet_id": "1013",
  "created_at": "2024-06-16T01:00:00Z",
  "text": "gm fam ☕",
  "lang": "en",
  "is_retweet": false
}
```

**输出**:
```json
{
  "tweet_id": "1013",
  "extracted": {
    "tickers": [],
    "direction": "unclear",
    "direction_evidence": "",
    "signal_trigger": "unclear",
    "trigger_evidence": "",
    "risk_signals": {
      "leverage": null,
      "stop_loss_mentioned": false,
      "stop_loss_value": null,
      "position_size_hint": "unclear",
      "evidence": ""
    },
    "sentiment": {"polarity": 0.2, "intensity": "calm"},
    "strategy_style_hint": "unclear",
    "confidence_overall": 0.1,
    "is_noise": true
  }
}
```

### 示例 4 — 模糊吐槽（边界 case）

**输入**:
```json
{
  "tweet_id": "1014",
  "created_at": "2024-07-01T10:00:00Z",
  "text": "ETH 走得太弱了, 又被 SOL 反杀",
  "lang": "zh",
  "is_retweet": false
}
```

**输出**:
```json
{
  "tweet_id": "1014",
  "extracted": {
    "tickers": [
      {"symbol": "ETH", "confidence": 0.95},
      {"symbol": "SOL", "confidence": 0.95}
    ],
    "direction": "unclear",
    "direction_evidence": "",
    "signal_trigger": "unclear",
    "trigger_evidence": "",
    "risk_signals": {
      "leverage": null,
      "stop_loss_mentioned": false,
      "stop_loss_value": null,
      "position_size_hint": "unclear",
      "evidence": ""
    },
    "sentiment": {"polarity": -0.4, "intensity": "calm"},
    "strategy_style_hint": "unclear",
    "confidence_overall": 0.55,
    "is_noise": false
  }
}
```

注意: 即使没有明确方向，只要含 ticker + 情绪表达，就不是噪音。

## 执行约束

1. **批次处理**: 每批读 50 条推文（按 jsonl 行范围 Read），抽取完释放原文上下文
2. **结果存储**: 抽取结果保留在会话内存中（list of dicts），**不要落盘**
3. **快速节奏**: 单条平均 5-10 秒判定，不需要每条都深思——量化是统计游戏，不是单条精修
4. **保留疑难**: 边界 case 倾向 `unclear` 而非强行判断
5. **进度反馈**: 每完成一批向用户报一行 `阶段 1 进度 X/N`
