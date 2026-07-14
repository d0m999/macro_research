# 美股与宏观 KOL 方法论蒸馏计划

Created: 2026-06-15
Status: Draft v0
Merged: 2026-06-16, absorbed and removed the former repo copy of the gstack
`/plan-ceo-review` artifact at
`docs/gstack/2026-06-16-us-macro-kol-methodology-evidence-loop-ceo-plan.md`.

Canonical repo document: this file. `docs/gstack/` is only the lightweight
gstack process index; do not keep a second long-form copy of this plan there.

目标：从美股与宏观 KOL 的公开内容中，筛出真正有研究价值的人，抽取可验证的观点记录，回溯其数据源与推理链，最后沉淀成一个可在研究时调用的投资方法论 skill。

边界：这是研究工作流设计，不是投资建议；所有结论必须保留来源、时间戳、适用场景、失效条件和数据滞后说明。

GStack 续跑状态：

- 原始本地 artifact: `~/.gstack/projects/d0m999-ft_userdata/ceo-plans/2026-06-16-us-macro-kol-methodology-evidence-loop.md`
- repo 内权威计划: `docs/us-macro-kol-methodology-distillation.md`
- repo 内 gstack 索引: `docs/gstack/README.md`
- 已完成: `/plan-ceo-review`
- 下一步: `/plan-eng-review`，以本文档为计划输入，重点审架构、测试、错误路径、性能和实现任务。
- 续跑规则: 新的 gstack 流程可以继续写入 `~/.gstack/projects/d0m999-ft_userdata/`；如果需要放入 repo，只归档不重复的 review 输出，并同步更新本文档末尾的 `GSTACK REVIEW REPORT`。

---

## 0. 核心判断

当前没有一个三方服务能可靠覆盖 “X + YouTube + newsletter + podcast” 上所有美股/宏观 KOL 的真实胜率。成熟服务如 TipRanks 更适合覆盖卖方分析师、金融博客作者、研究机构、内部人、基金经理等显性荐股记录；X/YouTube 原生 KOL 仍需要自建抽取与回测。

因此建议采用两层筛选：

1. 用三方服务和公开指标做候选池降噪。
2. 自己从内容中抽取可证伪观点，并按统一规则回测。

不要只看粉丝、互动或单次爆款观点。真正要蒸馏的是：

- 他在什么市场 regime 下有效
- 他依赖哪些数据源
- 他如何从数据推出结论
- 他如何定义反证和失效
- 他在错误时如何调整
- 这些规则是否能被复用，而不只是复述观点

---

## 1. 总体流水线

```text
候选 KOL 池
  -> 身份归一化：X / YouTube / Substack / podcast / website
  -> 内容采集：posts / videos / transcripts / articles / charts
  -> AI 可读化：Markdown + JSON metadata + source URL + timestamp
  -> 观点抽取：只抽可证伪 prediction / thesis / catalyst / invalidation
  -> 结果解析：映射 ticker / macro proxy / horizon / benchmark
  -> 回测评分：胜率、超额收益、样本量、时效、透明度、回撤
  -> 方法论蒸馏：数据源 -> 指标解释 -> 推理路径 -> 交易/研究动作
  -> Skill 化：固定输入、检查清单、推理模板、输出格式、eval
```

建议先做 MVP：

- KOL 数：10-20 个候选，最后蒸馏 3-5 个。
- 内容范围：最近 12-24 个月，先覆盖 X 和 YouTube。
- 资产范围：美股单票、SPY/QQQ/IWM、TLT/IEF、DXY/UUP、GLD、USO、VIX/MOVE 等可交易 proxy。
- 观点样本：每人至少 30 条可证伪观点；低于 30 条只做定性，不做排名。
- 人工校验：抽取结果至少 20% 抽样复核，重点检查时间戳、方向、horizon 和是否未来函数。

---

## 2. KOL 筛选逻辑

### 2.1 候选池来源

候选池可以从这些地方起步：

| 来源 | 用途 | 局限 |
|---|---|---|
| TipRanks | 筛卖方分析师、金融博客、研究机构、基金经理等有结构化记录的人 | 覆盖不了大多数 X/YouTube 原生宏观 KOL |
| X Lists / follows graph | 找同圈层内被高质量账号引用的人 | 社交图不等于预测能力 |
| YouTube channel search + SocialBlade | 找持续输出宏观/美股内容的频道，评估更新频率和受众规模 | 只能看传播，不等于胜率 |
| Substack / newsletter / podcast榜单 | 找深度研究型作者 | 历史内容可能付费或难结构化 |
| 用户手动名单 | 最高质量入口 | 容易有个人偏好，需要后续回测纠偏 |

### 2.2 已确认的 KOL 胜率/价格映射工具

确认日期：2026-06-16。这里的“可访问”是按浏览器打开 + HTTP 状态综合判断；部分站点会拦截 `curl` 或需要登录/浏览器环境。

结论：加密方向已经有多款接近“X KOL post -> token/ticker -> 胜率/收益 -> K线或后续价格表现”的产品；美股方向目前更常见的是 YouTube finfluencer track record，尚未确认到成熟公开的“美股 X KOL post 映射 K线并统计胜率”产品。

| 名称 | 覆盖 | 贴近程度 | 已确认能力 | 访问状态 |
|---|---|---|---|---|
| [AiCoin KOL指标](https://www.aicoin.com/zh-Hans/article/381511) | 加密 | 很高 | 文档提到可筛高胜率 KOL，并点击具体时间点进入 K线回测发推内容 | 浏览器可打开；`curl` 被拦 |
| [Scopechat KOL Calls / KOL Leaderboard](https://docs.scopechat.ai/how-to-use/find-token) | 加密 | 很高 | 按 KOL posts 提到的 token，统计 Win Rate、post 后不同时间段价格变化、平均收益 | 文档 200 可访问 |
| [Thrive KOL Tracker](https://docs.thrive.fi/docs/market-intel-sentiment) | 加密 | 很高 | NLP 从 KOL posts 抽取 token/direction，跟踪 24h/7d/30d 表现，给 accuracy、avg return、hit rate | 200 可访问 |
| [FlashX KOL Performance Metrics](https://docs.flashx.ai/kol-performance-metrics) | 加密 | 高 | Chrome extension 中基于 Twitter signal 统计 Average ROI、Win Rate | 200 可访问 |
| [BitMart X Insight](https://www.bitmart.com/ai/xinsight/landing) / [User Guide](https://bitmart.zendesk.com/hc/en-us/articles/38066376411931-X-Insight-User-Guide) | 加密 | 中 | 跟踪 crypto KOL tweets，做 sentiment、KOL consensus、SSI vs price；未确认有 KOL 胜率/K线回测 | 浏览器可打开；部分页面 `curl` 403 |
| [XHunt](https://kol.xhunt.ai/) / [Chrome 插件](https://chromewebstore.google.com/detail/xhunt-%E2%80%93-your-ai-co-pilot/gonmfafjcdkngkbhcpmcphlgfhabkeji) | 加密 | 中 | 定位为 X 上的 KOLFi / tweets-to-trades，追踪 KOL crypto mentions 和 KOL metrics | 站点/插件页 200 可访问 |
| [AlphaCheck](https://alphacheck.ai/) | 美股，YouTube | 中 | 抽取视频里的股票提及，显示提及时价格和当前价格，支持 channel track record | 200 可访问 |
| [FinTuber](https://www.fintuber.io/) | 美股，YouTube | 中 | 分析 YouTube finance creators 的 stock picks，和 S&P 500 对比，显示 win rate | 200 可访问 |
| [Social Stock](https://socialstock.app/) | 美股，X/Reddit/YouTube | 低到中 | 聚合社媒股票讨论和 high conviction posts；未确认有 KOL 胜率/K线回测 | 200 可访问 |
| [Frontrun](https://www.frontrun.pro/) / [Chrome 插件](https://chromewebstore.google.com/detail/frontrun/kifcalgkjaphbpbcgokommchjiimejah) | 加密 | 辅助 | 更偏 tweets-to-trades、加密 KOL/交易信号，不是完整 post-to-Kline 胜率库 | 200 可访问 |
| [Kolscan](https://kolscan.io/) | 加密 | 辅助 | 更偏 KOL/钱包表现、PnL、排行榜，不是完整 post-to-Kline 胜率库 | 200 可访问 |

使用建议：

- 加密 KOL 初筛可以优先看 AiCoin、Scopechat、Thrive、FlashX，直接获得已有的 post 后表现和 KOL track record。
- 美股 KOL 如果来源是 YouTube，可以先用 AlphaCheck、FinTuber 做候选降噪。
- 美股 X KOL 仍建议自建抽取与回测 pipeline：现成产品暂时只能作为候选池补充，不能替代自己的 prediction schema 和回测规则。
- 对任何三方胜率都要二次审计：确认是否按首次提及计数、是否合并重复 post、是否包含删除内容、是否使用固定 horizon、是否以当前可交易价格还是 post 时间价格计算。

### 2.3 初筛标准

候选进入采集前，先用以下标准打分：

| 维度 | 问题 | 推荐权重 |
|---|---|---:|
| 可证伪性 | 是否经常给明确方向、horizon、催化剂或失效条件 | 25% |
| 研究透明度 | 是否展示数据源、图表、模型、原始链接 | 20% |
| 领域专长 | 是否长期聚焦少数资产/主题，而不是到处追热点 | 15% |
| 历史样本量 | 过去 12-24 个月可抽取观点是否足够 | 15% |
| 前瞻性 | 是在事件前提出判断，还是事后解释价格 | 15% |
| 噪音控制 | 是否频繁删帖、转向、标题党、无明确结论 | 10% |

建议分级：

- A：可进入完整回测和方法论蒸馏。
- B：可持续跟踪，但先不 skill 化。
- C：只做背景观点，不作为方法来源。
- D：娱乐/情绪/流量账号，剔除。

### 2.4 胜率以外的评分

赔率无法稳定获取时，不要只用胜率。高胜率可能来自说模糊话、短 horizon 追趋势、只挑 easy call。应采用组合指标：

| 指标 | 解释 |
|---|---|
| Clarity Rate | 内容中有多少比例能抽成可证伪观点 |
| Hit Rate | 方向判断在固定 horizon 内是否正确 |
| Alpha Hit Rate | 相对 benchmark/sector/proxy 是否跑赢 |
| Median Forward Return | 命中/未命中之外，看收益分布中位数 |
| Max Adverse Excursion | 判断后先反向走多远，衡量 timing |
| Information Coefficient | 观点强度/置信度与后续收益的相关性 |
| Calibration | 若 KOL 给概率/置信度，检验 60% 观点是否约 60% 命中 |
| Sample Size | 样本量太小直接降权 |
| Regime Robustness | 是否只在单一市场环境有效 |
| Source Transparency | 数据源和推理链是否可复现 |
| Revision Quality | 错了以后是否有明确复盘和更新 |

评分公式初版：

```text
KOLScore =
  0.30 * TrackRecord
  + 0.20 * Falsifiability
  + 0.15 * ProcessTransparency
  + 0.15 * SpecialtyFit
  + 0.10 * TimingQuality
  + 0.10 * RevisionQuality
```

强制降权规则：

- 样本量 < 30：不做量化排名。
- 明确观点中超过 50% 无 horizon：最多 B。
- 大量观点无法确定发布时间或原文已删除：最多 B。
- 只给方向、不提风险或失效条件：ProcessTransparency 降权。
- 观点高度跟随当日价格动作：TimingQuality 降权。

---

## 3. 内容采集与 Markdown 化

### 3.1 原始数据结构

所有平台统一成 `source_item`：

```yaml
id: x_1234567890
kol_id: sample_kol
platform: x
url: https://x.com/...
published_at: 2026-05-01T14:32:00Z
collected_at: 2026-06-15T12:00:00Z
content_type: post
language: en
raw_path: data/raw/x/sample_kol/2026/05/x_1234567890.json
markdown_path: data/markdown/sample_kol/2026-05-01_x_1234567890.md
media_paths:
  - data/raw/x/sample_kol/2026/05/x_1234567890_image_1.png
engagement:
  likes: 1200
  reposts: 220
  replies: 90
license_or_access: public
```

### 3.2 平台采集建议

| 平台 | 首选 | 备选 | 备注 |
|---|---|---|---|
| X | X API v2 recent/full-archive search | twscrape 等开源工具 | 官方 recent search 只覆盖近 7 天；full-archive 需要 pay-per-use/Enterprise。非官方工具要单独评估 ToS、账号风控和稳定性 |
| YouTube | YouTube Data API + captions API | yt-dlp / youtube-transcript-api | 官方 captions API 能列出和下载 caption track；开源方案适合公开字幕和批处理 |
| Website / blog | Firecrawl / Crawl4AI / Jina Reader | Playwright + readability | 目标是输出干净 Markdown，不要保存广告和导航噪音 |
| PDF / slides | Docling / MarkItDown | OCR + 手工校验 | 保留页码、图表标题、原始链接 |
| Newsletter | 官方导出/API/邮箱规则 | 手工保存 HTML/PDF | 注意付费内容版权，不把全文随意扩散 |

### 3.3 Markdown 输出格式

每条内容转成独立 Markdown：

```markdown
---
kol_id: sample_kol
platform: youtube
source_url: https://www.youtube.com/watch?v=...
published_at: 2026-05-01T14:32:00Z
collected_at: 2026-06-15T12:00:00Z
content_type: transcript
title: "..."
language: en
duration_seconds: 1842
---

# Title

## Metadata

- KOL: sample_kol
- Platform: youtube
- URL: https://www.youtube.com/watch?v=...
- Published: 2026-05-01T14:32:00Z

## Transcript

...

## Media Notes

- Chart at 00:13:22: 10Y yield vs Nasdaq relative performance
```

要求：

- Markdown 必须保留 `source_url` 和 `published_at`。
- YouTube transcript 保留时间戳区间，便于回看。
- 图片和图表不只存图，要生成 `media_notes`，描述坐标轴、指标和结论。
- AI 生成的摘要必须与原文分开，不能覆盖原文。

---

## 4. 可证伪观点抽取

### 4.1 只抽这些类型

| 类型 | 示例 | 是否进入回测 |
|---|---|---|
| Directional Call | “NVDA 未来 3 个月跑赢 QQQ” | 是 |
| Macro Regime Call | “实际利率下行阶段，长久期科技股占优” | 是，映射 proxy |
| Catalyst Call | “CPI 后 yields 会下行” | 是，事件窗口 |
| Thesis / Narrative | “AI capex cycle 未结束” | 进入方法论，若能映射 proxy 再回测 |
| Invalidation | “若 10Y 收上 5%，long duration thesis 失效” | 进入方法论 |
| Data Interpretation | “RRP 降至低位意味着流动性缓冲变弱” | 进入数据源/推理链 |
| 纯情绪/段子/新闻转发 | “市场疯了” | 不进入 |

### 4.2 Prediction schema

```yaml
prediction_id: sample_kol_20260501_001
kol_id: sample_kol
source_item_id: x_1234567890
source_url: https://x.com/...
published_at: 2026-05-01T14:32:00Z

claim_text: "..."
claim_type: directional_call
asset_type: equity
tickers: [NVDA]
proxy: null
direction: long
benchmark: QQQ
horizon:
  type: explicit
  start: 2026-05-01
  end: 2026-08-01
confidence:
  value: null
  source: not_provided
catalyst:
  - earnings
  - AI capex
invalidation:
  - "..."
data_sources_mentioned:
  - "earnings call"
  - "hyperscaler capex"
extractor_confidence: 0.82
needs_human_review: false
```

### 4.3 抽取 prompt 初版

```text
You are extracting falsifiable investment claims from one source item.

Rules:
- Extract only claims made before the outcome is known.
- Do not infer a trade if the speaker only reports news.
- Preserve the original timestamp and source URL.
- If horizon is absent, infer a conservative default only when the claim has clear event timing; otherwise set horizon.type = "missing".
- Map macro claims to a tradable proxy only when the mapping is standard and explain the mapping.
- Return JSON only.

Output fields:
prediction_id, claim_text, claim_type, asset_type, tickers, proxy,
direction, benchmark, horizon, confidence, catalyst, invalidation,
data_sources_mentioned, extractor_confidence, needs_human_review, notes.
```

### 4.4 人工复核优先级

优先复核：

- 高影响观点：视频标题、置顶 post、长 thread、newsletter headline。
- 模糊方向：bullish/bearish 但没有明确资产。
- 模糊 horizon：soon、next leg、into earnings、cycle turn。
- 宏观 proxy：例如 “liquidity up” 到底映射 QQQ、SPY、BTC 还是 gold。
- 事件后内容：防止把事后解释当成预测。

---

## 5. 回测与 KOL 胜率

### 5.1 结果解析规则

固定 horizon：

| 原文 horizon | 解析 |
|---|---|
| intraday | 发布后到当日收盘 |
| next few days | 5 个交易日 |
| next week | 5 个交易日 |
| next month | 21 个交易日 |
| quarter / earnings cycle | 到下次财报或 63 个交易日 |
| 3-6 months | 63 和 126 两个窗口都算 |
| missing | 不进入主胜率，只进入定性方法论 |

方向判断：

```text
long success = asset_forward_return - benchmark_forward_return > threshold
short success = asset_forward_return - benchmark_forward_return < -threshold
macro rate-up success = mapped_yield_change > threshold
macro dollar-up success = DXY/UUP forward_return > threshold
```

建议阈值：

- 单票 vs sector/QQQ/SPY：超额收益 > 1% 才算成功，避免噪音。
- ETF/指数方向：绝对收益 > 0.5% 或 z-score > 0.25。
- 利率/宏观数据：用 bp 变化或 surprise z-score。

### 5.2 Benchmark 映射

| Claim | Asset | Benchmark |
|---|---|---|
| Mega-cap tech long | AAPL/MSFT/NVDA/AMZN/GOOGL/META/TSLA | QQQ 或 XLK/sector ETF |
| Broad US equity | SPY/ES | cash 或 T-bill proxy |
| Small caps | IWM/RTY | SPY |
| Long duration bonds | TLT/IEF/ZB | cash 或 IEF/TLT 对应 |
| USD bullish | DXY/UUP | cash |
| Gold bullish | GLD/GC | real yield 变化作为辅助 |
| Oil bullish | USO/CL | broad commodity proxy |
| Volatility | VIX/VXX/options proxy | SPY realized vol |

### 5.3 统计输出

每个 KOL 输出：

```yaml
kol_id: sample_kol
period: 2024-06-01_to_2026-06-01
sample_count_total: 182
sample_count_falsifiable: 74
clarity_rate: 0.41
hit_rate_5d: 0.54
hit_rate_21d: 0.58
alpha_hit_rate_21d: 0.51
median_alpha_21d: 0.8%
max_adverse_excursion_median: -2.4%
regime_notes:
  strongest: "AI capex / liquidity easing"
  weakest: "rates shock / CPI surprise"
data_source_transparency_score: 0.72
revision_quality_score: 0.60
overall_grade: B+
```

### 5.4 防偏差规则

- 禁止未来函数：只允许使用 `published_at` 当时已公布的数据。
- 同一观点重复发帖：合并为一个 `prediction_cluster`，不重复计数。
- 截图型观点：需要 OCR/人工确认图表日期，避免图表本身已经包含未来数据。
- 删除内容：标记 `deleted_or_unavailable`，不直接剔除，否则会高估。
- 追涨型观点：记录发布前 1/5/21 日资产已涨跌幅，作为 momentum exposure。
- 大盘 beta：单票观点必须同时看绝对收益和相对 benchmark。
- 样本量和置信区间必须展示，不只展示单一胜率。

---

## 6. 方法论蒸馏

### 6.1 三遍蒸馏法

第一遍：事实抽取。

- KOL 提到过哪些数据源？
- 什么时候看这些数据？
- 用哪些阈值、变化率、相对强弱、背离？
- 哪些观点有明确失败/修正？

第二遍：模式聚类。

- 将观点按 `asset_class`、`regime`、`data_source`、`horizon` 聚类。
- 找出“重复出现且命中率较高”的推理模式。
- 找出“重复出现但失败”的反模式。

第三遍：反证压力测试。

- 选择其最成功的 5-10 个观点和最失败的 5-10 个观点。
- 比较成功/失败时数据源是否不同、regime 是否不同、是否忽略了关键变量。
- 只把能解释成功和失败边界的方法写进 skill。

### 6.2 蒸馏对象不是观点，而是推理函数

错误格式：

```text
KOL A 看多 AI，所以我们看多 AI。
```

正确格式：

```text
当 hyperscaler capex guidance 上修、AI revenue run-rate 加速、供应链交付仍紧、且长端利率未重新上行时，
KOL A 倾向把 mega-cap AI infrastructure 叙事视为未结束。
若 capex 上修但 FCF guide 下修、RPO/booking 没有同步改善，叙事从“供不应求”切换成“capex trap”。
```

### 6.3 方法论卡片模板

```markdown
# Method Card: <name>

## Applies To

- Asset: US mega-cap tech / macro rates / USD / gold / oil
- Horizon: 1-12 weeks
- Best regime: ...
- Weak regime: ...

## Data Inputs

| Data | Source | Frequency | Lag | Required |
|---|---|---|---|---|
| 10Y yield | FRED / market data | daily | EOD | yes |

## Reasoning Path

1. Observe ...
2. Compare ...
3. Infer ...
4. Check contradiction ...
5. Decide research stance ...

## Signal

- Bullish if ...
- Bearish if ...
- Neutral if ...

## Invalidation

- ...

## Known Failure Modes

- ...

## Evidence

- KOL source ids:
  - sample_kol_20260501_001
```

### 6.4 方法论蒸馏 prompt 初版

```text
You are distilling a KOL's investment methodology from extracted evidence.

Inputs:
- Source items with timestamps and URLs
- Extracted predictions with outcomes
- Mentioned data sources
- Success and failure clusters

Task:
1. Identify recurring decision rules.
2. Separate explicit statements from inferred rules.
3. Map each rule to data inputs, horizon, asset class, and regime.
4. List counterexamples and failure modes.
5. Output reusable method cards.

Constraints:
- Do not copy the KOL's current market calls.
- Do not include a rule unless at least 3 evidence items support it, or mark it as "low confidence".
- Every rule must include invalidation or known failure modes.
```

---

## 7. 数据源总结

### 7.1 数据源识别层级

| 层级 | 含义 | 例子 |
|---|---|---|
| Explicit | KOL 直接说出或链接 | FRED series、BLS CPI、SEC 10-Q、Fed speech |
| Visual | 图表截图中可见 | Bloomberg chart、TradingView、Koyfin、Yardeni chart |
| Inferred | 根据术语或字段推断 | RRP/TGA/reserves 可能来自 FRED/NY Fed/Treasury |
| Unknown | 无法确定 | 只说 “my model says” |

每个数据源需要记录：

```yaml
source_name: FRED
source_type: macro_database
official_url: https://fred.stlouisfed.org/
access: free_api_key
frequency: daily/monthly/quarterly
lag: varies
used_by_kols:
  - sample_kol
fields:
  - DGS10
  - WALCL
  - RRPONTSYD
confidence: explicit
notes: "Need point-in-time availability where possible."
```

### 7.2 美股与宏观常见数据源清单

| 类别 | 数据源 | 用途 |
|---|---|---|
| 股价/ETF/OHLCV | OpenBB, yfinance, Polygon, Tiingo, Nasdaq Data Link | 回测价格、benchmark、forward return |
| 公司文件 | SEC EDGAR APIs | 10-K/10-Q/8-K、company facts、filing metadata |
| 财报与电话会 | 公司 IR、SEC 8-K、Aiera/FactSet/Capital IQ 等商业源 | 管理层表述、guidance、segment trend |
| 宏观 | FRED、BLS、BEA、Treasury、NY Fed | CPI、jobs、GDP、rates、liquidity、TGA/RRP |
| 定位 | CFTC COT | futures positioning、leveraged funds、asset managers |
| 利率/流动性 | FRED、Treasury、Fed H.4.1、SOFR、MOVE | real yield、curve、reserves、liquidity regime |
| 期权/波动率 | CBOE、OptionMetrics/ORATS/Polygon 等 | VIX、skew、gamma/flow proxy |
| 情绪/社媒 | X、Stocktwits、Reddit、YouTube comments | 情绪和拥挤度，不能单独作为 thesis |
| 新闻/事件 | company IR、Fed calendar、economic calendar、news APIs | catalyst 和事件窗口 |

---

## 8. 数据源到推理路径

### 8.1 标准推理链

```text
Data Source
  -> Feature
  -> Interpretation
  -> Regime / Thesis
  -> Asset Proxy
  -> Horizon
  -> Invalidation
  -> Research Action
```

### 8.2 示例：流动性/长久期科技

```text
FRED / NY Fed / Treasury data
  -> bank reserves, RRP, TGA, 10Y real yield, DXY
  -> liquidity impulse improving + real yield falling
  -> financial conditions easing
  -> QQQ / high-duration equities outperform SPY
  -> 1-8 week horizon
  -> invalidated if 10Y real yield breaks higher, DXY rallies, CPI surprises up
  -> research action: overweight duration-sensitive growth, check crowdedness
```

### 8.3 示例：财报叙事

```text
SEC filing / earnings transcript / company IR
  -> revenue growth, guide, backlog/RPO, capex, margin, FCF
  -> growth acceleration with durable demand and acceptable margin tradeoff
  -> narrative strengthening
  -> ticker vs sector ETF / QQQ
  -> earnings cycle horizon
  -> invalidated if guide beat is driven by pull-forward, backlog decelerates, or capex destroys FCF without demand proof
  -> research action: update thesis and catalyst watchlist
```

### 8.4 示例：定位与反身性

```text
CFTC COT / options data / price trend
  -> leveraged funds crowded short, put/call elevated, price holds support
  -> asymmetric squeeze risk
  -> tactical long or avoid adding short
  -> futures/ETF proxy
  -> days to weeks
  -> invalidated if price loses support with vol expanding
  -> research action: mark as timing/sentiment signal, not standalone fundamental thesis
```

### 8.5 示例：宏观数据 surprise

```text
BLS / BEA / ISM / FOMC
  -> actual vs consensus, revision, diffusion, wage/inflation component
  -> growth/inflation mix changes
  -> rates path and equity multiple pressure changes
  -> TLT/IEF, SPY/QQQ, DXY, GLD
  -> event window to 2 weeks
  -> invalidated by next major data print or Fed communication
  -> research action: update macro regime table before making single-name conclusions
```

---

## 9. 最终 Investment Methodology Skill 形态

目标目录建议：

```text
skills/local/us-macro-kol-methodology/
  SKILL.md
  references/
    data-sources.md
    methodology-cards.md
    kol-scorecards/
      sample-kol.md
    reasoning-templates.md
    failure-modes.md
  evals/
    sample-ticker-analysis.md
    sample-macro-regime.md
```

### 9.1 `SKILL.md` 骨架

```markdown
---
name: us-macro-kol-methodology
description: Analyze US equities and macro regimes using distilled KOL-derived research methods with source-backed data checks, reasoning paths, invalidation, and failure modes.
---

# US Macro KOL Methodology

Use this skill when the user asks for:
- US equity thesis analysis
- macro regime diagnosis
- catalyst watchlist
- KOL-methodology-backed research
- data-source-to-thesis reasoning

Do not use this skill for:
- personalized financial advice
- guaranteed trade calls
- unsupported real-time data claims

## Required Workflow

1. Identify asset, horizon, and user intent.
2. Select relevant methodology cards.
3. Build the data checklist.
4. Pull or request current data.
5. Produce a reasoning trace:
   data -> interpretation -> thesis -> invalidation -> watchlist.
6. Explicitly separate:
   observed data, KOL-derived method, model inference, and uncertainty.

## Output

- Thesis
- Data checklist
- Reasoning path
- Invalidation
- Catalyst watchlist
- Confidence and uncertainty
- Sources used
```

### 9.2 Skill 输出格式

```markdown
# <Ticker or Macro Theme> Research Note

## 1. Setup

- Asset:
- Horizon:
- Relevant method cards:
- Data freshness:

## 2. Data Checklist

| Data | Latest value/date | Interpretation | Source |
|---|---|---|---|

## 3. Reasoning Path

1. ...

## 4. Thesis

- Base case:
- Bull case:
- Bear case:

## 5. Invalidation

- ...

## 6. Watchlist

- Next data/event:
- What would strengthen thesis:
- What would weaken thesis:

## 7. Limits

- Missing data:
- Regime risk:
- Method failure modes:
```

### 9.3 Skill eval

每次修改 skill 后，用固定案例回归：

| Eval | 输入 | 期望 |
|---|---|---|
| Ticker thesis | “用该方法分析 NVDA 未来 1-3 个月” | 不直接喊单；先列数据源、叙事、催化剂、失效条件 |
| Macro regime | “现在是否利好长久期科技？” | 检查 rates、real yield、DXY、liquidity、earnings breadth |
| Missing data | “分析一个没有当前数据的 ticker” | 明确说缺数据，不编数 |
| Contradiction | “价格创新高但基本面变差” | 输出冲突解释和观察清单 |
| KOL citation | “这个结论来自谁的方法？” | 只引用已蒸馏的方法卡，不冒充 KOL 当前观点 |

---

## 10. 项目落地目录

如果后续要把这个方案实现成可跑项目，建议单独放到 `research/kol-distillation/`。CEO review 后的 v0 目录以可验证 artifact 为中心，不再只保存 notebook 和 markdown 草稿：

```text
research/kol-distillation/
  README.md
  corpus.yaml
  contracts/
    single_ticker_contract.schema.json
  schemas/
    source_item.py
    capture_input.py
    prediction.py
    outcome.py
    method_card.py
    research_note.py
  scripts/
    convert_x_capture.py
    extract_predictions.py
    score_outcomes.py
    export_single_ticker_adapter.py
  candidates/
    kol-list.yaml
  data/
    capture_inputs/
    markdown/
    provenance/
      source_manifest.jsonl
    runs/
      llm_runs.jsonl
      pipeline_runs/
    extracted/
      predictions.jsonl
    review/
      prediction_reviews.jsonl
    outcomes/
      prediction_outcomes.jsonl
    market_snapshots/
    manual_overrides/
  fixtures/
    extraction_goldset/
    outcomes/
    adapters/
    adversarial/
  notebooks/
    01_candidate_screening.ipynb
    02_prediction_extraction_review.ipynb
    03_backtest_scorecards.ipynb
  prompts/
    extract_predictions.md
    distill_methodology.md
    map_data_sources.md
  outputs/
    scorecards/
    method_cards/
    research_notes/
    adapters/
      single_ticker/
    run_reports/
    skill_draft/
```

最小 schema / model：

```text
capture_input
source_item
provenance_manifest
llm_run
prediction
prediction_review
prediction_outcome
scorecard
method_card
research_note
single_ticker_adapter_export
pipeline_run
```

v0 规则：

- `capture_input` 是第一等 artifact，先记录 URL、手动文本、截图/OCR、browser export 和 rights baseline，再转换为 `source_item`。
- `source_item` 必须有 provenance manifest、`content_hash` 和 `storage_policy`。
- 所有 LLM 产物只存 `llm_run_id`，详细 prompt/model/hash/retry 元数据统一写入 `data/runs/llm_runs.jsonl`。
- 所有 scored predictions 必须先经过人工 review，并处于 `accepted` 或 `corrected` 终态。
- outcome scorer 先跑 fixtures；live data 只在 fixtures 通过后使用。
- adapter 只导出 JSON，不自动改写未来的 `tickers/{TICKER}/thesis.md`。

---

## 11. 推荐工具栈

| 环节 | 开源/服务 | 推荐用途 |
|---|---|---|
| 金融数据聚合 | OpenBB | 统一拉取多数据源，用于研究与 agent 接入 |
| 价格数据 | yfinance / OpenBB / Nasdaq Data Link / Alpha Vantage / Polygon | MVP 用免费/低价源，正式回测用更稳定源 |
| 回测 | vectorbt / backtrader | 批量 forward return、事件窗口、proxy 策略 |
| 绩效统计 | QuantStats / scipy / statsmodels | 胜率、收益分布、置信区间 |
| 已有 KOL 胜率/价格映射工具 | AiCoin / Scopechat / Thrive / FlashX / XHunt | 加密 KOL 候选降噪、post 后收益参考、第三方 track record 交叉验证 |
| 美股 finfluencer track record | AlphaCheck / FinTuber / Social Stock | 美股 YouTube / 社媒候选池降噪；目前不替代自建 X 回测 |
| X 数据 | X API v2；twscrape 作为需合规评估的备选 | timeline/search/author posts |
| YouTube 数据 | YouTube Data API / yt-dlp / youtube-transcript-api | metadata、字幕、transcript |
| Web 转 Markdown | Firecrawl / Crawl4AI / Jina Reader | blog、网页、长文 |
| 文档转 Markdown | MarkItDown / Docling | PDF、PPT、DOCX、HTML |
| 深度研究模式参考 | GPT Researcher / STORM | planner -> gather -> summarize -> cite -> report |
| LLM eval | OpenAI Evals / 自建 golden set | 验证抽取与 skill 输出是否稳定 |
| 存储 | DuckDB + Parquet + Markdown | 结构化查询 + git 友好文本 |

---

## 12. 合规与风险

- 优先使用官方 API、用户自己有权访问的数据、公开网页。
- 非官方采集工具只作为技术备选，必须单独评估平台 ToS、账号风险、速率限制和版权。
- 付费 newsletter、研报、数据库内容不得把全文复制到公开仓库。
- 保存必要摘录、metadata、URL、时间戳和自己的分析即可。
- KOL 方法论不能等同于 KOL 当前观点；skill 输出必须说明是“基于历史方法蒸馏的研究框架”。
- 不把 AI 抽取结果当真值；涉及评分和样本归因的记录必须可人工复核。

---

## 13. 待用户决策

1. 第一批 KOL 名单：手动给 10-20 个，还是先从 X/YouTube/TipRanks 自动生成候选池。
2. 数据预算：只用免费/低价源，还是接入付费价格、新闻、财报转录和期权数据。
3. 时间范围：12 个月、24 个月，还是覆盖完整周期。
4. 内容范围：先只做英文，还是中英混合。
5. 最终目标：只产出研究 skill，还是同时产出可运行的采集/回测 pipeline。

---

## 14. 资料来源

工具与数据源：

- OpenBB: https://github.com/OpenBB-finance/OpenBB
- vectorbt: https://github.com/polakowo/vectorbt
- backtrader: https://www.backtrader.com/
- QuantStats: https://github.com/ranaroussi/quantstats
- SEC EDGAR APIs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- FRED API: https://fred.stlouisfed.org/docs/api/fred/
- CFTC COT: https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm
- Nasdaq Data Link: https://docs.data.nasdaq.com/
- Alpha Vantage: https://www.alphavantage.co/documentation/
- X API Search Posts: https://docs.x.com/x-api/posts/search/introduction
- twscrape: https://github.com/vladkens/twscrape
- YouTube Data API captions: https://developers.google.com/youtube/v3/docs/captions
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- youtube-transcript-api: https://github.com/jdepoix/youtube-transcript-api
- Firecrawl: https://github.com/firecrawl/firecrawl
- Crawl4AI: https://github.com/unclecode/crawl4ai
- MarkItDown: https://github.com/microsoft/markitdown
- Docling: https://github.com/docling-project/docling
- GPT Researcher: https://github.com/assafelovic/gpt-researcher
- STORM: https://github.com/stanford-oval/storm
- OpenAI Evals: https://github.com/openai/evals

三方 KOL/传播参考：

- TipRanks Top Analysts: https://www.tipranks.com/experts/analysts
- SocialBlade: https://socialblade.com/
- AiCoin KOL指标: https://www.aicoin.com/zh-Hans/article/381511
- Scopechat KOL Calls / Leaderboard: https://docs.scopechat.ai/how-to-use/find-token
- Thrive KOL Tracker: https://docs.thrive.fi/docs/market-intel-sentiment
- FlashX KOL Performance Metrics: https://docs.flashx.ai/kol-performance-metrics
- BitMart X Insight: https://www.bitmart.com/ai/xinsight/landing
- XHunt: https://kol.xhunt.ai/
- XHunt Chrome Extension: https://chromewebstore.google.com/detail/xhunt-%E2%80%93-your-ai-co-pilot/gonmfafjcdkngkbhcpmcphlgfhabkeji
- AlphaCheck: https://alphacheck.ai/
- FinTuber: https://www.fintuber.io/
- Social Stock: https://socialstock.app/
- Frontrun: https://www.frontrun.pro/
- Kolscan: https://kolscan.io/

---

## 15. GStack CEO Review 合并记录

本节合并自 2026-06-16 的 `/plan-ceo-review`。它是本文档从“研究方法论草案”进入“可实现 v0 计划”的执行约束。前文保留问题背景、候选筛选、评分和方法论蒸馏思路；本节定义 v0 实现时必须满足的 artifact、状态、测试和 review gate。

### 15.1 v0 范围

选定路线：Closed-Loop v0 / Evidence Loop + Skill Harness。

```text
seeded source items
  -> source_item markdown + provenance manifest
  -> prediction extraction
  -> schema validation
  -> manual review state transitions
  -> outcome scoring with fixtures
  -> scorecard
  -> method_card
  -> ticker/theme research_note
  -> evals against expected behavior
  -> single-ticker research adapter export
```

v0 接受范围：

- 种子语料：2-3 个 KOL、1-2 个主题、30-60 个 source items、至少 20 条可证伪 predictions。
- 首批语料路线：`B3 Low-Cost X Seed Corpus`，用人工筛选的 X posts / threads、手动文本、截图 OCR、browser export 或 clipped HTML 作为输入。
- 数据默认：fixture first，然后 `yfinance` adjusted close、`pandas_market_calendars`、FRED snapshots、`manual_overrides`。
- 产物：source items、predictions、outcomes、scorecards、method cards、research notes、single-ticker adapter export。
- 必须有 validators、gold-set eval、rights/provenance manifest、deterministic outcome fixtures。

v0 不做：

- 全量 X / YouTube crawler 或连续平台采集。
- 公开 KOL 排行榜。
- 未授权的付费 newsletter / 研报全文 ingest。
- Dashboard / UI。
- 自动改写 `tickers/{TICKER}/thesis.md`。
- 自动法律分类。v0 只记录 rights metadata 和人工 notes。
- OpenBB-first provider abstraction。

### 15.2 核心术语

- `source_item`: 一个有来源 URL、发布时间、content hash、storage policy 和 provenance 的内容单元。
- `capture_input`: source conversion 前的输入记录，覆盖 URL、手动文本、截图/OCR、browser export、rights baseline。
- `prediction`: 从 source item 抽取的可证伪 claim，必须包含 asset/proxy、direction、horizon、benchmark、source span、confidence 和 review state。
- `outcome`: 单个 prediction 在固定窗口下的评分结果，包含 start/end、asset return、benchmark return、alpha、success、MAE、data source 和 unscored reason。
- `scorecard`: 对 KOL 或 method 的聚合评分，必须展示 sample count、hit/alpha hit rate、confidence、regime notes 和 caveats。
- `method_card`: 从证据中蒸馏出的可复用研究规则，包含适用资产/主题、输入数据、推理路径、signal、invalidation、failure modes 和 evidence IDs。
- `research_note`: 面向用户的 ticker/theme 输出，必须分开 observed data、method-derived interpretation、model inference、uncertainty、invalidation、watchlist 和 missing data。
- `macro proxy`: 宏观 claim 的可交易或可观测替代物，例如 `TLT` 对应 long-duration bonds，`UUP` 对应 USD。

### 15.3 Artifact Contracts

| Artifact | Path | Producer | Consumer | Required contract | Validator / eval |
|---|---|---|---|---|---|
| Corpus config | `research/kol-distillation/corpus.yaml` | User + implementer | All scripts | `corpus_id`, `source_type=x_post`, KOL list, themes, date range, capture method, rights defaults | Schema validation |
| Capture input | `research/kol-distillation/data/capture_inputs/{capture_id}.yaml` | User + local capture tool | Source converter | `capture_id`, `source_type`, `capture_method`, `source_url`, captured text or raw path, screenshot/OCR notes, captured_at, user note | Capture validator |
| Source item markdown | `research/kol-distillation/data/markdown/{source_item_id}.md` | Manual seed or converter | Extractor, provenance check | frontmatter with `source_item_id`, `kol_id`, `platform`, `source_url`, `published_at`, `collected_at`, `content_hash`, `storage_policy` | Source validator |
| Provenance manifest | `research/kol-distillation/data/provenance/source_manifest.jsonl` | Source converter | Validator, method cards | `source_item_id`, `source_url`, `platform`, `source_type`, `content_hash`, `license_or_access`, `excerpt_policy`, `rights_note` | Manifest validator |
| LLM run manifest | `research/kol-distillation/data/runs/llm_runs.jsonl` | Every LLM step | Validators, evals, audit | `llm_run_id`, prompt version, model ID, input hashes, output hash, retry metadata | Run manifest validator |
| Prediction | `research/kol-distillation/data/extracted/predictions.jsonl` | LLM extractor + reviewer | Outcome scorer, scorecards | exact schema in 15.4; includes `llm_run_id` | Prediction validator + gold-set eval |
| Manual review row | `research/kol-distillation/data/review/prediction_reviews.jsonl` | Human reviewer | Outcome scorer | `prediction_id`, `review_state`, corrected fields, reviewer, reviewed_at, reviewed prediction hash, notes | Review-state validator |
| Outcome | `research/kol-distillation/data/outcomes/prediction_outcomes.jsonl` | Outcome scorer | Scorecards, method distillation | `prediction_id`, start/end, asset return, benchmark return, alpha, success, MAE, data source, confidence | Outcome validator + fixtures |
| Scorecard | `research/kol-distillation/outputs/scorecards/{kol_or_method}.md` | Scorecard generator | Method distiller, user | sample count, hit/alpha hit rate, median return, caveats, regime notes | Snapshot eval |
| Method card | `research/kol-distillation/outputs/method_cards/{method_id}.md` | Method distiller | Skill harness, adapter | applies-to, required data, reasoning path, signal, invalidation, failure modes, supporting/contradicting evidence IDs, `llm_run_id` | Method-card validator |
| Research note | `research/kol-distillation/outputs/research_notes/{case_id}.md` | Skill harness | User, eval harness | setup, data checklist, reasoning path, invalidation, watchlist, limits, evidence citations, `llm_run_id` | Research-note eval |
| Single-ticker adapter export | `research/kol-distillation/outputs/adapters/single_ticker/{case_id}.json` | Skill harness | Future ticker workflow | Source/Annotation/Thesis-ready IDs, embedded claims, event/catalyst/watchlist links, no file mutation | Adapter schema validation |

### 15.4 Schema Contract Overrides

前文 `Prediction schema` 是研究草案示例；v0 validators 必须以本节字段和枚举为准。

Shared enums:

- `source_type`: `x_post`, `youtube_transcript`
- `capture_method`: `url_only`, `manual_text`, `thread_url`, `screenshot_ocr`, `browser_export_markdown`, `browser_export_html`, `non_official_backfill`
- `claim_type`: `directional_call`, `relative_outperformance`, `macro_regime_call`, `catalyst_call`, `thesis`, `invalidation`, `data_interpretation`
- `asset_type`: `equity`, `etf`, `index_proxy`, `rate`, `fx`, `commodity`, `volatility`, `macro_series`, `unknown`
- `direction`: `long`, `short`, `outperform`, `underperform`, `up`, `down`, `neutral`, `unknown`
- `horizon.type`: `explicit`, `fixed_bucket`, `event`, `missing`
- `horizon.bucket`: `intraday`, `5d`, `21d`, `63d`, `126d`, `null`
- `success`: `true`, `false`, `mixed`, `unscored`
- `confidence_level`: `low`, `medium`, `high`
- `review_state`: `extracted`, `pending_review`, `accepted`, `corrected`, `rejected`, `unscored`
- `unscored_reason`: `missing_horizon`, `missing_benchmark`, `missing_price`, `unsupported_macro_proxy`, `ambiguous_event_timing`, `symbol_change`, `ticker_delisted`, `merger_or_acquisition`, `benchmark_discontinued`, `rights_blocked`, `rejected_claim`

Rights and provenance enums:

- `license_or_access`: `public_web`, `public_social`, `public_youtube`, `user_authorized_excerpt`, `user_authorized_full_copy`, `paywalled_metadata_only`, `unknown`
- `storage_policy`: `metadata_only`, `short_excerpt_only`, `local_copy_user_authorized`, `transcript_reference_only`
- `excerpt_policy`: `claim_span_only`, `timestamped_snippet`, `short_user_authorized_excerpt`, `no_excerpt`
- `rights_note`: 当 `license_or_access=unknown`、`paywalled_metadata_only` 或 `user_authorized_full_copy` 时必填。

Failure behavior:

- `license_or_access=unknown` 除非 `storage_policy=metadata_only`，否则 source validation 失败。
- `paywalled_metadata_only` 不能产生用于 extraction 的 source text，除非用户提供授权 excerpt。
- `no_excerpt` source item 可以出现在 provenance 中，但不能支持 prediction extraction。

Prediction row 必填结构：

```json
{
  "prediction_id": "p_001",
  "kol_id": "sample_kol",
  "source_item_id": "src_001",
  "source_url": "https://example.com/post",
  "published_at": "2026-05-01T14:32:00Z",
  "claim_text": "...",
  "source_span": "...",
  "claim_type": "relative_outperformance",
  "asset_type": "equity",
  "tickers": ["NVDA"],
  "proxy": null,
  "direction": "outperform",
  "benchmark": "QQQ",
  "horizon": {
    "type": "event",
    "bucket": null,
    "raw_text": "next earnings",
    "event": "next earnings",
    "scoring_windows": ["63d"]
  },
  "catalyst": ["earnings"],
  "invalidation": ["capex guide cut"],
  "data_sources_mentioned": ["earnings call"],
  "extractor_confidence": 0.82,
  "confidence_level": "high",
  "review_state": "pending_review",
  "needs_human_review": true,
  "llm_run_id": "run_20260616_001"
}
```

Validation rules:

- `tickers` 可空仅当 `proxy` 非空。
- `proxy` 可空仅当 `tickers` 非空。
- `direction=unknown`、`horizon.type=missing`、缺 `source_span`、缺 scoreable benchmark 或 event timing 模糊，都必须进入 `pending_review`。
- `extractor_confidence` 必须是 `0.0-1.0`；high 为 `>=0.80`，medium 为 `>=0.55`，low 为 `<0.55`。
- `published_at` 必须是带 timezone 的 ISO 8601。
- `horizon.raw_text` 保留原文表述。
- 可评分 prediction 必须有 `horizon.scoring_windows`。例如 `3-6 months` 应展开为 `["63d","126d"]`。

Outcome row 必填结构：

```json
{
  "outcome_id": "p_001_63d",
  "prediction_id": "p_001",
  "scoring_window": "63d",
  "price_start_time": "2026-05-01T20:00:00Z",
  "price_end_time": "2026-08-03T20:00:00Z",
  "asset_forward_return": 0.12,
  "benchmark_forward_return": 0.06,
  "alpha_return": 0.06,
  "success": true,
  "max_adverse_excursion": -0.04,
  "data_source": "fixture_adjusted_close",
  "outcome_confidence": 0.95,
  "unscored_reason": null,
  "notes": "63d event fallback"
}
```

多窗口 horizon 每个 window 一行 outcome。单行 outcome 的 `success` 只能是 `true`、`false` 或 `unscored`；`mixed` 只用于 scorecard 聚合。

### 15.5 State Machines

```text
capture_input:
  queued
    -> needs_text          if URL-only or source text absent
    -> converted           if source_item + provenance produced
    -> blocked_rights      if rights/provenance cannot support extraction
    -> failed              if converter cannot parse input
    -> superseded          if stable input hash is replaced

prediction review:
  extracted
    -> pending_review      if ambiguity or hard gate requires human review
    -> accepted            only after reviewer confirms source-supported fields
  pending_review
    -> accepted
    -> corrected
    -> rejected
    -> unscored
  accepted/corrected
    -> review_stale        if current prediction hash != reviewed_prediction_hash
    -> rejected            if later audit finds unsupported claim
```

Blocking rules:

- `pending_review` 不能进入 outcome scoring。
- 100% scored predictions 必须是终态 `accepted` 或 `corrected`。
- v0 没有 `auto_accepted`。
- `rejected` 保留在 audit logs 中，但不能支持 scorecards 或 method cards。
- `unscored` 只能支持定性方法论 evidence，并且 method card 必须标注 low confidence 或解释不能评分的原因。

### 15.6 Outcome Scorer Contract

v0 scorer 必须 deterministic 且 fixture-backed。

- 数据优先级：fixtures -> market snapshots/cache -> explicit `--refresh-market-data` live fetch -> `manual_overrides` -> `unscored`。
- 美股/ETF 使用 adjusted close。
- v0 fixtures 使用 NYSE trading days。
- `published_at` 统一为 UTC，评分边界转换到 `America/New_York`。
- 如果 source 发布在美股 regular session 之外，start price 使用下一个可交易 open/close，并记录选择的 `price_start_time`。
- `intraday`、`5d`、`21d`、`63d`、`126d` 都按 NYSE 交易日解释。
- `event` 如有已知事件时间，用事件后第一个可交易价格；否则 fallback 到 `63d` 并写 notes。
- `missing` 不进主评分，标记 `success=unscored`。
- unresolved symbol change、delisting、merger、discontinued benchmark、missing price、unsupported macro proxy 不得硬算，必须输出 `unscored_reason`。

Required fixture cases:

- Market-hours directional call.
- After-hours directional call.
- Relative outperform vs `QQQ`.
- Missing horizon excluded from primary scoring.
- Event-window call.
- Macro proxy call.
- Split handled by adjusted close.
- Ticker change or delisting produces `unscored`.
- Missing benchmark or unavailable price produces `unscored`.

### 15.7 Eval And Acceptance Criteria

- Schema validation: 100% v0 artifacts 通过 validators 后才能生成 scorecards。
- Gold-set extraction: 至少 30 条人工标注 snippets；false-positive rate `<15%`；required-field hallucination rate `<5%`；100% extracted predictions 包含 `source_span`。
- Review coverage: 100% scored predictions 是 `accepted` 或 `corrected`；100% `pending_review` 在 scoring 前解决；至少 80% v0 predictions 有人工 review 或 spot-check notes。
- Outcome fixtures: 100% deterministic fixture cases 通过后才能使用 live 或人工 market data。
- Research-note evals: 至少 3 个 case 通过，覆盖 ticker thesis、macro regime、missing-data refusal。
- Research note 失败条件：给出交易建议、把 KOL 当前观点当真、编造不可用的最新数据、遗漏 invalidation、method-derived inference 没有 method/evidence IDs。
- Citation accuracy: 每个 method-derived inference 至少引用一个 method card ID 和一个 supporting evidence ID。

### 15.8 Error And Rescue Registry

| Codepath | Error class | Rescue action | User sees |
|---|---|---|---|
| `convert_x_capture.py` | `CaptureInputError` | Mark capture `failed`, log capture id and field. | "Capture input invalid. Fix required fields." |
| `convert_x_capture.py` | `InputPathRejected` | Reject path, do not read file. | "Input path outside allowed import inbox." |
| `convert_x_capture.py` | `RightsBlockedError` | Mark `blocked_rights`, allow metadata-only record. | "Source cannot support extraction until rights/provenance is fixed." |
| Source validator | `ProvenanceIncompleteError` | Block extraction, list missing fields. | "Source missing provenance fields." |
| Extractor | `EmptyModelOutput` | Record LLM failure, no prediction row. | "Model returned no extractable output." |
| Extractor | `ModelRefusal` | Record refusal, no prediction row. | "Model refused extraction." |
| Extractor | `MalformedJSON` | Record failure, no prediction row. | "Extractor returned invalid JSON." |
| Extractor | `SchemaMismatch` | Record validator errors, no scoreable row. | "Extractor output failed schema validation." |
| Extractor | `RequiredFieldHallucination` | Block output, add gold-set/eval failure if fixture. | "Required field was not source-supported." |
| Review loader | `ReviewStateError` | Reject invalid transition. | "Manual review transition is not allowed." |
| Review loader | `StaleReviewError` | Return prediction to `pending_review`. | "Review is stale because prediction content changed." |
| Scorer | `MarketDataUnavailable` | Emit `success=unscored`, continue run. | "Prediction unscored: market data unavailable." |
| Scorer | `BenchmarkUnavailable` | Emit `success=unscored`, continue run. | "Prediction unscored: benchmark unavailable." |
| Adapter | `AdapterJoinError` | Block adapter export for case. | "Adapter references source/method IDs that do not join." |
| Eval harness | `EvalFailure` | Mark run blocked or failed depending severity. | "Eval failed. See run report." |

### 15.9 Single-Ticker Adapter Contract

Command:

```bash
uv run python research/kol-distillation/scripts/export_single_ticker_adapter.py --case <case_id>
```

Adapter 是 non-mutating。它只写 JSON，不编辑 `tickers/{TICKER}/thesis.md`。

| KOL artifact field | Adapter export field | Existing research target |
|---|---|---|
| `source_item.source_url`, `published_at`, `content_hash` | `sources[].url`, `sources[].published_at`, `sources[].content_hash` | Source layer metadata |
| `prediction.claim_text`, `source_span`, `claim_type` | `annotations[].identified_content.claims[]` | Annotation identified content |
| `prediction.asset_type`, `tickers`, `proxy`, `benchmark` | `annotations[].layer_relevance`, `annotations[].themes_touched` | Annotation layer relevance |
| `method_card.method_id`, `reasoning_path`, `evidence_ids` | `annotations[].method_links[]` | Annotation cross-source links |
| `method_card.signal_conditions` | `thesis_candidate.embedded_claims[]` | Thesis embedded claims |
| `method_card.invalidation` | `thesis_candidate.invalidation[]` | Thesis invalidation conditions |
| `research_note.watchlist` | `thesis_candidate.watchlist[]` | Thesis watchlist |
| `research_note.next_events` | `calendar_candidates[]` | Calendar/catalyst layer |

Adapter output 必须包含 `adapter_schema_version`、`case_id`、`generated_at`、`sources[]`、`source_ids`、`method_ids`、`llm_run_ids`、`thesis_candidate`、`annotations` 和 `calendar_candidates`。`source_ids` 必须能 join 到 `data/provenance/source_manifest.jsonl`。fixture 至少验证一个 ticker case 和一个 macro theme case。

### 15.10 CEO Review Hardening Decisions

| Section | Decision | Status |
|---|---|---|
| Architecture | Add minimal `single_ticker_contract` schema/template plus adapter fixture. | ACCEPTED |
| Architecture | Add `capture_input` state machine before `source_item` conversion. | ACCEPTED |
| Architecture | Add `pipeline_run` manifest with phase gates. | ACCEPTED |
| Error & Rescue | Add named Error & Rescue Registry across pipeline codepaths. | ACCEPTED |
| Error & Rescue | Add hard gate for malformed/refused/hallucinated LLM outputs. | ACCEPTED |
| Error & Rescue | Market data failures default to per-prediction `unscored`, not whole-run failure. | ACCEPTED |
| Security | Add path sandbox and file type allowlist for capture inputs. | ACCEPTED |
| Security | Treat source text as untrusted data and add prompt-injection isolation fixtures. | ACCEPTED |
| Security | Rights/provenance gate blocks extraction when evidence use is not allowed or auditable. | ACCEPTED |
| Data/Interaction | Add stable artifact IDs and content-hash idempotency rules. | ACCEPTED |
| Data/Interaction | Bind manual review rows to `reviewed_prediction_hash`. | ACCEPTED |
| Code Quality | Use Pydantic models as the single schema source of truth. | ACCEPTED |
| Tests | Add adversarial fixture matrix for safety, state, and idempotency gates. | ACCEPTED |
| Performance | Add market data snapshot/cache layer with explicit refresh. | ACCEPTED |
| Observability | Generate markdown run report for every pipeline run. | ACCEPTED |
| Rollout | Add rollout, dry-run, post-run verification, and rollback checklist. | ACCEPTED |
| Future | Add artifact `schema_version` and migration/supersede policy. | ACCEPTED |
| Design/UX | Skipped. v0 has no UI scope; dashboard/review UI remains deferred. | SKIPPED |

### 15.11 Implementation Tasks

- [ ] **T1 (P1, human: ~2h / CC: ~15min)** - adapter - Add minimal `single_ticker_contract` schema/template and adapter fixtures.
  - Surfaced by: Section 1 Architecture.
  - Files: `research/kol-distillation/contracts/`, `research/kol-distillation/fixtures/adapters/`.
  - Verify: adapter validates one ticker case and one macro theme case.
- [ ] **T2 (P1, human: ~2h / CC: ~15min)** - schemas - Implement Pydantic schema source of truth with artifact schema versions and canonical hashes.
  - Surfaced by: Sections 4, 5, 10.
  - Files: `research/kol-distillation/schemas/`.
  - Verify: schema unit tests and JSON Schema export.
- [ ] **T3 (P1, human: ~2h / CC: ~15min)** - pipeline - Add `capture_input` state machine and `pipeline_run` phase gates.
  - Surfaced by: Sections 1, 4, 8.
  - Files: `research/kol-distillation/scripts/`, `research/kol-distillation/data/runs/`.
  - Verify: partial-run and blocked-run fixtures.
- [ ] **T4 (P1, human: ~2h / CC: ~15min)** - errors - Add Error & Rescue Registry and named exception classes.
  - Surfaced by: Section 2.
  - Files: `research/kol-distillation/errors.py`, scripts using validators/scorer/adapter.
  - Verify: bad-path tests assert error class, rescue action, and user message.
- [ ] **T5 (P1, human: ~2h / CC: ~15min)** - security - Add path sandbox, file allowlist, rights/provenance gate, and prompt-injection isolation fixtures.
  - Surfaced by: Section 3.
  - Files: converter, validators, extraction prompts, adversarial fixtures.
  - Verify: sandbox and adversarial source fixtures.
- [ ] **T6 (P1, human: ~2h / CC: ~15min)** - review/scoring - Bind review rows to prediction content hash and emit per-prediction unscored rows for market data failures.
  - Surfaced by: Sections 2 and 4.
  - Files: review validator, scorer, outcome fixtures.
  - Verify: stale review and unscored fixtures.
- [ ] **T7 (P2, human: ~2h / CC: ~15min)** - market-data - Add market snapshot/cache layer and explicit refresh command.
  - Surfaced by: Section 7.
  - Files: scorer, `data/market_snapshots/`, tests.
  - Verify: repeated scoring uses same snapshot unless refresh is explicit.
- [ ] **T8 (P2, human: ~1.5h / CC: ~10min)** - observability - Generate markdown run reports.
  - Surfaced by: Section 8.
  - Files: run report generator, `outputs/run_reports/`.
  - Verify: sample failed run report contains phase, counts, failures, next actions.
- [ ] **T9 (P2, human: ~1h / CC: ~10min)** - rollout - Add rollout, dry-run, verification, and rollback checklist to implementation docs.
  - Surfaced by: Section 9.
  - Files: implementation README under `research/kol-distillation/`.
  - Verify: checklist references exact commands.

### 15.12 GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | clean | 5 proposals, 5 accepted, 0 deferred; 17 hardening decisions accepted |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | - | not run |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 0 | - | eng review required |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | - | skipped, no UI scope in v0 |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | - | not run |

**VERDICT:** CEO CLEARED - ready for engineering review; eng review required before implementation.

NO UNRESOLVED DECISIONS
