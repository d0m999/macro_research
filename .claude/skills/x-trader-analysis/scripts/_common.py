"""共享工具：jsonl 流式写入、时间分片、tweet 字段标准化。

为 scrape_twscrape.py、scrape_apify.py、scrape_scweet.py 提供基础设施。
不依赖任何爬虫 SDK，纯标准库 + 项目已有依赖（rich, orjson）。
"""

from __future__ import annotations

import logging
import os
import sys
from calendar import monthrange
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import orjson  # 项目已依赖
except ImportError:  # pragma: no cover - fallback to stdlib
    orjson = None  # type: ignore
    import json


# ---------------------------------------------------------------------------
# 日志：复用项目 logging_config 的结构化思路，但精简版以避免循环依赖
# ---------------------------------------------------------------------------


class _JsonFormatter(logging.Formatter):
    """结构化 JSON 日志格式，与项目 logging_config.py 风格保持一致。"""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        # 允许 extra 注入额外上下文
        for key, value in record.__dict__.items():
            if key in {"args", "asctime", "created", "exc_info", "exc_text", "filename",
                       "funcName", "levelname", "levelno", "lineno", "module",
                       "msecs", "msg", "name", "pathname", "process", "processName",
                       "relativeCreated", "stack_info", "thread", "threadName",
                       "message", "taskName"}:
                continue
            payload[key] = value
        if orjson:
            return orjson.dumps(payload).decode("utf-8")
        return json.dumps(payload, ensure_ascii=False)  # type: ignore[name-defined]


def setup_logging(level: str = "INFO") -> logging.Logger:
    """初始化模块级 logger，输出结构化 JSON 到 stderr。"""
    logger = logging.getLogger("x_scraper")
    if logger.handlers:  # 幂等
        return logger
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    return logger


# ---------------------------------------------------------------------------
# JSONL I/O
# ---------------------------------------------------------------------------


def load_existing_ids(path: str | os.PathLike[str]) -> set[str]:
    """读取已有 jsonl，提取所有 tweet_id 用于 resume 去重。

    损坏行跳过不抛错，避免一行格式问题阻塞整次回溯。
    """
    p = Path(path)
    if not p.exists():
        return set()
    ids: set[str] = set()
    with p.open("rb") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                if orjson:
                    obj = orjson.loads(line)
                else:
                    obj = json.loads(line.decode("utf-8"))  # type: ignore[name-defined]
            except Exception:
                continue
            tid = obj.get("tweet_id")
            if tid:
                ids.add(str(tid))
    return ids


def write_jsonl_line(path: str | os.PathLike[str], obj: dict[str, Any]) -> None:
    """流式追加单条记录，每条 flush + fsync，避免中断丢数据。

    长回溯（万条以上）下 fsync 会拖慢吞吐；如果性能瓶颈再改成批量 flush。
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if orjson:
        data = orjson.dumps(obj) + b"\n"
    else:
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")  # type: ignore[name-defined]
    # 用 os.open 拿到 fd，确保能 fsync
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)


# ---------------------------------------------------------------------------
# 时间分片
# ---------------------------------------------------------------------------


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def month_range(since: str, until: str) -> list[tuple[str, str]]:
    """生成 [since, until] 之间逐月分片，闭区间。

    返回形如 [("2024-01-01", "2024-01-31"), ("2024-02-01", "2024-02-29"), ...]。
    第一片从 since 起算（可能不是月初），最后一片到 until 截止（可能不是月末）。
    用于绕 X 搜索 API 单 query 3200 上限：每月一个 query。
    """
    start = _parse_date(since)
    end = _parse_date(until)
    if end < start:
        raise ValueError(f"until ({until}) 必须不早于 since ({since})")

    out: list[tuple[str, str]] = []
    cur = start
    while cur <= end:
        last_day_of_month = monthrange(cur.year, cur.month)[1]
        month_end = date(cur.year, cur.month, last_day_of_month)
        slice_end = min(month_end, end)
        out.append((cur.isoformat(), slice_end.isoformat()))
        # 跳到下月 1 日
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return out


# ---------------------------------------------------------------------------
# 字段标准化
# ---------------------------------------------------------------------------


# 输出 schema 的所有字段，未提供的填默认值
_SCHEMA_DEFAULTS: dict[str, Any] = {
    "tweet_id": "",
    "url": "",
    "user": "",
    "created_at": "",
    "text": "",
    "is_retweet": False,
    "is_reply": False,
    "reply_to_user": None,
    "reply_to_tweet_id": None,
    "quoted_tweet_id": None,
    "like_count": 0,
    "retweet_count": 0,
    "reply_count": 0,
    "view_count": 0,
    "lang": "",
    "media_urls": [],
    "hashtags": [],
    "mentions": [],
    "external_urls": [],
    "source": "",
}


def _coerce_int(v: Any) -> int:
    if v is None:
        return 0
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def _coerce_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    if isinstance(v, str):
        return v.lower() in {"true", "1", "yes"}
    return bool(v)


def _to_iso_z(value: Any) -> str:
    """统一时间戳为 ISO8601 UTC（末尾 Z）。"""
    if not value:
        return ""
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        # 尝试 Apify 常见格式：'Sun May 12 10:30:00 +0000 2024' 或 ISO8601
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S%z", "%a %b %d %H:%M:%S %z %Y",
                    "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue
        else:
            # fromisoformat 兜底（Python 3.11+ 支持 Z）
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return value  # 原样返回，下游自己处理
    else:
        return str(value)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_apify(raw: dict[str, Any]) -> dict[str, Any]:
    """Apify apidojo/tweet-scraper raw item -> 标准 schema。

    字段参考 Actor 文档与实测 sample：
    https://apify.com/apidojo/tweet-scraper
    """
    author = raw.get("author") or {}
    user_name = author.get("userName") or author.get("screen_name") or ""

    tid = str(raw.get("id") or raw.get("tweetId") or raw.get("id_str") or "")
    url = raw.get("url") or raw.get("twitterUrl") or (
        f"https://x.com/{user_name}/status/{tid}" if user_name and tid else ""
    )

    # media
    media_urls: list[str] = []
    for m in (raw.get("media") or []):
        if isinstance(m, dict):
            u = m.get("media_url_https") or m.get("url") or m.get("expandedUrl")
            if u:
                media_urls.append(u)
        elif isinstance(m, str):
            media_urls.append(m)
    if not media_urls:
        for u in (raw.get("extendedEntities", {}) or {}).get("media", []) or []:
            if isinstance(u, dict) and u.get("media_url_https"):
                media_urls.append(u["media_url_https"])

    # hashtags / mentions / urls 兼容多种结构
    entities = raw.get("entities") or {}
    hashtags = [h.get("text") for h in (entities.get("hashtags") or []) if isinstance(h, dict) and h.get("text")]
    if not hashtags and raw.get("hashtags"):
        hashtags = [h for h in raw["hashtags"] if isinstance(h, str)]
    mentions = [m.get("screen_name") for m in (entities.get("user_mentions") or []) if isinstance(m, dict) and m.get("screen_name")]
    if not mentions and raw.get("mentions"):
        mentions = [m for m in raw["mentions"] if isinstance(m, str)]
    external_urls = [u.get("expanded_url") for u in (entities.get("urls") or []) if isinstance(u, dict) and u.get("expanded_url")]
    if not external_urls and raw.get("urls"):
        external_urls = [u for u in raw["urls"] if isinstance(u, str)]

    return {
        "tweet_id": tid,
        "url": url,
        "user": user_name,
        "created_at": _to_iso_z(raw.get("createdAt") or raw.get("created_at")),
        "text": raw.get("text") or raw.get("fullText") or raw.get("full_text") or "",
        "is_retweet": _coerce_bool(raw.get("isRetweet") or raw.get("retweeted")),
        "is_reply": _coerce_bool(raw.get("isReply") or raw.get("inReplyToStatusId") or raw.get("in_reply_to_status_id")),
        "reply_to_user": raw.get("inReplyToUsername") or raw.get("in_reply_to_screen_name"),
        "reply_to_tweet_id": (str(raw["inReplyToStatusId"]) if raw.get("inReplyToStatusId") else None)
        or (str(raw["in_reply_to_status_id"]) if raw.get("in_reply_to_status_id") else None),
        "quoted_tweet_id": (str(raw["quotedStatusId"]) if raw.get("quotedStatusId") else None)
        or (str(raw["quoted_status_id"]) if raw.get("quoted_status_id") else None),
        "like_count": _coerce_int(raw.get("likeCount") or raw.get("favorite_count")),
        "retweet_count": _coerce_int(raw.get("retweetCount") or raw.get("retweet_count")),
        "reply_count": _coerce_int(raw.get("replyCount") or raw.get("reply_count")),
        "view_count": _coerce_int(raw.get("viewCount") or raw.get("views")),
        "lang": raw.get("lang") or "",
        "media_urls": media_urls,
        "hashtags": hashtags,
        "mentions": mentions,
        "external_urls": external_urls,
    }


def _extract_twscrape(raw: dict[str, Any]) -> dict[str, Any]:
    """twscrape Tweet.dict() 输出 -> 标准 schema。

    twscrape 的字段命名遵循 X GraphQL 原始字段，常见键:
        id / id_str / url, user.username / user.id_str,
        date / created_at, rawContent, retweetedTweet, inReplyToTweetId,
        inReplyToUser.username, quotedTweet.id, likeCount, retweetCount,
        replyCount, viewCount, lang, media (list, dict with type/url/fullUrl),
        hashtags, mentionedUsers (list of User dict), outlinks, links.

    实测不同版本 Tweet.dict() 输出略有差异，按多个候选字段名兜底。
    """

    def pick(*keys: str, default: Any = None) -> Any:
        for k in keys:
            if k in raw and raw[k] not in (None, ""):
                return raw[k]
        return default

    # user
    user_obj = raw.get("user") or {}
    if isinstance(user_obj, dict):
        user_name = (
            user_obj.get("username")
            or user_obj.get("screen_name")
            or user_obj.get("displayname")
            or ""
        )
    else:
        user_name = str(user_obj) if user_obj else ""

    tid = str(pick("id_str", "id", "tweetId", default=""))
    url = pick("url", default="")
    if not url and user_name and tid:
        url = f"https://x.com/{user_name}/status/{tid}"

    # retweet / reply / quote flags
    retweeted = raw.get("retweetedTweet")
    is_retweet = bool(retweeted) if retweeted is not None else False

    reply_to_tid_raw = pick("inReplyToTweetId", "inReplyToStatusId", "in_reply_to_status_id")
    is_reply = bool(reply_to_tid_raw)

    reply_to_user_obj = raw.get("inReplyToUser") or {}
    if isinstance(reply_to_user_obj, dict):
        reply_to_user = (
            reply_to_user_obj.get("username")
            or reply_to_user_obj.get("screen_name")
            or None
        )
    else:
        reply_to_user = reply_to_user_obj or pick("inReplyToUsername") or None

    quoted = raw.get("quotedTweet") or {}
    if isinstance(quoted, dict):
        quoted_tid = quoted.get("id_str") or quoted.get("id")
        quoted_tweet_id = str(quoted_tid) if quoted_tid else None
    else:
        quoted_tweet_id = str(quoted) if quoted else None

    # media
    media_urls: list[str] = []
    media_field = raw.get("media") or {}
    if isinstance(media_field, dict):
        # twscrape 新版把 photos/videos/animated 拆 dict
        for category in ("photos", "videos", "animated"):
            items = media_field.get(category) or []
            for m in items:
                if isinstance(m, dict):
                    u = m.get("url") or m.get("fullUrl") or m.get("previewUrl")
                    if u:
                        media_urls.append(u)
                elif isinstance(m, str):
                    media_urls.append(m)
    elif isinstance(media_field, list):
        for m in media_field:
            if isinstance(m, dict):
                u = m.get("url") or m.get("fullUrl") or m.get("media_url_https")
                if u:
                    media_urls.append(u)
            elif isinstance(m, str):
                media_urls.append(m)

    # hashtags
    hashtags_raw = raw.get("hashtags") or []
    hashtags: list[str] = []
    for h in hashtags_raw:
        if isinstance(h, dict):
            tag = h.get("text") or h.get("tag")
            if tag:
                hashtags.append(tag)
        elif isinstance(h, str):
            hashtags.append(h.lstrip("#"))

    # mentions
    mentions_raw = raw.get("mentionedUsers") or raw.get("mentions") or []
    mentions: list[str] = []
    for m in mentions_raw:
        if isinstance(m, dict):
            name = m.get("username") or m.get("screen_name")
            if name:
                mentions.append(name)
        elif isinstance(m, str):
            mentions.append(m.lstrip("@"))

    # outlinks / external urls
    external_urls: list[str] = []
    for key in ("outlinks", "links", "external_urls"):
        val = raw.get(key) or []
        if isinstance(val, list):
            for u in val:
                if isinstance(u, dict):
                    eu = u.get("expandedUrl") or u.get("expanded_url") or u.get("url")
                    if eu:
                        external_urls.append(eu)
                elif isinstance(u, str) and u:
                    external_urls.append(u)
        if external_urls:
            break

    return {
        "tweet_id": tid,
        "url": url,
        "user": user_name,
        "created_at": _to_iso_z(pick("date", "created_at", "createdAt")),
        "text": pick("rawContent", "text", "fullText", "full_text", default=""),
        "is_retweet": is_retweet,
        "is_reply": is_reply,
        "reply_to_user": reply_to_user,
        "reply_to_tweet_id": (str(reply_to_tid_raw) if reply_to_tid_raw else None),
        "quoted_tweet_id": quoted_tweet_id,
        "like_count": _coerce_int(pick("likeCount", "favorite_count")),
        "retweet_count": _coerce_int(pick("retweetCount", "retweet_count")),
        "reply_count": _coerce_int(pick("replyCount", "reply_count")),
        "view_count": _coerce_int(pick("viewCount", "views", "view_count")),
        "lang": pick("lang", "language", default=""),
        "media_urls": media_urls,
        "hashtags": hashtags,
        "mentions": mentions,
        "external_urls": external_urls,
    }


def _extract_scweet(raw: dict[str, Any]) -> dict[str, Any]:
    """Scweet 返回字典 -> 标准 schema。

    Scweet v5 输出字段名以列形式存在（与 DataFrame 行同构），常见键：
    UserScreenName, Timestamp, Text, Likes, Retweets, Comments, Tweet URL,
    Tweet ID, Emojis, Image url, Embedded_text, ...
    不同版本字段大小写有变化，做容错匹配。
    """

    def pick(*keys: str, default: Any = None) -> Any:
        for k in keys:
            if k in raw and raw[k] not in (None, ""):
                return raw[k]
        return default

    text = pick("Text", "text", "Embedded_text", "embedded_text", default="")
    user_name = pick("UserScreenName", "username", "user", "screen_name", default="")
    if isinstance(user_name, str):
        user_name = user_name.lstrip("@")

    tid = str(pick("Tweet ID", "tweet_id", "id", default=""))
    url = pick("Tweet URL", "url", "tweet_url", default="")
    if not url and user_name and tid:
        url = f"https://x.com/{user_name}/status/{tid}"

    media_field = pick("Image url", "image_url", "media", default=[])
    if isinstance(media_field, str):
        media_urls = [m for m in media_field.split(",") if m.strip()]
    elif isinstance(media_field, list):
        media_urls = [str(m) for m in media_field if m]
    else:
        media_urls = []

    # hashtags / mentions：Scweet 通常不结构化，从 text 兜底解析
    text_str = str(text or "")
    hashtags = [w[1:] for w in text_str.split() if w.startswith("#") and len(w) > 1]
    mentions = [w[1:] for w in text_str.split() if w.startswith("@") and len(w) > 1]

    return {
        "tweet_id": tid,
        "url": url or "",
        "user": user_name or "",
        "created_at": _to_iso_z(pick("Timestamp", "timestamp", "created_at", "date")),
        "text": text_str,
        "is_retweet": _coerce_bool(pick("isRetweet", "is_retweet", default=False)),
        "is_reply": _coerce_bool(pick("isReply", "is_reply", default=False)),
        "reply_to_user": pick("reply_to_user", "in_reply_to_screen_name"),
        "reply_to_tweet_id": (str(pick("reply_to_tweet_id", "in_reply_to_status_id")) if pick("reply_to_tweet_id", "in_reply_to_status_id") else None),
        "quoted_tweet_id": (str(pick("quoted_tweet_id", "quoted_status_id")) if pick("quoted_tweet_id", "quoted_status_id") else None),
        "like_count": _coerce_int(pick("Likes", "likes", "favorite_count")),
        "retweet_count": _coerce_int(pick("Retweets", "retweets", "retweet_count")),
        "reply_count": _coerce_int(pick("Comments", "comments", "reply_count")),
        "view_count": _coerce_int(pick("Views", "views", "view_count")),
        "lang": pick("lang", "language", default=""),
        "media_urls": media_urls,
        "hashtags": hashtags,
        "mentions": mentions,
        "external_urls": [],
    }


def normalize_tweet(raw: dict[str, Any], source: str) -> dict[str, Any]:
    """把不同源的 raw item 映射成统一 schema。

    source: "apify" | "scweet" | "twscrape"。未知源走 apify 分支（字段名相似）。
    """
    if source == "scweet":
        out = _extract_scweet(raw)
    elif source == "twscrape":
        out = _extract_twscrape(raw)
    else:
        out = _extract_apify(raw)

    # 用 defaults 补齐缺失字段，保证 schema 完整
    merged = {**_SCHEMA_DEFAULTS, **out}
    merged["source"] = source
    return merged


def normalize_twscrape(raw: dict[str, Any]) -> dict[str, Any]:
    """便捷封装：把 twscrape 的 Tweet 对象（或 .dict()）映射到统一 jsonl schema。

    支持传 Tweet 对象（自动调用 .dict()）或已经是 dict 的输入。
    """
    if hasattr(raw, "dict") and callable(raw.dict):
        raw = raw.dict()
    if not isinstance(raw, dict):
        raise TypeError(
            f"normalize_twscrape 期望 dict 或 Tweet 对象，得到 {type(raw).__name__}"
        )
    return normalize_tweet(raw, "twscrape")


# ---------------------------------------------------------------------------
# 简单工具
# ---------------------------------------------------------------------------


def iter_unique(items: Iterable[dict[str, Any]], seen: set[str]) -> Iterable[dict[str, Any]]:
    """按 tweet_id 去重的生成器；seen 是外部传入的累积集合（in-place 更新）。"""
    for it in items:
        tid = it.get("tweet_id")
        if not tid or tid in seen:
            continue
        seen.add(tid)
        yield it


# ---------------------------------------------------------------------------
# 自检（不写单测文件，靠 __main__ 块）
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    # month_range 边界自检
    r1 = month_range("2024-01-15", "2024-03-10")
    assert r1 == [
        ("2024-01-15", "2024-01-31"),
        ("2024-02-01", "2024-02-29"),
        ("2024-03-01", "2024-03-10"),
    ], r1

    r2 = month_range("2024-05-01", "2024-05-01")
    assert r2 == [("2024-05-01", "2024-05-01")], r2

    r3 = month_range("2023-12-20", "2024-01-05")
    assert r3 == [
        ("2023-12-20", "2023-12-31"),
        ("2024-01-01", "2024-01-05"),
    ], r3

    try:
        month_range("2024-05-10", "2024-05-01")
    except ValueError:
        pass
    else:
        raise AssertionError("应抛 ValueError")

    # normalize_tweet apify 路径
    sample_apify = {
        "id": "1789012345",
        "url": "https://x.com/foo/status/1789012345",
        "author": {"userName": "foo"},
        "createdAt": "2024-05-12T10:30:00.000Z",
        "text": "hello #btc @bar",
        "likeCount": 100,
        "retweetCount": 20,
        "replyCount": 5,
        "viewCount": 5000,
        "lang": "en",
        "isRetweet": False,
        "isReply": False,
        "entities": {
            "hashtags": [{"text": "btc"}],
            "user_mentions": [{"screen_name": "bar"}],
            "urls": [],
        },
    }
    n = normalize_tweet(sample_apify, "apify")
    assert n["tweet_id"] == "1789012345"
    assert n["user"] == "foo"
    assert n["created_at"] == "2024-05-12T10:30:00Z"
    assert n["like_count"] == 100
    assert n["hashtags"] == ["btc"]
    assert n["mentions"] == ["bar"]
    assert n["source"] == "apify"

    # scweet 路径
    sample_scweet = {
        "UserScreenName": "@foo",
        "Timestamp": "2024-05-12T10:30:00+00:00",
        "Text": "hello #btc @bar",
        "Likes": "100",
        "Retweets": "20",
        "Comments": "5",
        "Tweet ID": "1789012345",
        "Tweet URL": "https://x.com/foo/status/1789012345",
    }
    n2 = normalize_tweet(sample_scweet, "scweet")
    assert n2["tweet_id"] == "1789012345"
    assert n2["user"] == "foo"
    assert n2["like_count"] == 100
    assert n2["source"] == "scweet"
    assert "btc" in n2["hashtags"]

    # twscrape 路径
    sample_twscrape = {
        "id": 1789012345,
        "id_str": "1789012345",
        "url": "https://x.com/foo/status/1789012345",
        "user": {"username": "foo", "id_str": "111"},
        "date": "2024-05-12T10:30:00+00:00",
        "rawContent": "hello #btc @bar https://example.com",
        "retweetedTweet": None,
        "inReplyToTweetId": None,
        "quotedTweet": None,
        "likeCount": 100,
        "retweetCount": 20,
        "replyCount": 5,
        "viewCount": 5000,
        "lang": "en",
        "media": {"photos": [{"url": "https://pbs.twimg.com/media/abc.jpg"}]},
        "hashtags": [{"text": "btc"}],
        "mentionedUsers": [{"username": "bar"}],
        "outlinks": ["https://example.com"],
    }
    n3 = normalize_tweet(sample_twscrape, "twscrape")
    assert n3["tweet_id"] == "1789012345", n3
    assert n3["user"] == "foo", n3
    assert n3["created_at"] == "2024-05-12T10:30:00Z", n3["created_at"]
    assert n3["like_count"] == 100
    assert n3["hashtags"] == ["btc"]
    assert n3["mentions"] == ["bar"]
    assert n3["external_urls"] == ["https://example.com"]
    assert n3["media_urls"] == ["https://pbs.twimg.com/media/abc.jpg"]
    assert n3["is_retweet"] is False
    assert n3["is_reply"] is False
    assert n3["source"] == "twscrape"

    # twscrape 便捷封装：传 dict
    n4 = normalize_twscrape(sample_twscrape)
    assert n4["source"] == "twscrape"
    assert n4["tweet_id"] == "1789012345"

    # twscrape reply 情况
    sample_reply = {
        "id_str": "999",
        "user": {"username": "foo"},
        "date": "2024-06-01T00:00:00Z",
        "rawContent": "reply text",
        "inReplyToTweetId": 1234,
        "inReplyToUser": {"username": "alice"},
        "likeCount": 0,
        "retweetCount": 0,
        "replyCount": 0,
        "viewCount": 0,
        "lang": "en",
    }
    n5 = normalize_tweet(sample_reply, "twscrape")
    assert n5["is_reply"] is True
    assert n5["reply_to_tweet_id"] == "1234"
    assert n5["reply_to_user"] == "alice"

    print("[_common.py] self-check passed")
