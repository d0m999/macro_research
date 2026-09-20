# X KOL 投资风格识别：开源项目检索

> 检索日期：2026-08-31。本文只评估公开代码的研究用途，不构成投资建议，也不建议接入自动下单或自动跟单。

## 结论

GitHub 上已经有数据采集器、MCP 连接层、浏览器 Skill、本地 RAG 和加密货币信号验证项目，但目前没有找到一个成熟项目能同时完成：

```text
指定 X KOL 的历史内容采集 → 投资观点抽取 → 事后表现验证 → 方法论蒸馏 → 可复用 SKILL.md
```

最可行的实现是组合多个层次：官方 X API 负责可审计采集，本地 RAG 负责证据检索，自定义结构化抽取和前瞻性评估负责“投资风格”，最后再生成 `SKILL.md`。

## 候选项目

| 层次 | 项目 | 已有能力 | 主要缺口 |
| --- | --- | --- | --- |
| AI 数据连接 | [`6551Team/opentwitter-mcp`](https://github.com/6551Team/opentwitter-mcp) | MCP 提供用户资料、用户推文、搜索、KOL tracking 等工具，适合让 Claude/Cursor 直接查询某个账号。 | 数据来自外部 6551 服务，需要其 token；不是本地 X crawler，也没有投资风格蒸馏。 |
| 现成浏览器 Skill | [`SamCuipogobongo/x-collect`](https://github.com/SamCuipogobongo/x-collect) | Claude Code Skill + Actionbook 浏览器自动化；将 X 内容和互动数据输出为 JSONL/Markdown。 | 重点是主题/内容情报；不是完整的指定 KOL 历史抓取、投资观点抽取或回测。 |
| 中文时间线过滤 | [`Wade-Song/Twitter-Scanner`](https://github.com/Wade-Song/Twitter-Scanner) | Chrome 扩展读取当前可见的 X 时间线，用 Claude 做高价值内容分类、中文总结、主题聚合和 Markdown 输出。 | 更像关注初期的降噪原型；当前可见内容有限，不是历史数据库或投资风格模型。 |
| 单条内容标准化 | [`tweet-md/skill`](https://github.com/tweet-md/skill) | 提供公开 `SKILL.md`，把 X 帖子、Thread、Article 或 profile 转成适合 LLM/RAG 的 Markdown。 | 适合精选帖子/线程，不是批量时间线采集器；按仓库说明，部分资源/API 有访问和付费限制。 |
| 本地证据/RAG 底座 | [`mameshivaa/x-archive-rag`](https://github.com/mameshivaa/x-archive-rag) | 导入 X archive ZIP/目录，使用 SQLite、FTS5、轻量语义检索、引用 ID、persona profile 和 MCP；适合沉淀本地可追溯知识库。 | 按仓库说明目前是 Alpha，输入是 archive，不负责任意 KOL 的采集；需要自己做 KOL JSONL 适配。 |
| 投资信号参考 | [`2582552544-gif/memerecall`](https://github.com/2582552544-gif/memerecall) | 面向 Crypto Twitter，将帖子分为 S0–S4 噪声到买入/退出声明，并尝试做钱包匹配、真实性、纪律性和跟随收益模拟。 | 加密货币专用、实验性强；更接近信号验证而非一般投资风格。未看到清晰的可复用许可证，不应直接用于生产或自动跟单。 |
| RAG 应用参考 | [`sid-2209/rag-assistant-twitter-x-influencer-knowledge-base`](https://github.com/sid-2209/rag-assistant-twitter-x-influencer-knowledge-base) | FastAPI、向量检索、引用、`/ingest`、`/query` 和数据集上传，展示了完整的“导入后问答”形态。 | 需要已有数据集，不负责 X 采集；更适合作为 RAG 原型参考，不宜视为生产方案。 |

`YoriHan/influencer-skills` 的定位是把 X/YouTube/LinkedIn KOL 管理到 Notion，偏营销/GTM；它不是投资方法论蒸馏器。[仓库](https://github.com/YoriHan/influencer-skills)

## 采集层的选择

长期和可审计方案应优先使用官方 API：

- X 的 [`GET /2/users/:id/tweets`](https://docs.x.com/x-api/posts/timelines/introduction) 支持按用户取帖子、分页、时间范围以及排除回复/转发，但用户时间线最多返回该用户最近约 3,200 条帖子。
- X Search 的 [`from:` 查询](https://docs.x.com/x-api/posts/search/introduction) 可按账号检索；Recent Search 面向最近 7 天，Full-Archive Search 回溯到 2006 年，但后者面向 Pay-per-use/Enterprise 方案。
- Python 可以用官方 API 的 [`tweepy/tweepy`](https://github.com/tweepy/tweepy)；Node.js 可考虑 [`node-twitter-api-v2`](https://github.com/PLhery/node-twitter-api-v2)。这些是 API client，不是 AI 蒸馏系统。

`twscrape` 和 `twikit` 可以作为实验性非官方采集器参考，但它们依赖登录、Cookie 或 X 内部接口，稳定性和条款边界都更差；`twscrape` 的近期 issue 也记录了 Cloudflare challenge 导致的 Cookie 账号失败。[twscrape](https://github.com/vladkens/twscrape)、[twikit](https://github.com/d60/twikit)、[issue #330](https://github.com/vladkens/twscrape/issues/330)

## 推荐的 KOL 风格蒸馏管线

```text
X @handle
  ↓
帖子 ID/时间/URL/正文/媒体/回复与转发标记
  ↓
观点 JSON：资产、方向、时间窗口、催化剂、失效条件、置信度、引用证据
  ↓
按帖子发布时间计算未来表现，并与基准和同周期市场表现比较
  ↓
风格卡：资产范围、持有周期、方向偏好、信号类型、风险纪律、修正习惯
  ↓
evidence.jsonl + methodology.md + KOL_<handle>/SKILL.md
```

不要只让模型总结语气或主题。要至少区分：

1. `commentary`、新闻转发、明确预测、明确交易声明和事后解释；
2. 看多/看空/中性、资产和市场、时间窗口、催化剂、失效条件；
3. 观点是否可证伪、是否在期限内兑现、是否修改过观点；
4. 命中率、收益、最大不利波动、基准超额和样本量，并保留每项指标的原始证据。

## 对当前 `vibe-trading` 仓库的建议

仓库已有 [`docs/us-macro-kol-methodology-distillation.md`](../us-macro-kol-methodology-distillation.md)，其中的候选池、内容归一化、观点抽取、回测评分、方法论卡和 `SKILL.md` 骨架已经接近上述目标。建议在它上面接一个采集适配器，优先做本地研究证据链，不重新引入 Python/FreqTrade 执行层或交易数据库。

第一版可以这样选：

```text
官方 X API + Tweepy
→ 规范化 JSONL
→ x-archive-rag 本地证据库
→ 自定义投资观点抽取/前瞻评估
→ SKILL.md
```

如果只是快速验证交互，再用 `opentwitter-mcp` 或 `x-collect`；如果研究对象是 Crypto KOL，可以借鉴 `memerecall` 的信号分类，但必须补上价格基准、时间窗口、失效条件和样本外评估。

## X 平台边界

X 开发者政策对内容再分发、删除请求、API key、速率限制和商业使用有要求；不要把已展开的原始 X 内容数据集直接提交到公开 GitHub，也不要采集受保护/私密内容或绕过平台限制。[Developer Policy](https://docs.x.com/developer-terms/policy)、[Restricted Use Cases](https://docs.x.com/developer-terms/restricted-use-cases)

官方 Developer Agreement 还明确限制将 X API/X Content 用于 foundation/frontier model 的 fine-tune 或训练。把一组证据整理成本地研究用 `SKILL.md` 与训练基础模型不是同一件事，但实际用途仍需按你的账号、产品和商业模式核对条款；本文不是法律意见。[Developer Agreement](https://docs.x.com/developer-terms/agreement)
