# `tradesdontlie/tradingview-mcp` 封号案例检索

检索日期：2026-08-06（Asia/Tokyo）

## 结论

在本次检索到的公开、可索引内容中，没有找到可以核验的第一手案例，能够证明某个用户因使用 `tradesdontlie/tradingview-mcp` 而被 TradingView 封号、临时封禁或永久封禁。

这不是“没有人被封”的证明：封禁通常是私密的，用户也可能没有公开发帖，搜索引擎还可能遗漏 X、Discord、Telegram 等内容。当前结论应表述为“未找到公开可核验案例”，而不是“没有封号风险”。

## 证据分级

### A. 直接相关的公开使用记录：未报告封号

- Reddit 用户公开展示使用 TradingView MCP 读取图表并让 Claude 进行分析，评论中还讨论了 `--remote-debugging-port=9222` 的连接方式；帖子没有报告账号被封或收到 TradingView 警告：[I Connected Claude AI to TradingView Charts (It Actually Works)](https://www.reddit.com/r/ai_trading/comments/1u68h7h/i_connected_claude_ai_to_tradingview_charts_it/)。该帖评论区明确链接到 `tradesdontlie/tradingview-mcp`。
- 另一个 Reddit 帖子讨论 `tradingview-mcp` 的 ML/AI 数据管线；同样没有报告封号：[ML/AI with Tradingview-mcp](https://www.reddit.com/r/ai_trading/comments/1tg1aen/mlai_with_tradingviewmcp/)。

这些只能说明有人公开声称在使用，不能证明长期使用安全，也不能排除帖子作者使用的是小号、尚未被检测或之后发生了封禁。

### B. 风险警告或猜测：不是封号案例

- 一篇日文实操文章明确提到该工具的用途，并写道账号“可能”被 BAN、需要自行承担责任；作者没有说自己已经被封：[例のツールをごにょごにょしてClaudeのデスクトップアプリと連携させるのを簡単便利にしてみた](https://note.com/yutas001/n/n0dab6bcd9e3c)。因此它是风险提示，不是实证。
- Reddit 上有一条专门讨论“使用这个 TradingView MCP 是否违反 ToS、是否会被封号”的帖子，但帖子指向的是另一个项目 `atilaahmettaner/tradingview-mcp`，不是本次目标的 `tradesdontlie/tradingview-mcp`：[Does this Trading View MCP server breach the Terms of Service?](https://www.reddit.com/r/TradingView/comments/1u38kl7/does_this_trading_view_mcp_server_breach_the/)。不能把它当作第一个 MCP 的封号案例。
- 目标仓库的 Issues 搜索 `is:issue ban` 当前没有结果：[tradesdontlie/tradingview-mcp issues](https://github.com/tradesdontlie/tradingview-mcp/issues?q=is%3Aissue+ban)；Discussions 的 `ban` 搜索也没有匹配项：[tradesdontlie/tradingview-mcp discussions](https://github.com/tradesdontlie/tradingview-mcp/discussions?discussions_q=ban)。这只是公开仓库内没有留下相关报告，不等于平台侧没有封禁。

### C. TradingView 官方的一般性封禁依据

TradingView 官方说明，因“可疑活动”触发的封禁包括使用脚本、API、屏幕抓取、数据挖掘、机器人或其他数据收集/提取工具，且不因使用目的为研究而自动豁免；外部软件、工具、脚本、机器人和扩展进行自动化也不允许。首次若干次可能是临时封禁，连续违规可能永久封禁：[Why is my account banned due to suspicious activity?](https://www.tradingview.com/support/solutions/43000674726-why-is-my-account-banned-due-to-suspicious-activity/)。

目标仓库自己也说明它通过 TradingView Desktop 的本地 CDP 连接、使用未公开的内部接口，并提示程序化消费数据可能与 TradingView 条款冲突、存在封禁/暂停和法律风险：[tradesdontlie/tradingview-mcp README](https://github.com/tradesdontlie/tradingview-mcp)。因此“没有找到案例”不能转化为“官方允许”。

## 目前可下的判断

1. **封号实证：未找到。** 没有找到“我使用 `tradesdontlie/tradingview-mcp` 后被封”的可核验公开一手陈述。
2. **官方规则风险：明确存在。** TradingView 的规则描述的是行为类型，而不是是否用于交易；“只做研究、不程序化下单”不能自动消除自动化采集/提取风险。
3. **检测与触发阈值：未知。** 官方公开页面没有说明具体检测阈值、频率窗口或 CDP 是否单独识别；不应据此推断低频、人工确认就一定安全。

## 后续核验建议

如果需要把结论升级为更高置信度的尽调，应直接向仓库维护者和实际用户询问：是否使用主账号、持续运行多久、请求频率、是否出现过 `suspicious activity`、临时限制或图表功能失效，并要求提供可打码的 TradingView 通知或工单截图。没有这些材料，不应把社媒上的“能运行”当作“合规或不会封”。
