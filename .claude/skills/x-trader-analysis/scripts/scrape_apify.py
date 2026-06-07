"""Apify apidojo/tweet-scraper 主方案：按月分片回溯单用户推文。

用法示例:
    python scrape_apify.py --user ShanghaoJin --since 2023-01-01 \
        --until 2026-05-17 --max 5000 --out data/raw/ShanghaoJin.jsonl

依赖:
    apify-client (运行时), rich (进度条), orjson (项目已有)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# 允许以脚本直接运行 (python scrape_apify.py) 也能 import 同目录 _common
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    iter_unique,
    load_existing_ids,
    month_range,
    normalize_tweet,
    setup_logging,
    write_jsonl_line,
)

ACTOR_ID = "apidojo/tweet-scraper"
APIFY_CONSOLE_URL = "https://console.apify.com"
DEFAULT_MAX = 10000


def _build_search_term(
    user: str,
    since: str,
    until: str,
    include_replies: bool,
    include_retweets: bool,
) -> str:
    """构造单月 search query。

    X 高级搜索语法：from:user since:YYYY-MM-DD until:YYYY-MM-DD
    默认排除回复与转推（精度高的"博主原创时间线"）。
    """
    parts = [f"from:{user}", f"since:{since}", f"until:{until}"]
    if not include_replies:
        parts.append("-filter:replies")
    if not include_retweets:
        # X 搜索语法对 -filter:retweets 支持不稳，附加 -filter:nativeretweets 兜底
        parts.append("-filter:nativeretweets")
    return " ".join(parts)


def _plan_chunks(
    user: str,
    since: str | None,
    until: str | None,
    include_replies: bool,
    include_retweets: bool,
) -> list[dict]:
    """生成 Apify Actor 调用计划。

    无 since/until 时退化为单 query（让 Actor 按相关性/最新拉），
    通常仅用于小批量探查；万条级回溯必须给定时间区间。
    """
    if since and until:
        slices = month_range(since, until)
    elif since or until:
        # 缺一端按 "最近 3 年" / "至今" 推导，让用户显式指定更稳
        raise SystemExit("错误：--since 与 --until 必须同时提供，或都不提供。")
    else:
        slices = []  # 单 query 模式

    if not slices:
        return [{
            "term": f"from:{user}"
                    + (" -filter:replies" if not include_replies else "")
                    + (" -filter:nativeretweets" if not include_retweets else ""),
            "since": None,
            "until": None,
        }]

    return [
        {
            "term": _build_search_term(user, s, e, include_replies, include_retweets),
            "since": s,
            "until": e,
        }
        for s, e in slices
    ]


def _run_actor(client, run_input: dict):
    """封装 Actor 调用，集中处理 SDK 调用细节，方便 dry-run mock。"""
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if not run or "defaultDatasetId" not in run:
        raise RuntimeError(f"Apify Actor 返回异常：{run}")
    return client.dataset(run["defaultDatasetId"]).iterate_items()


def run(args: argparse.Namespace) -> int:
    logger = setup_logging()

    chunks = _plan_chunks(
        user=args.user,
        since=args.since,
        until=args.until,
        include_replies=args.include_replies,
        include_retweets=args.include_retweets,
    )

    logger.info(
        "scrape_apify 计划生成",
        extra={
            "user": args.user,
            "chunks": len(chunks),
            "since": args.since,
            "until": args.until,
            "max": args.max,
            "out": args.out,
            "include_replies": args.include_replies,
            "include_retweets": args.include_retweets,
            "resume": args.resume,
        },
    )

    if args.dry_run:
        print(f"[DRY-RUN] 用户: {args.user}")
        print(f"[DRY-RUN] 时间区间: {args.since or '不限'} -> {args.until or '不限'}")
        print(f"[DRY-RUN] 最大条数: {args.max}")
        print(f"[DRY-RUN] 输出文件: {args.out}")
        print(f"[DRY-RUN] 包含回复: {args.include_replies}  包含转推: {args.include_retweets}")
        print(f"[DRY-RUN] 续抓模式: {args.resume}")
        print(f"[DRY-RUN] 计划分片数（按月）: {len(chunks)}")
        for i, ch in enumerate(chunks[:5], 1):
            print(f"[DRY-RUN]   分片 {i}: {ch['term']}")
        if len(chunks) > 5:
            print(f"[DRY-RUN]   ... 还有 {len(chunks) - 5} 个分片")
        if args.resume:
            existing = load_existing_ids(args.out)
            print(f"[DRY-RUN] 续抓将跳过已有 tweet_id 数量: {len(existing)}")
        print("[DRY-RUN] 未实际调用 Apify，token 校验已跳过。")
        return 0

    # 真跑：校验 token
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        logger.error("缺少环境变量 APIFY_TOKEN")
        print(
            "错误：未设置环境变量 APIFY_TOKEN。\n"
            f"请到 {APIFY_CONSOLE_URL} 注册账号、获取 API token，并执行：\n"
            "  export APIFY_TOKEN=apify_api_xxx",
            file=sys.stderr,
        )
        return 2

    # 延迟 import，避免 dry-run 强制依赖
    try:
        from apify_client import ApifyClient
    except ImportError:
        logger.error("缺少 apify-client 依赖")
        print(
            "错误：未安装 apify-client。请执行：\n"
            "  uv pip install apify-client",
            file=sys.stderr,
        )
        return 3

    try:
        from rich.progress import (
            BarColumn,
            MofNCompleteColumn,
            Progress,
            TextColumn,
            TimeElapsedColumn,
        )
    except ImportError:
        logger.error("缺少 rich 依赖")
        print("错误：未安装 rich。请执行：\n  uv pip install rich", file=sys.stderr)
        return 3

    client = ApifyClient(token)

    seen: set[str] = load_existing_ids(args.out) if args.resume else set()
    if args.resume:
        logger.info("续抓模式已加载已有 ID", extra={"existing": len(seen)})

    collected = 0
    target_max = max(1, args.max)

    progress = Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("[yellow]{task.fields[term]}"),
        TimeElapsedColumn(),
    )

    with progress:
        task = progress.add_task(
            "Apify 抓取中", total=len(chunks), term=""
        )
        for idx, ch in enumerate(chunks, 1):
            progress.update(task, term=ch["term"][:60])
            remaining = target_max - collected
            if remaining <= 0:
                logger.info("已达 --max 上限，提前停止", extra={"collected": collected})
                break

            # 每片留点余量，避免 Actor 多还少要
            chunk_max = min(remaining + 50, 3200)
            run_input = {
                "searchTerms": [ch["term"]],
                "tweetLanguage": "any",
                "maxItems": chunk_max,
                "includeSearchTerms": True,
                "sort": "Latest",
            }

            try:
                items_iter = _run_actor(client, run_input)
            except Exception as exc:
                logger.exception(
                    "Apify Actor 调用失败，跳过此分片",
                    extra={"chunk_index": idx, "term": ch["term"]},
                )
                progress.advance(task)
                continue

            normalized = (
                normalize_tweet(raw, "apify")
                for raw in items_iter
                if isinstance(raw, dict)
            )
            written_in_chunk = 0
            for tweet in iter_unique(normalized, seen):
                # 区间硬过滤：Actor 偶尔越界，按 created_at 兜底
                if ch["since"] and ch["until"] and tweet["created_at"]:
                    date_part = tweet["created_at"][:10]
                    if date_part < ch["since"] or date_part > ch["until"]:
                        continue
                # 跳过用户错配（避免 from: 语法被忽略）
                if tweet["user"] and tweet["user"].lower() != args.user.lower():
                    continue

                write_jsonl_line(args.out, tweet)
                collected += 1
                written_in_chunk += 1
                if collected >= target_max:
                    break

            logger.info(
                "分片完成",
                extra={
                    "chunk_index": idx,
                    "term": ch["term"],
                    "written": written_in_chunk,
                    "collected_total": collected,
                },
            )
            progress.advance(task)

    logger.info("抓取结束", extra={"collected": collected, "out": args.out})
    print(f"完成：累计写入 {collected} 条到 {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Apify apidojo/tweet-scraper 主方案：单用户深度历史回溯",
    )
    p.add_argument("--user", required=True, help="博主 handle（不含 @）")
    p.add_argument("--since", help="起始日期 YYYY-MM-DD")
    p.add_argument("--until", help="结束日期 YYYY-MM-DD")
    p.add_argument("--max", type=int, default=DEFAULT_MAX, help="最大条数，默认 10000")
    p.add_argument("--out", required=True, help="输出 jsonl 路径")
    p.add_argument("--include-replies", action="store_true", help="包含回复推文")
    p.add_argument("--include-retweets", action="store_true", help="包含转推")
    p.add_argument("--resume", action="store_true", help="从已有 jsonl 续抓，去重 tweet_id")
    p.add_argument("--dry-run", action="store_true", help="只打印计划，不调用 API")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
