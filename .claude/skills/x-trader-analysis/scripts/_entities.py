"""实体抽取的正则字典与白名单。

独立成文件方便维护：新增 ticker / 关键词时只改这里，不动 preprocess.py。

设计原则（来自 Simons 30 年经验）：
- 召回率优先于精确率：宁可多抓后由 LLM 复核，也别漏信号。
- 但 ticker 必须严格去歧：A/I/U 这类英文虚词若误判为代币，下游分析会被毒化。
- 所有正则使用 `regex` 库（不是 `re`），原因是要支持 \p{Han} 等 Unicode 类。
"""

from __future__ import annotations

import regex as re
from typing import Pattern


# ---------------------------------------------------------------------------
# 1. Ticker 白名单（主流币 + Top100 alt + meme + 常见 L2/L1）
# ---------------------------------------------------------------------------
# 注意：所有 token 都用大写。匹配时对原文做 upper() 对比。
TICKER_WHITELIST: frozenset[str] = frozenset({
    # 主流
    "BTC", "ETH", "BNB", "SOL", "XRP", "USDT", "USDC", "DAI", "TUSD", "BUSD",
    # L1 / L2 / 老牌
    "ADA", "AVAX", "DOT", "MATIC", "POL", "ATOM", "NEAR", "FTM", "ALGO", "TRX",
    "ETC", "LTC", "BCH", "XLM", "HBAR", "VET", "ICP", "FIL", "EOS", "XTZ",
    "FLOW", "EGLD", "KAS", "SUI", "APT", "SEI", "TIA", "INJ", "STX", "ARB",
    "OP", "BASE", "BLAST", "MANTA", "STRK", "ZK", "LINEA", "SCROLL",
    # DeFi
    "UNI", "AAVE", "MKR", "COMP", "SNX", "CRV", "CVX", "LDO", "RPL", "GMX",
    "DYDX", "SUSHI", "1INCH", "BAL", "YFI", "BNT", "FXS", "PENDLE",
    # Layer 0 / staking / interop
    "RNDR", "GRT", "OCEAN", "LPT", "AKT", "RUNE", "KAVA", "OSMO",
    # Meme
    "DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "MEME", "BOME", "MOG",
    "NEIRO", "POPCAT", "MEW", "BRETT", "TRUMP", "TURBO",
    # 其他热门
    "TON", "JUP", "PYTH", "JTO", "ORDI", "SATS", "WLD", "ENS", "LINK", "FET",
    "AGIX", "AI", "TAO", "OCEAN", "RNDR",  # AI 板块（注意 AI 单独维护去歧）
    # Stablecoin / wrapped
    "WBTC", "WETH", "WSOL", "STETH", "RETH", "WBETH",
    # 国产 / 中文社区常聊
    "BSV", "FIL", "HT", "OKB", "CRO", "KCS",
})

# 中文叫法映射到代币（手工维护，必要时扩展）
CHINESE_TICKER_ALIASES: dict[str, str] = {
    "比特币": "BTC", "比特": "BTC", "大饼": "BTC",
    "以太坊": "ETH", "以太": "ETH", "二饼": "ETH",
    "狗狗币": "DOGE", "狗狗": "DOGE", "屎币": "SHIB",
    "索拉纳": "SOL", "索拉那": "SOL",
    "波卡": "DOT", "波场": "TRX", "波卡币": "DOT",
    "瑞波": "XRP", "瑞波币": "XRP",
    "莱特币": "LTC",
    "门罗": "XMR",
    "卡尔达诺": "ADA", "艾达币": "ADA",
    "雪崩": "AVAX",
    "马蹄": "MATIC",
    "宇宙": "ATOM",
    "胶水": "GLMR",
    "佩佩": "PEPE", "佩佩蛙": "PEPE",
    "柴犬": "SHIB",
}

# Ticker 去歧黑名单：这些大写词在英文上下文中是常见单词，不应识别为 ticker。
# 即使它们恰好在 TICKER_WHITELIST 中（如 AI），也需在出现时检查上下文。
TICKER_STOPWORDS: frozenset[str] = frozenset({
    # 单字母 / 常见英文短词
    "A", "I", "AN", "OR", "ON", "IN", "AT", "BE", "DO", "GO", "IT", "IF",
    "IS", "ME", "MY", "NO", "OF", "SO", "TO", "UP", "US", "WE",
    # 常见英文词碰到 ticker 字母
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "ANY", "CAN",
    "HAS", "HAD", "HER", "HIS", "HOW", "ITS", "MAY", "NEW", "NOW", "OLD",
    "ONE", "OUR", "OUT", "SEE", "TWO", "WAY", "WHO", "WHY",
    # 加密俚语
    "ATH", "ATL", "DCA", "FUD", "FOMO", "HODL", "LFG", "GM", "WAGMI", "NGMI",
    "DYOR", "IMO", "TBH", "AFAIK", "ROI", "APR", "APY", "TVL", "PNL", "PR",
    "CEO", "CTO", "CFO", "USA", "UK", "EU", "USD", "EUR", "GBP", "JPY",
    "PSA", "FAQ", "FYI", "BTW", "ETA", "TGA", "TGE", "ICO", "IDO", "IEO",
    # 交易所
    "CEX", "DEX", "AMM", "LP", "MM", "OI", "FR",
})


# ---------------------------------------------------------------------------
# 2. Ticker 抽取正则
# ---------------------------------------------------------------------------
# $BTC / $ETH 风格（最可靠）：$ 后跟 2-8 个大写字母
RE_TICKER_DOLLAR: Pattern[str] = re.compile(r"\$([A-Z]{2,8})\b")

# 纯大写 token：仅在 whitelist 内匹配，且需通过 stopword 过滤
# 注意用 lookbehind / lookahead 防止匹配单词中间（如 OPEN 里的 OP）
RE_TICKER_BARE: Pattern[str] = re.compile(
    r"(?<![A-Za-z0-9$/])([A-Z]{2,8})(?![A-Za-z0-9])",
)

# 中文 ticker 别名匹配（运行时通过 dict 查找，不预编译大正则）


# ---------------------------------------------------------------------------
# 3. 价格抽取
# ---------------------------------------------------------------------------
# $45k / $1.2m / $100 / $45,000
# 拆成两组：数字 + 可选单位
RE_PRICE_USD: Pattern[str] = re.compile(
    r"\$\s?(\d{1,3}(?:[,，]\d{3})*(?:\.\d+)?)\s?([kKmMbB])?\b"
)

# 中文价格：45k刀 / 100万U / 5000美元 / 1.2万u
RE_PRICE_CN: Pattern[str] = re.compile(
    r"(\d{1,7}(?:\.\d+)?)\s?([kK千万亿]?)\s?(刀|美元|美刀|[uU])\b"
)

# 单位映射
PRICE_UNIT_MULTIPLIER: dict[str, float] = {
    "": 1.0, "k": 1_000.0, "K": 1_000.0,
    "m": 1_000_000.0, "M": 1_000_000.0,
    "b": 1_000_000_000.0, "B": 1_000_000_000.0,
    "千": 1_000.0, "万": 10_000.0, "亿": 100_000_000.0,
}


# ---------------------------------------------------------------------------
# 4. 百分比抽取
# ---------------------------------------------------------------------------
# +5% / -3.2% / 上涨 5% / 跌 3%
RE_PERCENT: Pattern[str] = re.compile(
    r"([+\-]?\d+(?:\.\d+)?)\s?%"
)


# ---------------------------------------------------------------------------
# 5. 方向词（情绪 + 操作）
# ---------------------------------------------------------------------------
DIRECTION_LONG_EN: frozenset[str] = frozenset({
    # 注意：breakout/breakdown 是 trigger 词不是方向词，归在 SIGNAL_TRIGGER_WORDS
    "long", "buy", "bought", "buying", "bullish", "bull", "pump", "pumping",
    "moon", "mooning", "rally", "ath", "fomo", "accumulate", "accumulating",
    "scalp long", "go long", "scoop", "load", "loaded",
})
DIRECTION_SHORT_EN: frozenset[str] = frozenset({
    "short", "sell", "sold", "selling", "bearish", "bear", "dump", "dumping",
    "crash", "rekt", "puked", "puke", "rugpull", "rug", "exit", "exited",
    "scalp short", "go short", "fade",
})
DIRECTION_LONG_CN: frozenset[str] = frozenset({
    "做多", "看多", "看涨", "买入", "抄底", "满仓", "加仓", "建仓", "进场",
    "梭哈", "all in", "全仓", "重仓", "反弹", "回升", "拉升", "起飞", "大涨",
    "暴涨",
})
DIRECTION_SHORT_CN: frozenset[str] = frozenset({
    "做空", "看空", "看跌", "卖出", "逃顶", "清仓", "减仓", "出货", "离场",
    "下车", "暴跌", "大跌", "崩盘", "瀑布", "插针", "止损", "斩仓",
})


# ---------------------------------------------------------------------------
# 6. 杠杆
# ---------------------------------------------------------------------------
# 数字 + x/X，且邻近(50字符内)出现 leverage/lev/杠杆
RE_LEVERAGE_TOKEN: Pattern[str] = re.compile(r"\b(\d{1,3})\s?[xX]\b")
LEVERAGE_CONTEXT_KEYWORDS: frozenset[str] = frozenset({
    "leverage", "lev", "杠杆", "倍杠杆", "x lev", "leveraged",
})


# ---------------------------------------------------------------------------
# 7. 时间框架
# ---------------------------------------------------------------------------
RE_TIMEFRAME: Pattern[str] = re.compile(
    r"\b(\d{1,3}\s?(?:min|m|h|hr|hour|d|day|w|week|mo|month))\b",
    flags=re.IGNORECASE,
)
TIMEFRAME_KEYWORDS: frozenset[str] = frozenset({
    "daily", "weekly", "monthly", "hourly", "intraday",
    "日线", "周线", "月线", "小时线", "分钟线", "日内",
})


# ---------------------------------------------------------------------------
# 8. 信号关键词（trigger / risk / sentiment）
# ---------------------------------------------------------------------------
SIGNAL_TRIGGER_WORDS: frozenset[str] = frozenset({
    # EN
    "breakout", "breakdown", "retest", "pullback", "bounce", "rejection",
    "support", "resistance", "fib", "fibo", "fibonacci", "ema", "sma", "rsi",
    "macd", "divergence", "wedge", "triangle", "flag", "pennant", "cup",
    "handle", "head and shoulders", "double top", "double bottom",
    "trendline", "channel", "consolidation", "squeeze",
    # CN
    "突破", "跌破", "回踩", "回测", "反弹", "拒绝", "支撑", "阻力",
    "压力", "斐波", "均线", "背离", "三角", "旗形", "楔形", "整理",
    "趋势线", "通道", "形态",
})

SIGNAL_RISK_WORDS: frozenset[str] = frozenset({
    # EN
    "stop", "sl", "stop loss", "stoploss", "tp", "take profit", "target",
    "risk", "risk reward", "rr", "r:r", "liquidation", "liq", "margin call",
    "drawdown", "exit plan", "invalidation",
    # CN
    "止损", "止盈", "目标", "风险", "风报比", "盈亏比", "爆仓", "强平",
    "保证金", "回撤", "出场", "止盈位", "止损位", "失效",
})

SIGNAL_SENTIMENT_WORDS: frozenset[str] = frozenset({
    # EN
    "confident", "sure", "gem", "alpha", "calling", "high conviction",
    "conviction", "high probability", "guaranteed", "easy money", "free money",
    "moon", "send it", "ape in", "100x", "1000x",
    # CN
    "笃定", "确定", "必涨", "必跌", "稳赚", "暴富", "翻倍", "翻几倍",
    "百倍币", "千倍币", "高确信", "押注", "梭哈",
})


# ---------------------------------------------------------------------------
# 9. 垃圾/营销词（spam 过滤）
# ---------------------------------------------------------------------------
SPAM_PATTERNS: tuple[Pattern[str], ...] = (
    re.compile(r"\bgiveaway\b", flags=re.IGNORECASE),
    re.compile(r"\bairdrop\b", flags=re.IGNORECASE),
    re.compile(r"\bjoin\s+(?:my|our)\s+(?:discord|tg|telegram|group)\b", flags=re.IGNORECASE),
    re.compile(r"\bdm\s+me\s+for\b", flags=re.IGNORECASE),
    re.compile(r"\bpremium\s+signal\b", flags=re.IGNORECASE),
    re.compile(r"\b(?:vip|paid)\s+(?:group|signal|channel)\b", flags=re.IGNORECASE),
    re.compile(r"私聊|私信|加我|加群|加微信|进群|内推|带单|喊单|付费信号", flags=re.IGNORECASE),
)


# ---------------------------------------------------------------------------
# 10. 杂用：emoji 检测
# ---------------------------------------------------------------------------
# 覆盖主要 emoji 区段（Misc Symbols / Pictographs / Transport / Flags / Suppl. Symbols）
RE_EMOJI: Pattern[str] = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002600-\U000026FF"
    "\U00002700-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]",
    flags=re.UNICODE,
)

# URL 检测（用于清洗后计算"去URL文本长度"）
RE_URL: Pattern[str] = re.compile(
    r"https?://[^\s一-鿿]+",
    flags=re.IGNORECASE,
)
