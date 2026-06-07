"""X 推文预处理 + 实体抽取主脚本。

Pipeline:
  raw.jsonl --[load]--> tweet dicts
            --[normalize]--> 统一字段格式
            --[noise filter]--> 标记 is_noise + noise_reasons
            --[entity extract]--> tickers / price / direction / leverage / ...
            --[signal keywords]--> trigger / risk / sentiment
            --[engagement score]--> 0..N（越高越值得 LLM 看）
            --[dedup detect]--> 标记 90%+ 相似的连续推文
            --> enriched.jsonl
            --[aggregate]--> stats.json

设计原则（来自 Simons 30 年经验）：
1. 噪音不是删除，是打标记。下游 LLM 可以自行决定是否消费。
2. 召回率 > 精确率：宁可多打几个实体让 LLM 复核，也别漏。
3. 任何聚合统计都基于 enriched 而不是 raw，方便复算。
4. 所有时间戳统一成 UTC ISO8601。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import regex as re
from dateutil import parser as date_parser

from _entities import (
    CHINESE_TICKER_ALIASES,
    DIRECTION_LONG_CN,
    DIRECTION_LONG_EN,
    DIRECTION_SHORT_CN,
    DIRECTION_SHORT_EN,
    LEVERAGE_CONTEXT_KEYWORDS,
    PRICE_UNIT_MULTIPLIER,
    RE_EMOJI,
    RE_LEVERAGE_TOKEN,
    RE_PERCENT,
    RE_PRICE_CN,
    RE_PRICE_USD,
    RE_TICKER_BARE,
    RE_TICKER_DOLLAR,
    RE_TIMEFRAME,
    RE_URL,
    SIGNAL_RISK_WORDS,
    SIGNAL_SENTIMENT_WORDS,
    SIGNAL_TRIGGER_WORDS,
    SPAM_PATTERNS,
    TICKER_STOPWORDS,
    TICKER_WHITELIST,
    TIMEFRAME_KEYWORDS,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger("x_trader.preprocess")


def _setup_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler(sys.stderr)
    fmt = "%(asctime)s [%(levelname)s] %(name)s :: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
MIN_CLEAN_TEXT_LENGTH: int = 5
EMOJI_RATIO_THRESHOLD: float = 0.70
DUPLICATE_SIMILARITY_THRESHOLD: float = 0.80
DUPLICATE_LOOKBACK_WINDOW: int = 5  # 仅与最近 N 条比较

# 上下文窗口（用于价格/杠杆判定）
PRICE_TICKER_PROXIMITY: int = 30
LEVERAGE_CONTEXT_PROXIMITY: int = 50


# ---------------------------------------------------------------------------
# 工具：文本清洗 / 相似度
# ---------------------------------------------------------------------------
def _strip_urls_and_emoji(text: str) -> str:
    """去掉 URL 与 emoji 后的纯文本，用于计算"实际有效长度"。"""
    no_url = RE_URL.sub("", text)
    no_emoji = RE_EMOJI.sub("", no_url)
    return no_emoji.strip()


def _emoji_ratio(text: str) -> float:
    """emoji 字符数占总字符数比例（去 URL 后计算）。"""
    no_url = RE_URL.sub("", text).strip()
    if not no_url:
        return 0.0
    emoji_chars = len(RE_EMOJI.findall(no_url))
    # 注意：RE_EMOJI.findall 返回的是单字符列表，长度即数量
    total = max(1, len(no_url))
    return emoji_chars / total


def _is_pure_link(text: str) -> bool:
    """去 URL 后是否还剩有效字符？无则判为纯链接。"""
    stripped = _strip_urls_and_emoji(text)
    # 允许保留 1-2 字符标点（如 "."），但视为纯链接
    cleaned = re.sub(r"[\p{P}\s]+", "", stripped)
    return len(cleaned) == 0 and RE_URL.search(text) is not None


def _normalize_for_hash(text: str) -> str:
    """生成用于去重比较的归一化字符串：去 URL/标点/空白/emoji + 小写。"""
    s = RE_URL.sub("", text)
    s = RE_EMOJI.sub("", s)
    s = re.sub(r"[\p{P}\s]+", "", s)
    return s.lower()


def _char_overlap_ratio(a: str, b: str) -> float:
    """两段文本的字符重叠率（Jaccard on character bag）。

    对短文本 + 中英混合更鲁棒，且不需要分词。
    """
    if not a or not b:
        return 0.0
    set_a = Counter(a)
    set_b = Counter(b)
    inter = sum((set_a & set_b).values())
    union = sum((set_a | set_b).values())
    if union == 0:
        return 0.0
    return inter / union


# ---------------------------------------------------------------------------
# 时间归一化
# ---------------------------------------------------------------------------
def _parse_dt(s: str | None) -> datetime | None:
    """解析任意 ISO8601 / RFC 字符串到 UTC datetime。失败返回 None。"""
    if not s:
        return None
    try:
        dt = date_parser.isoparse(s)
    except (ValueError, TypeError):
        try:
            dt = date_parser.parse(s)
        except (ValueError, TypeError, OverflowError):
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# 实体抽取
# ---------------------------------------------------------------------------
def extract_tickers(text: str) -> list[str]:
    """抽取代币符号。返回去重后的大写 ticker 列表，顺序保留首次出现。"""
    found: list[str] = []
    seen: set[str] = set()

    # 1. $TICKER 形式（最可靠）
    for m in RE_TICKER_DOLLAR.finditer(text):
        sym = m.group(1).upper()
        if sym in TICKER_STOPWORDS:
            continue
        if sym not in seen:
            seen.add(sym)
            found.append(sym)

    # 2. 纯大写 token，需在 whitelist 内
    for m in RE_TICKER_BARE.finditer(text):
        sym = m.group(1).upper()
        if sym in TICKER_STOPWORDS:
            continue
        if sym not in TICKER_WHITELIST:
            continue
        if sym not in seen:
            seen.add(sym)
            found.append(sym)

    # 3. 中文别名
    for alias, sym in CHINESE_TICKER_ALIASES.items():
        if alias in text and sym not in seen:
            seen.add(sym)
            found.append(sym)

    return found


def _parse_price_amount(num_str: str, unit: str) -> float | None:
    """把 "45" + "k" → 45000.0; "1,200" + "" → 1200.0."""
    try:
        cleaned = num_str.replace(",", "").replace("，", "")
        val = float(cleaned)
    except (ValueError, TypeError):
        return None
    mult = PRICE_UNIT_MULTIPLIER.get(unit, 1.0)
    return val * mult


def extract_price_mentions(text: str, nearby_tickers: list[str]) -> list[dict[str, Any]]:
    """抽取价格提及。

    策略：
    - $45k / $1.2m / $100 风格 → USD
    - 45k刀 / 100万U → USD（中文）
    - 只在邻近 30 字内有 ticker 时记录（除非是 $-前缀且很可能是金额）
    - 实际上 USD 标记的金额本身就高度可信，不强制要求邻近 ticker
    """
    results: list[dict[str, Any]] = []

    # USD 风格
    for m in RE_PRICE_USD.finditer(text):
        raw = m.group(0)
        num, unit = m.group(1), (m.group(2) or "")
        val = _parse_price_amount(num, unit)
        if val is None:
            continue
        # 过滤明显不是价格的小数字（避免 $1 这种被无脑收）
        if val < 0.0001:
            continue
        results.append({"raw": raw, "value": val, "currency": "USD"})

    # 中文风格：45k刀 / 100万U / 5000美元
    for m in RE_PRICE_CN.finditer(text):
        raw = m.group(0)
        num, scale, _suffix = m.group(1), (m.group(2) or ""), m.group(3)
        val = _parse_price_amount(num, scale)
        if val is None:
            continue
        if val < 0.0001:
            continue
        results.append({"raw": raw, "value": val, "currency": "USD"})

    return results


def extract_percent_mentions(text: str) -> list[dict[str, Any]]:
    """抽取百分比。"""
    results: list[dict[str, Any]] = []
    for m in RE_PERCENT.finditer(text):
        raw = m.group(0)
        try:
            val = float(m.group(1))
        except (ValueError, TypeError):
            continue
        # 过滤明显异常的（>10000% 多半是噪音）
        if abs(val) > 10_000:
            continue
        results.append({"raw": raw, "value": val})
    return results


def extract_direction_hints(text: str) -> list[str]:
    """抽取方向词（多/空/buy/sell 等）。返回归一化后的标签列表。"""
    lower = text.lower()
    hints: list[str] = []
    seen: set[str] = set()

    # 英文：必须整词匹配
    # 简单做法：用空格切分后查表（再补一个 substring 模糊匹配兜底）
    tokens = set(re.findall(r"[a-z]+", lower))
    for word in DIRECTION_LONG_EN:
        # 短语包含空格的 fallback：直接 substring 检查
        if " " in word:
            if word in lower and word not in seen:
                seen.add(word)
                hints.append(word)
        elif word in tokens and word not in seen:
            seen.add(word)
            hints.append(word)
    for word in DIRECTION_SHORT_EN:
        if " " in word:
            if word in lower and word not in seen:
                seen.add(word)
                hints.append(word)
        elif word in tokens and word not in seen:
            seen.add(word)
            hints.append(word)

    # 中文：直接 substring 匹配（无需分词）
    for word in DIRECTION_LONG_CN:
        if word in text and word not in seen:
            seen.add(word)
            hints.append(word)
    for word in DIRECTION_SHORT_CN:
        if word in text and word not in seen:
            seen.add(word)
            hints.append(word)

    return hints


def classify_direction(direction_hints: list[str]) -> str:
    """根据方向词的出现情况判定整体倾向（long / short / neutral）。"""
    long_set = DIRECTION_LONG_EN | DIRECTION_LONG_CN
    short_set = DIRECTION_SHORT_EN | DIRECTION_SHORT_CN

    n_long = sum(1 for h in direction_hints if h in long_set)
    n_short = sum(1 for h in direction_hints if h in short_set)

    if n_long > n_short:
        return "long"
    if n_short > n_long:
        return "short"
    return "neutral"


def extract_leverage_hints(text: str) -> list[str]:
    """抽取杠杆倍数。仅当数字+x 邻近(50字符)出现 leverage/lev/杠杆 时记录。"""
    lower = text.lower()
    hints: list[str] = []
    seen: set[str] = set()

    for m in RE_LEVERAGE_TOKEN.finditer(text):
        raw = m.group(0)
        try:
            n = int(m.group(1))
        except ValueError:
            continue
        # 过滤 1x（无意义）和 >125x（Binance 最大 125）
        if n < 2 or n > 125:
            continue

        # 检查上下文窗口
        start = max(0, m.start() - LEVERAGE_CONTEXT_PROXIMITY)
        end = min(len(text), m.end() + LEVERAGE_CONTEXT_PROXIMITY)
        window = lower[start:end]
        if any(kw in window for kw in LEVERAGE_CONTEXT_KEYWORDS):
            tag = f"{n}x"
            if tag not in seen:
                seen.add(tag)
                hints.append(tag)

    return hints


def extract_timeframe_hints(text: str) -> list[str]:
    """抽取时间框架（1h, 4h, daily, 日线...）。"""
    lower = text.lower()
    hints: list[str] = []
    seen: set[str] = set()

    for m in RE_TIMEFRAME.finditer(text):
        raw = m.group(1).lower().replace(" ", "")
        if raw not in seen:
            seen.add(raw)
            hints.append(raw)

    for kw in TIMEFRAME_KEYWORDS:
        if kw in lower or kw in text:
            if kw not in seen:
                seen.add(kw)
                hints.append(kw)

    return hints


def extract_signal_keywords(text: str) -> dict[str, list[str]]:
    """三类信号关键词：trigger / risk / sentiment。"""
    lower = text.lower()
    result: dict[str, list[str]] = {
        "trigger_words": [],
        "risk_words": [],
        "sentiment_words": [],
    }

    def _scan(words: Iterable[str], bucket: list[str]) -> None:
        seen: set[str] = set()
        for w in words:
            # 中文直接 substring；英文要尽量整词（substring 在英文文本也够好，因为关键词都比较长）
            if w in lower or w in text:
                if w not in seen:
                    seen.add(w)
                    bucket.append(w)

    _scan(SIGNAL_TRIGGER_WORDS, result["trigger_words"])
    _scan(SIGNAL_RISK_WORDS, result["risk_words"])
    _scan(SIGNAL_SENTIMENT_WORDS, result["sentiment_words"])

    return result


# ---------------------------------------------------------------------------
# 噪音过滤
# ---------------------------------------------------------------------------
def detect_noise(
    tweet: dict[str, Any],
    text: str,
    recent_hashes: list[tuple[str, str]],
) -> list[str]:
    """返回 noise reasons 列表。空列表表示非噪音。

    recent_hashes: [(normalized_text, hash), ...] 最近 N 条的归一化内容，用于查重
    """
    reasons: list[str] = []

    # 1. 纯转推
    if tweet.get("is_retweet"):
        reasons.append("retweet")

    # 2. 长度太短（去 URL + emoji 后）
    clean = _strip_urls_and_emoji(text)
    if len(clean) < MIN_CLEAN_TEXT_LENGTH:
        reasons.append("too_short")

    # 3. 纯链接
    if _is_pure_link(text):
        reasons.append("pure_link")

    # 4. emoji 灌水
    if _emoji_ratio(text) > EMOJI_RATIO_THRESHOLD:
        reasons.append("emoji_only")

    # 5. spam（营销词）
    for pat in SPAM_PATTERNS:
        if pat.search(text):
            reasons.append("spam")
            break

    # 6. 重复（与最近 N 条比较）
    norm = _normalize_for_hash(text)
    if norm:
        norm_hash = hashlib.md5(norm.encode("utf-8")).hexdigest()
        for prev_norm, prev_hash in recent_hashes:
            if norm_hash == prev_hash:
                reasons.append("duplicate")
                break
            if len(norm) >= 10 and _char_overlap_ratio(norm, prev_norm) >= DUPLICATE_SIMILARITY_THRESHOLD:
                reasons.append("duplicate")
                break

    # 去重 reasons 同时保持顺序
    seen: set[str] = set()
    ordered: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    return ordered


# ---------------------------------------------------------------------------
# Engagement score
# ---------------------------------------------------------------------------
def calc_engagement_score(tweet: dict[str, Any]) -> float:
    """score = (likes + 2*RT + 3*replies) / max(1, views) * 1000

    用 max(1, views) 防止除零；返回保留 4 位小数。
    """
    likes = int(tweet.get("like_count") or 0)
    retweets = int(tweet.get("retweet_count") or 0)
    replies = int(tweet.get("reply_count") or 0)
    views = int(tweet.get("view_count") or 0)
    if views <= 0:
        # 没 view 数据时退化成原始加权和（线性，仍可比）
        return float(likes + 2 * retweets + 3 * replies)
    score = (likes + 2 * retweets + 3 * replies) / max(1, views) * 1000.0
    return round(score, 4)


# ---------------------------------------------------------------------------
# 主 pipeline
# ---------------------------------------------------------------------------
def enrich_tweet(
    tweet: dict[str, Any],
    recent_hashes: list[tuple[str, str]],
) -> dict[str, Any]:
    """单条推文 → enriched dict。"""
    text = str(tweet.get("text") or "")

    # 实体抽取
    tickers = extract_tickers(text)
    price_mentions = extract_price_mentions(text, tickers)
    percent_mentions = extract_percent_mentions(text)
    direction_hints = extract_direction_hints(text)
    leverage_hints = extract_leverage_hints(text)
    timeframe_hints = extract_timeframe_hints(text)
    signal_keywords = extract_signal_keywords(text)

    # 噪音判定
    noise_reasons = detect_noise(tweet, text, recent_hashes)
    is_noise = len(noise_reasons) > 0

    # Engagement
    engagement = calc_engagement_score(tweet)

    # URL 兜底：从 external_urls 取第一个，否则用 https://x.com/<user>/status/<id>
    url = ""
    ext_urls = tweet.get("external_urls") or []
    if ext_urls:
        url = str(ext_urls[0])
    elif tweet.get("user") and tweet.get("tweet_id"):
        url = f"https://x.com/{tweet['user']}/status/{tweet['tweet_id']}"

    enriched: dict[str, Any] = {
        "tweet_id": tweet.get("tweet_id"),
        "user": tweet.get("user"),
        "created_at": tweet.get("created_at"),
        "text": text,
        "lang": tweet.get("lang"),
        "is_noise": is_noise,
        "noise_reasons": noise_reasons,
        "engagement_score": engagement,
        "engagement_raw": {
            "like_count": int(tweet.get("like_count") or 0),
            "retweet_count": int(tweet.get("retweet_count") or 0),
            "reply_count": int(tweet.get("reply_count") or 0),
            "view_count": int(tweet.get("view_count") or 0),
        },
        "entities": {
            "tickers": tickers,
            "price_mentions": price_mentions,
            "percent_mentions": percent_mentions,
            "direction_hints": direction_hints,
            "direction_label": classify_direction(direction_hints),
            "leverage_hints": leverage_hints,
            "timeframe_hints": timeframe_hints,
        },
        "signal_keywords": signal_keywords,
        "hashtags": tweet.get("hashtags") or [],
        "mentions": tweet.get("mentions") or [],
        "url": url,
    }
    return enriched


def _load_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                logger.warning("跳过第 %d 行 JSON 解析失败: %s", line_no, exc)


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")
            n += 1
    return n


def _quartile(values: list[float], q: float) -> float:
    """简易分位数（线性插值）。q ∈ [0,1]。"""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    pos = (len(s) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] * (1 - frac) + s[hi] * frac


def aggregate_stats(
    enriched: list[dict[str, Any]],
    noise_breakdown: Counter,
    total_in: int,
) -> dict[str, Any]:
    """从 enriched 推文聚合 stats.json。"""
    after_filter = sum(1 for r in enriched if not r["is_noise"])

    # 语言分布（对全量计算，不区分 noise）
    lang_counter: Counter = Counter()
    for r in enriched:
        lang = r.get("lang") or "unknown"
        lang_counter[lang] += 1

    # 时间分布
    dts: list[datetime] = []
    daily_counter: Counter = Counter()
    for r in enriched:
        dt = _parse_dt(r.get("created_at"))
        if dt is None:
            continue
        dts.append(dt)
        daily_counter[dt.date().isoformat()] += 1

    time_range: dict[str, Any] = {}
    tweet_frequency: dict[str, Any] = {}
    if dts:
        start = min(dts)
        end = max(dts)
        span_days = max(1, (end.date() - start.date()).days + 1)
        time_range = {
            "start": start.date().isoformat(),
            "end": end.date().isoformat(),
            "span_days": span_days,
        }
        daily_counts = list(daily_counter.values())
        per_day_median = float(median(daily_counts)) if daily_counts else 0.0

        # 周聚合
        weekly_counter: Counter = Counter()
        for dt in dts:
            iso_year, iso_week, _ = dt.isocalendar()
            weekly_counter[f"{iso_year}-W{iso_week:02d}"] += 1
        per_week_median = float(median(weekly_counter.values())) if weekly_counter else 0.0

        peak_day, peak_count = max(daily_counter.items(), key=lambda kv: kv[1])
        tweet_frequency = {
            "per_day_median": per_day_median,
            "per_week_median": per_week_median,
            "peak_day": peak_day,
            "peak_count": peak_count,
        }

    # Ticker 频次（仅非噪音）
    ticker_counter: Counter = Counter()
    direction_counter: Counter = Counter({"long_hints": 0, "short_hints": 0, "neutral": 0})
    hashtag_counter: Counter = Counter()
    engagement_values: list[float] = []
    candidate_top: list[tuple[float, str, str]] = []  # (score, tweet_id, preview)

    for r in enriched:
        if r["is_noise"]:
            continue
        for t in r["entities"]["tickers"]:
            ticker_counter[t] += 1
        label = r["entities"]["direction_label"]
        if label == "long":
            direction_counter["long_hints"] += 1
        elif label == "short":
            direction_counter["short_hints"] += 1
        else:
            direction_counter["neutral"] += 1
        for h in r.get("hashtags") or []:
            tag = h if h.startswith("#") else f"#{h}"
            hashtag_counter[tag] += 1
        engagement_values.append(r["engagement_score"])
        preview = r["text"][:140].replace("\n", " ")
        candidate_top.append((r["engagement_score"], str(r["tweet_id"] or ""), preview))

    engagement_quartiles: dict[str, float] = {
        "q25": round(_quartile(engagement_values, 0.25), 4),
        "q50": round(_quartile(engagement_values, 0.50), 4),
        "q75": round(_quartile(engagement_values, 0.75), 4),
        "q95": round(_quartile(engagement_values, 0.95), 4),
    } if engagement_values else {"q25": 0.0, "q50": 0.0, "q75": 0.0, "q95": 0.0}

    candidate_top.sort(reverse=True, key=lambda x: x[0])
    top_engagement_tweets = [
        {"tweet_id": tid, "score": score, "text_preview": prev}
        for score, tid, prev in candidate_top[:10]
    ]

    stats: dict[str, Any] = {
        "total_tweets": total_in,
        "after_filter": after_filter,
        "noise_breakdown": dict(noise_breakdown),
        "lang_distribution": dict(lang_counter),
        "time_range": time_range,
        "tweet_frequency": tweet_frequency,
        "ticker_frequency": dict(ticker_counter.most_common(50)),
        "direction_breakdown": dict(direction_counter),
        "engagement_quartiles": engagement_quartiles,
        "top_engagement_tweets": top_engagement_tweets,
        "hashtag_frequency": dict(hashtag_counter.most_common(50)),
    }
    return stats


def run(in_path: Path, out_enriched: Path, out_stats: Path) -> dict[str, Any]:
    """主入口：读 raw jsonl，写 enriched jsonl + stats json。

    返回 stats dict（方便测试 / 调用方使用）。
    """
    if not in_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {in_path}")
    if not in_path.is_file():
        raise ValueError(f"输入路径不是文件: {in_path}")

    logger.info("开始预处理: %s", in_path)

    # 一次遍历：load → enrich → buffer 用于 stats
    recent_norm_window: list[tuple[str, str]] = []  # [(norm_text, hash)]
    noise_breakdown: Counter = Counter()
    enriched_rows: list[dict[str, Any]] = []
    total_in = 0

    for tweet in _load_jsonl(in_path):
        total_in += 1
        enriched = enrich_tweet(tweet, recent_norm_window)
        enriched_rows.append(enriched)

        if enriched["is_noise"]:
            for reason in enriched["noise_reasons"]:
                noise_breakdown[reason] += 1

        # 维护去重窗口
        text = enriched["text"]
        norm = _normalize_for_hash(text)
        if norm:
            norm_hash = hashlib.md5(norm.encode("utf-8")).hexdigest()
            recent_norm_window.append((norm, norm_hash))
            if len(recent_norm_window) > DUPLICATE_LOOKBACK_WINDOW:
                recent_norm_window.pop(0)

    logger.info("读取完成: %d 条原始推文", total_in)

    n_written = _write_jsonl(out_enriched, enriched_rows)
    logger.info("写入 enriched.jsonl: %s (%d 行)", out_enriched, n_written)

    stats = aggregate_stats(enriched_rows, noise_breakdown, total_in)
    out_stats.parent.mkdir(parents=True, exist_ok=True)
    with out_stats.open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    logger.info("写入 stats.json: %s", out_stats)

    logger.info(
        "汇总: total=%d, after_filter=%d, noise=%s",
        stats["total_tweets"],
        stats["after_filter"],
        stats["noise_breakdown"],
    )
    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="preprocess",
        description="X 推文预处理 + 实体抽取（中文方向词、ticker、价格、信号）。",
    )
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        required=True,
        help="原始 jsonl 输入路径",
    )
    p.add_argument(
        "--out-enriched",
        type=Path,
        required=True,
        help="enriched.jsonl 输出路径",
    )
    p.add_argument(
        "--out-stats",
        type=Path,
        required=True,
        help="stats.json 输出路径",
    )
    p.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="日志级别",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    _setup_logging(getattr(logging, args.log_level))

    try:
        run(args.in_path, args.out_enriched, args.out_stats)
    except FileNotFoundError as exc:
        logger.error("文件错误: %s", exc)
        return 2
    except ValueError as exc:
        logger.error("参数错误: %s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001 — 顶层兜底，避免静默崩溃
        logger.exception("处理失败: %s", exc)
        return 1
    return 0


# ---------------------------------------------------------------------------
# 自检：mock 数据
# ---------------------------------------------------------------------------
def _self_check() -> None:
    """用 5 条 mock 推文跑通流程，打印噪音统计 + 1 条 enriched 示例。"""
    import tempfile

    mock_tweets = [
        {
            "tweet_id": "1001",
            "user": "ShanghaoJin",
            "created_at": "2025-03-15T12:00:00Z",
            "text": "$BTC breakout above $72k, going long with 10x leverage. SL at 70k. 笃定看多.",
            "is_retweet": False,
            "is_reply": False,
            "like_count": 500,
            "retweet_count": 100,
            "reply_count": 50,
            "view_count": 10000,
            "lang": "en",
            "hashtags": ["BTC", "trading"],
            "mentions": [],
            "external_urls": [],
        },
        {
            "tweet_id": "1002",
            "user": "ShanghaoJin",
            "created_at": "2025-03-15T13:00:00Z",
            "text": "RT @somebody: just a retweet",
            "is_retweet": True,
            "is_reply": False,
            "like_count": 5,
            "retweet_count": 1,
            "reply_count": 0,
            "view_count": 200,
            "lang": "en",
            "hashtags": [],
            "mentions": ["somebody"],
            "external_urls": [],
        },
        {
            "tweet_id": "1003",
            "user": "ShanghaoJin",
            "created_at": "2025-03-16T09:00:00Z",
            "text": "https://example.com/foo",
            "is_retweet": False,
            "is_reply": False,
            "like_count": 1,
            "retweet_count": 0,
            "reply_count": 0,
            "view_count": 100,
            "lang": "en",
            "hashtags": [],
            "mentions": [],
            "external_urls": ["https://example.com/foo"],
        },
        {
            "tweet_id": "1004",
            "user": "ShanghaoJin",
            "created_at": "2025-03-16T10:00:00Z",
            "text": "以太坊跌破支撑位，建议止损离场。-5% 回撤已止盈一半。看空 ETH。",
            "is_retweet": False,
            "is_reply": False,
            "like_count": 300,
            "retweet_count": 50,
            "reply_count": 20,
            "view_count": 8000,
            "lang": "zh",
            "hashtags": ["ETH"],
            "mentions": [],
            "external_urls": [],
        },
        {
            "tweet_id": "1005",
            "user": "ShanghaoJin",
            "created_at": "2025-03-16T11:00:00Z",
            "text": "Join my discord for premium signal! 100x gem alpha!",
            "is_retweet": False,
            "is_reply": False,
            "like_count": 2,
            "retweet_count": 0,
            "reply_count": 0,
            "view_count": 150,
            "lang": "en",
            "hashtags": [],
            "mentions": [],
            "external_urls": [],
        },
    ]

    _setup_logging(logging.INFO)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        in_p = tmp_path / "raw.jsonl"
        out_e = tmp_path / "enriched.jsonl"
        out_s = tmp_path / "stats.json"

        with in_p.open("w", encoding="utf-8") as f:
            for t in mock_tweets:
                f.write(json.dumps(t, ensure_ascii=False))
                f.write("\n")

        stats = run(in_p, out_e, out_s)

        logger.info("=== 自检 stats ===")
        logger.info(json.dumps(stats, ensure_ascii=False, indent=2))

        # 打印第一条 enriched 作为示例
        with out_e.open("r", encoding="utf-8") as f:
            first = json.loads(f.readline())
        logger.info("=== 第一条 enriched 示例 ===")
        logger.info(json.dumps(first, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 无参数时跑自检
        _self_check()
        sys.exit(0)
    sys.exit(main())
