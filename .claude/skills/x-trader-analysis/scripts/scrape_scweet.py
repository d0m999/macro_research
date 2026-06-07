"""Scweet 备用方案：用 cookies.json 抓单博主时间线 + 按月搜索补漏。

用法示例:
    python scrape_scweet.py --user ShanghaoJin --since 2023-01-01 \
        --until 2026-05-17 --max 5000 --out data/raw/ShanghaoJin.jsonl \
        --cookies cookies.json

依赖:
    Scweet>=5.0 (运行时), rich (进度条), orjson (项目已有)

cookies.json 示例（从浏览器 DevTools 复制）:
    {"auth_token": "xxx", "ct0": "xxx"}
    或 Scweet 兼容的 cookie 列表格式。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    iter_unique,
    load_existing_ids,
    month_range,
    normalize_tweet,
    setup_logging,
    write_jsonl_line,
)

DEFAULT_MAX = 10000
SCWEET_GUIDE_URL = "https://github.com/Altimis/Scweet"


def _validate_cookies(path: str) -> tuple[bool, str]:
    """轻量校验 cookies 文件。返回 (是否合法, 描述信息)。"""
    p = Path(path)
    if not p.exists():
        return False, f"cookies 文件不存在：{path}"
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        return False, f"cookies 文件解析失败：{exc}"

    # 支持两种格式：{auth_token, ct0} 或 cookie 列表
    if isinstance(data, dict):
        if data.get("auth_token") and data.get("ct0"):
            return True, "auth_token + ct0 (dict)"
        return False, "cookies dict 缺少 auth_token / ct0 字段"
    if isinstance(data, list):
        names = {c.get("name") for c in data if isinstance(c, dict)}
        if {"auth_token", "ct0"}.issubset(names):
            return True, "auth_token + ct0 (list)"
        return False, "cookies list 缺少 auth_token / ct0"
    return False, "cookies 格式未知（既非 dict 也非 list）"


def _plan(args: argparse.Namespace) -> dict:
    """生成抓取计划：profile 时间线 + 可选的月分片搜索。"""
    chunks = []
    if args.since and args.until:
        chunks = month_range(args.since, args.until)
    elif args.since or args.until:
        raise SystemExit("错误：--since 与 --until 必须同时提供。")

    return {
        "profile_pass": True,  # 先拉时间线
        "search_passes": chunks,  # 超过 3200 时用按月搜索补
        "search_term_template": f"from:{args.user}",
    }


def run(args: argparse.Namespace) -> int:
    logger = setup_logging()
    plan = _plan(args)

    logger.info(
        "scrape_scweet 计划生成",
        extra={
            "user": args.user,
            "cookies": args.cookies,
            "since": args.since,
            "until": args.until,
            "max": args.max,
            "out": args.out,
            "profile_pass": plan["profile_pass"],
            "search_passes": len(plan["search_passes"]),
            "include_replies": args.include_replies,
            "include_retweets": args.include_retweets,
            "resume": args.resume,
        },
    )

    if args.dry_run:
        print(f"[DRY-RUN] 用户: {args.user}")
        print(f"[DRY-RUN] cookies: {args.cookies}")
        print(f"[DRY-RUN] 时间区间: {args.since or '不限'} -> {args.until or '不限'}")
        print(f"[DRY-RUN] 最大条数: {args.max}")
        print(f"[DRY-RUN] 输出文件: {args.out}")
        print(f"[DRY-RUN] 包含回复: {args.include_replies}  包含转推: {args.include_retweets}")
        print(f"[DRY-RUN] 续抓模式: {args.resume}")
        print(f"[DRY-RUN] 第一步: profile_tweets 抓时间线（受 3200 上限）")
        print(f"[DRY-RUN] 第二步: 按月搜索补漏，共 {len(plan['search_passes'])} 个分片")
        for i, (s, e) in enumerate(plan["search_passes"][:5], 1):
            print(f"[DRY-RUN]   分片 {i}: {plan['search_term_template']} since:{s} until:{e}")
        if len(plan["search_passes"]) > 5:
            print(f"[DRY-RUN]   ... 还有 {len(plan['search_passes']) - 5} 个分片")

        ok, msg = _validate_cookies(args.cookies)
        print(f"[DRY-RUN] cookies 校验: {'OK' if ok else 'FAIL'} ({msg})")
        if args.resume:
            existing = load_existing_ids(args.out)
            print(f"[DRY-RUN] 续抓将跳过已有 tweet_id 数量: {len(existing)}")
        print("[DRY-RUN] 未实际启动 Scweet。")
        return 0

    # 真跑路径
    ok, msg = _validate_cookies(args.cookies)
    if not ok:
        logger.error("cookies 校验失败", extra={"reason": msg})
        print(
            f"错误：cookies 校验失败 — {msg}\n"
            f"请参考 {SCWEET_GUIDE_URL} 准备 cookies.json，至少包含 auth_token 与 ct0。",
            file=sys.stderr,
        )
        return 2

    try:
        from Scweet.scweet import Scweet  # type: ignore
    except ImportError:
        logger.error("缺少 Scweet 依赖")
        print(
            "错误：未安装 Scweet。请执行：\n  uv pip install 'Scweet>=5.0'",
            file=sys.stderr,
        )
        return 3

    try:
        from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    except ImportError:
        print("错误：未安装 rich。请执行：\n  uv pip install rich", file=sys.stderr)
        return 3

    seen: set[str] = load_existing_ids(args.out) if args.resume else set()
    if args.resume:
        logger.info("续抓已加载 ID", extra={"existing": len(seen)})

    s = Scweet(cookies_file=args.cookies)
    target_max = max(1, args.max)
    collected = 0

    def _emit(records: list[dict] | None, *, source_label: str) -> int:
        """归一化 + 去重写入。返回本批写入数。"""
        nonlocal collected
        if not records:
            return 0
        normalized = (normalize_tweet(r, "scweet") for r in records if isinstance(r, dict))
        written = 0
        for tweet in iter_unique(normalized, seen):
            if tweet["user"] and tweet["user"].lower() != args.user.lower():
                continue
            if not args.include_replies and tweet["is_reply"]:
                continue
            if not args.include_retweets and tweet["is_retweet"]:
                continue
            write_jsonl_line(args.out, tweet)
            collected += 1
            written += 1
            if collected >= target_max:
                break
        logger.info(
            "Scweet 批次写入",
            extra={"source_label": source_label, "written": written, "collected_total": collected},
        )
        return written

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        TextColumn("[yellow]{task.fields[stage]}"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task("Scweet 抓取中", stage="profile_tweets", total=None)

        # 第一步：profile_tweets 抓时间线
        try:
            profile_rows = s.get_profile_tweets(
                handles=[args.user],
                limit=min(target_max, 3200),
                save_path=None,
            )
            # Scweet 可能返回 DataFrame，统一转 list[dict]
            if hasattr(profile_rows, "to_dict"):
                profile_rows = profile_rows.to_dict(orient="records")
        except Exception:
            logger.exception("profile_tweets 抓取失败")
            profile_rows = []

        _emit(profile_rows or [], source_label="profile")

        # 第二步：按月搜索补漏（仅当指定 since/until 且未到上限）
        if plan["search_passes"] and collected < target_max:
            for s_date, e_date in plan["search_passes"]:
                if collected >= target_max:
                    break
                progress.update(task, stage=f"search {s_date}~{e_date}")
                term_parts = [f"from:{args.user}"]
                if not args.include_replies:
                    term_parts.append("-filter:replies")
                if not args.include_retweets:
                    term_parts.append("-filter:nativeretweets")
                term = " ".join(term_parts)

                try:
                    rows = s.search(
                        term,
                        since=s_date,
                        until=e_date,
                        limit=target_max - collected,
                    )
                    if hasattr(rows, "to_dict"):
                        rows = rows.to_dict(orient="records")
                except Exception:
                    logger.exception(
                        "Scweet search 分片失败",
                        extra={"since": s_date, "until": e_date},
                    )
                    continue

                _emit(rows or [], source_label=f"search:{s_date}")

    logger.info("抓取结束", extra={"collected": collected, "out": args.out})
    print(f"完成：累计写入 {collected} 条到 {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Scweet 备用方案：cookies + profile 时间线 + 按月搜索补漏",
    )
    p.add_argument("--user", required=True, help="博主 handle（不含 @）")
    p.add_argument("--since", help="起始日期 YYYY-MM-DD")
    p.add_argument("--until", help="结束日期 YYYY-MM-DD")
    p.add_argument("--max", type=int, default=DEFAULT_MAX, help="最大条数，默认 10000")
    p.add_argument("--out", required=True, help="输出 jsonl 路径")
    p.add_argument(
        "--cookies",
        default="cookies.json",
        help="cookies.json 路径（含 auth_token / ct0）",
    )
    p.add_argument("--include-replies", action="store_true", help="包含回复推文")
    p.add_argument("--include-retweets", action="store_true", help="包含转推")
    p.add_argument("--resume", action="store_true", help="从已有 jsonl 续抓，去重 tweet_id")
    p.add_argument("--dry-run", action="store_true", help="只打印计划，不调用 Scweet")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
