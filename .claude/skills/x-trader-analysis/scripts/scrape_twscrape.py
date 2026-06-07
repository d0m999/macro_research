"""twscrape 主力方案：账号池 + 按月分片抓取单博主历史。

是 X Trader Analysis skill 的**常态化推荐爬虫**。
零边际成本，账号池由 twscrape 自动轮换。

用法示例:
    python scrape_twscrape.py --user ShanghaoJin --since 2023-01-01 \\
        --until 2026-05-17 --max 10000 --out data/raw/ShanghaoJin.jsonl

依赖:
    twscrape>=0.17.0 (运行时), rich (进度条), orjson (项目已有)
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys
from pathlib import Path
from typing import Any

# 允许以脚本直接运行 (python scrape_twscrape.py) 也能 import 同目录 _common
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
# scripts/ -> x-trader-analysis/ -> .account_pool/accounts.db
DEFAULT_DB = Path(__file__).resolve().parents[1] / ".account_pool" / "accounts.db"

# 分片间随机休眠区间（秒），降低被识别为机器流量的概率
SLEEP_MIN = 5.0
SLEEP_MAX = 15.0


def _build_search_term(
    user: str,
    since: str,
    until: str,
    include_replies: bool,
    include_retweets: bool,
) -> str:
    """构造 X 高级搜索语法：from:user since:YYYY-MM-DD until:YYYY-MM-DD。

    默认排除回复与转推（关注博主原创时间线）。
    """
    parts = [f"from:{user}", f"since:{since}", f"until:{until}"]
    if not include_replies:
        parts.append("-filter:replies")
    if not include_retweets:
        parts.append("-filter:nativeretweets")
    return " ".join(parts)


def _plan_chunks(
    user: str,
    since: str | None,
    until: str | None,
    include_replies: bool,
    include_retweets: bool,
) -> list[dict[str, Any]]:
    """生成调用计划。

    必须提供 since/until 配对（要么都给要么都不给）。
    不给时退化为单 query（仅小批量探查用）。
    """
    if since and until:
        slices = month_range(since, until)
    elif since or until:
        raise SystemExit("错误：--since 与 --until 必须同时提供，或都不提供。")
    else:
        slices = []

    if not slices:
        term = f"from:{user}"
        if not include_replies:
            term += " -filter:replies"
        if not include_retweets:
            term += " -filter:nativeretweets"
        return [{"term": term, "since": None, "until": None}]

    return [
        {
            "term": _build_search_term(user, s, e, include_replies, include_retweets),
            "since": s,
            "until": e,
        }
        for s, e in slices
    ]


async def _ensure_pool_has_accounts(api: Any, logger: Any, db_path: Path) -> bool:
    """启动前自检账号池非空。"""
    accounts: list[Any] = []
    for getter_name in ("accounts_info", "get_all", "all"):
        getter = getattr(api.pool, getter_name, None)
        if getter is None:
            continue
        try:
            res = getter()
            if asyncio.iscoroutine(res):
                accounts = await res  # type: ignore[assignment]
            else:
                accounts = res  # type: ignore[assignment]
            if accounts is not None:
                break
        except Exception:
            logger.exception(
                "账号池列举接口异常", extra={"getter": getter_name}
            )
            continue

    if not accounts:
        print(
            f"错误：账号池为空 ({db_path})。\n"
            "请先添加至少 1 个 X 小号:\n"
            "  python scripts/account_pool/add_account.py --username u1 \\\n"
            '    --cookies "auth_token=xxx; ct0=yyy"\n'
            "更多说明: .claude/skills/x-trader-analysis/scripts/account_pool/README.md",
            file=sys.stderr,
        )
        return False

    # 检查至少有一个 active
    has_active = False
    for acc in accounts:
        if isinstance(acc, dict):
            if acc.get("active") and acc.get("logged_in"):
                has_active = True
                break
        else:
            if getattr(acc, "active", False) and getattr(acc, "logged_in", False):
                has_active = True
                break

    if not has_active:
        print(
            "错误：账号池中没有 active + logged_in 的账号。\n"
            "请运行: make account-health  查看具体状态。\n"
            "若 cookies 过期，请用 add_account.py 重新导入 cookies（同 username 会覆盖）。",
            file=sys.stderr,
        )
        return False

    logger.info("账号池可用", extra={"total_accounts": len(accounts), "db": str(db_path)})
    return True


async def _run_async(args: argparse.Namespace) -> int:
    logger = setup_logging()
    chunks = _plan_chunks(
        user=args.user,
        since=args.since,
        until=args.until,
        include_replies=args.include_replies,
        include_retweets=args.include_retweets,
    )

    logger.info(
        "scrape_twscrape 计划生成",
        extra={
            "user": args.user,
            "chunks": len(chunks),
            "since": args.since,
            "until": args.until,
            "max": args.max,
            "out": args.out,
            "db": args.db,
            "include_replies": args.include_replies,
            "include_retweets": args.include_retweets,
            "resume": args.resume,
        },
    )

    db_path = Path(args.db).expanduser().resolve()

    # ----- dry-run -----
    if args.dry_run:
        print(f"[DRY-RUN] 用户: {args.user}")
        print(f"[DRY-RUN] 账号池 DB: {db_path}")
        print(f"[DRY-RUN] 时间区间: {args.since or '不限'} -> {args.until or '不限'}")
        print(f"[DRY-RUN] 最大条数: {args.max}")
        print(f"[DRY-RUN] 输出文件: {args.out}")
        print(
            f"[DRY-RUN] 包含回复: {args.include_replies}  包含转推: {args.include_retweets}"
        )
        print(f"[DRY-RUN] 续抓模式: {args.resume}")
        print(f"[DRY-RUN] 计划分片数（按月）: {len(chunks)}")
        for i, ch in enumerate(chunks[:5], 1):
            print(f"[DRY-RUN]   分片 {i}: {ch['term']}")
        if len(chunks) > 5:
            print(f"[DRY-RUN]   ... 还有 {len(chunks) - 5} 个分片")
        print(f"[DRY-RUN] 分片间隔: 随机 {SLEEP_MIN}-{SLEEP_MAX}s")
        if args.resume:
            existing = load_existing_ids(args.out)
            print(f"[DRY-RUN] 续抓将跳过已有 tweet_id 数量: {len(existing)}")
        print("[DRY-RUN] 未实际调用 twscrape，账号池校验已跳过。")
        return 0

    # ----- 真跑：延迟 import twscrape -----
    try:
        from twscrape import API
    except ImportError:
        logger.error("缺少 twscrape 依赖")
        print(
            "错误：未安装 twscrape。请执行：\n  uv pip install 'twscrape>=0.17.0'",
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

    if not db_path.exists():
        print(
            f"错误：账号池 DB 不存在: {db_path}\n"
            "请先添加账号:\n"
            "  python scripts/account_pool/add_account.py --username u1 \\\n"
            '    --cookies "auth_token=xxx; ct0=yyy"',
            file=sys.stderr,
        )
        return 2

    api = API(str(db_path))

    if not await _ensure_pool_has_accounts(api, logger, db_path):
        return 2

    seen: set[str] = load_existing_ids(args.out) if args.resume else set()
    if args.resume:
        logger.info("续抓模式已加载已有 ID", extra={"existing": len(seen)})

    collected = 0
    target_max = max(1, args.max)

    progress = Progress(
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("[yellow]片={task.fields[term]}"),
        TextColumn("[green]累计={task.fields[collected]}"),
        TimeElapsedColumn(),
    )

    with progress:
        task = progress.add_task(
            "twscrape 抓取中",
            total=len(chunks),
            term="",
            collected=0,
        )

        for idx, ch in enumerate(chunks, 1):
            progress.update(task, term=ch["term"][:60])
            remaining = target_max - collected
            if remaining <= 0:
                logger.info(
                    "已达 --max 上限，提前停止", extra={"collected": collected}
                )
                break

            # 每月最多搜 chunk_max 条；twscrape 自己会分页 + 自动换号
            chunk_max = min(remaining + 50, 3200)
            written_in_chunk = 0

            try:
                async for tweet in api.search(ch["term"], limit=chunk_max):
                    # 转成 dict 后走统一 normalize_tweet
                    if hasattr(tweet, "dict") and callable(tweet.dict):
                        raw = tweet.dict()
                    elif isinstance(tweet, dict):
                        raw = tweet
                    else:
                        # 退化处理：直接拿属性
                        raw = {
                            "id_str": getattr(tweet, "id_str", None)
                            or getattr(tweet, "id", None),
                            "user": {
                                "username": getattr(
                                    getattr(tweet, "user", None), "username", ""
                                )
                            },
                            "date": getattr(tweet, "date", None),
                            "rawContent": getattr(tweet, "rawContent", ""),
                        }

                    normalized = normalize_tweet(raw, "twscrape")

                    # 去重 + 用户校验 + 区间硬过滤
                    tid = normalized.get("tweet_id")
                    if not tid or tid in seen:
                        continue
                    if (
                        normalized["user"]
                        and normalized["user"].lower() != args.user.lower()
                    ):
                        # 偶尔 from: 语法被忽略，硬过滤
                        continue
                    if ch["since"] and ch["until"] and normalized["created_at"]:
                        date_part = normalized["created_at"][:10]
                        if date_part < ch["since"] or date_part > ch["until"]:
                            continue

                    seen.add(tid)
                    write_jsonl_line(args.out, normalized)
                    collected += 1
                    written_in_chunk += 1
                    progress.update(task, collected=collected)
                    if collected >= target_max:
                        break
            except KeyboardInterrupt:
                logger.warning("用户中断")
                print(
                    f"\n用户中断，已写入 {collected} 条到 {args.out}（可用 --resume 续抓）",
                    file=sys.stderr,
                )
                return 130
            except Exception as exc:
                # 不吞异常：把账号池常见错误显式提示
                msg = str(exc).lower()
                if (
                    "no account" in msg
                    or "no active account" in msg
                    or "no accounts" in msg
                ):
                    logger.error(
                        "账号池可用账号耗尽",
                        extra={
                            "chunk_index": idx,
                            "term": ch["term"],
                            "exception": str(exc),
                        },
                    )
                    print(
                        f"\n错误：账号池里没有可用账号了 — {exc}\n"
                        "可能原因：所有账号都被风控 / cookies 过期 / 限流。\n"
                        "排查: make account-health  按建议重登 / 加新号后再续抓。",
                        file=sys.stderr,
                    )
                    return 4
                if "rate" in msg or "limit" in msg or "429" in msg:
                    logger.warning(
                        "分片被限流，跳过",
                        extra={"chunk_index": idx, "term": ch["term"]},
                    )
                else:
                    logger.exception(
                        "分片调用异常，跳过",
                        extra={"chunk_index": idx, "term": ch["term"]},
                    )
                progress.advance(task)
                continue

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

            # 每片之间随机抖动，降低被识别为机器流量
            if idx < len(chunks) and collected < target_max:
                sleep_s = random.uniform(SLEEP_MIN, SLEEP_MAX)
                await asyncio.sleep(sleep_s)

    logger.info("抓取结束", extra={"collected": collected, "out": args.out})
    print(f"完成：累计写入 {collected} 条到 {args.out}")
    return 0


def run(args: argparse.Namespace) -> int:
    return asyncio.run(_run_async(args))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "twscrape 主力方案：账号池轮询 + 按月分片回溯单博主历史。"
            " 零边际成本，常态化推荐。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "前置条件：\n"
            "  账号池已有 >= 1 个 active 账号。若未配置:\n"
            "    python scripts/account_pool/add_account.py --username u1 \\\n"
            '        --cookies "auth_token=xxx; ct0=yyy"\n'
        ),
    )
    p.add_argument("--user", required=True, help="博主 handle（不含 @）")
    p.add_argument("--since", help="起始日期 YYYY-MM-DD")
    p.add_argument("--until", help="结束日期 YYYY-MM-DD")
    p.add_argument(
        "--max", type=int, default=DEFAULT_MAX, help=f"最大条数，默认 {DEFAULT_MAX}"
    )
    p.add_argument("--out", required=True, help="输出 jsonl 路径")
    p.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help=f"twscrape 账号池 DB（默认 {DEFAULT_DB}）",
    )
    p.add_argument("--include-replies", action="store_true", help="包含回复推文")
    p.add_argument("--include-retweets", action="store_true", help="包含转推")
    p.add_argument(
        "--resume",
        action="store_true",
        help="从已有 jsonl 续抓，按 tweet_id 去重",
    )
    p.add_argument("--dry-run", action="store_true", help="只打印计划，不调用 twscrape")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
