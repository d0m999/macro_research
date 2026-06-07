"""检查 twscrape 账号池里每个账号的健康度。

用法:
    python health_check.py [--db .account_pool/accounts.db] [--fix] [--json]

输出 rich 表格:
    username, active, logged_in, last_used, total_req, error_msg, probe_status

probe_status 通过尝试 user_by_id(44196397) 调用得出（44196397 是 elonmusk 公开 ID）：
    - ok           调用成功，cookies 有效
    - rate_limited 临时限流，建议等待几小时
    - cookies_bad  cookies 过期或被风控（建议重登）
    - error        其它异常（看 error 列）
    - skipped      账号未激活 / 未登录，未做 probe

--fix 行为：
    - probe_status == rate_limited / cookies_bad / error 的账号会被尝试停用一段时间
      （twscrape 自带 set_active(False) 把账号从轮询里踢出）
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# 允许以脚本直接运行
_PKG_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _PKG_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from _common import setup_logging  # noqa: E402

# account_pool/ -> scripts/ -> x-trader-analysis/ -> .account_pool/accounts.db
DEFAULT_DB = Path(__file__).resolve().parents[2] / ".account_pool" / "accounts.db"
PROBE_USER_ID = 44196397  # elonmusk，公开稳定


@dataclass(frozen=True)
class AccountStatus:
    """单账号健康度快照。"""

    username: str
    active: bool
    logged_in: bool
    last_used: str
    total_req: int
    error_msg: str
    probe_status: str
    probe_detail: str


def _classify_probe_error(exc: BaseException) -> tuple[str, str]:
    """把异常分类成可读的 probe_status。"""
    name = type(exc).__name__
    msg = str(exc).lower()
    if "rate" in msg or "limit" in msg or "429" in msg:
        return "rate_limited", f"{name}: {exc}"
    if "401" in msg or "auth" in msg or "cookie" in msg or "csrf" in msg:
        return "cookies_bad", f"{name}: {exc}"
    if "ban" in msg or "suspend" in msg or "403" in msg:
        return "cookies_bad", f"{name}: {exc}"
    return "error", f"{name}: {exc}"


def _suggest(status: str) -> str:
    """根据 probe_status 给一句话补救建议。"""
    return {
        "ok": "正常使用",
        "rate_limited": "临时限流，停用 1-2 小时后自动恢复（或减少抓取频率）",
        "cookies_bad": "建议重登：用 add_account.py 重新导入 cookies（同 username 会覆盖）",
        "error": "查看 error_msg 决定，多次出现请重登",
        "skipped": "账号未激活或未登录，先用 add_account.py 注册",
    }.get(status, "未知")


async def _probe(api: Any, username: str) -> tuple[str, str]:
    """对单账号做一次轻量 API 调用，返回 (probe_status, detail)。"""
    try:
        user = await api.user_by_id(PROBE_USER_ID)
        if not user:
            return "error", "user_by_id 返回空"
        return "ok", "user_by_id OK"
    except Exception as exc:  # noqa: BLE001 - 我们就是要分类未知异常
        return _classify_probe_error(exc)


def _account_attr(acc: Any, *names: str, default: Any = "") -> Any:
    """从 twscrape Account 对象上取字段，兼容不同版本字段名。"""
    for n in names:
        if hasattr(acc, n):
            v = getattr(acc, n)
            if v is not None:
                return v
    return default


async def _gather_status(db_path: Path, do_fix: bool, logger: Any) -> list[AccountStatus]:
    try:
        from twscrape import API
    except ImportError:
        logger.error("缺少 twscrape 依赖")
        print(
            "错误：未安装 twscrape。请执行：\n  uv pip install 'twscrape>=0.17.0'",
            file=sys.stderr,
        )
        sys.exit(3)

    if not db_path.exists():
        print(
            f"错误：账号池 DB 不存在: {db_path}\n"
            "请先添加账号:\n"
            "  python scripts/account_pool/add_account.py --username u1 \\\n"
            '    --cookies "auth_token=xxx; ct0=yyy"',
            file=sys.stderr,
        )
        sys.exit(2)

    api = API(str(db_path))

    # twscrape 不同版本: pool.get_all() / accounts_info() / pool.accounts_info()
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
            logger.exception("调用账号池列举接口失败", extra={"getter": getter_name})
            continue

    if not accounts:
        print(
            f"账号池为空 ({db_path})。请先用 add_account.py 添加账号。",
            file=sys.stderr,
        )
        return []

    statuses: list[AccountStatus] = []
    for acc in accounts:
        # accounts_info 返回的可能是 dict 或对象，统一兼容
        if isinstance(acc, dict):

            def gp(k: str, default: Any = "") -> Any:
                return acc.get(k, default)

            username = str(gp("username") or gp("login") or "<unknown>")
            active = bool(gp("active", False))
            logged_in = bool(gp("logged_in", False))
            last_used = str(gp("last_used", "") or "")
            total_req = int(gp("total_req", 0) or 0)
            error_msg = str(gp("error_msg", "") or "")
        else:
            username = str(_account_attr(acc, "username", "login") or "<unknown>")
            active = bool(_account_attr(acc, "active", default=False))
            logged_in = bool(_account_attr(acc, "logged_in", default=False))
            last_used = str(_account_attr(acc, "last_used", default="") or "")
            total_req = int(_account_attr(acc, "total_req", default=0) or 0)
            error_msg = str(_account_attr(acc, "error_msg", default="") or "")

        if not (active and logged_in):
            statuses.append(
                AccountStatus(
                    username=username,
                    active=active,
                    logged_in=logged_in,
                    last_used=last_used,
                    total_req=total_req,
                    error_msg=error_msg,
                    probe_status="skipped",
                    probe_detail="账号未激活或未登录，跳过 probe",
                )
            )
            continue

        # 真正做 probe
        probe_status, probe_detail = await _probe(api, username)
        statuses.append(
            AccountStatus(
                username=username,
                active=active,
                logged_in=logged_in,
                last_used=last_used,
                total_req=total_req,
                error_msg=error_msg,
                probe_status=probe_status,
                probe_detail=probe_detail,
            )
        )

        # --fix: 把异常账号停用，避免被 twscrape 轮询又踩雷
        if do_fix and probe_status in {"cookies_bad", "error"}:
            try:
                set_active = getattr(api.pool, "set_active", None)
                if set_active and callable(set_active):
                    res = set_active(username, False)
                    if asyncio.iscoroutine(res):
                        await res
                    print(
                        f"  [--fix] 已停用 {username} ({probe_status})，"
                        "请用 add_account.py 重登。"
                    )
            except Exception:
                logger.exception("set_active 失败", extra={"username": username})

    return statuses


def _print_table(statuses: list[AccountStatus]) -> None:
    """用 rich 渲染状态表；rich 不可用时退化为纯文本。"""
    try:
        from rich.console import Console
        from rich.table import Table
    except ImportError:
        for s in statuses:
            print(
                f"{s.username}\tactive={s.active}\tlogged_in={s.logged_in}\t"
                f"probe={s.probe_status}\tlast_used={s.last_used}\t"
                f"total_req={s.total_req}\terror={s.error_msg}"
            )
        return

    console = Console()
    table = Table(title="twscrape 账号池健康度")
    table.add_column("username", style="cyan", no_wrap=True)
    table.add_column("active", justify="center")
    table.add_column("logged_in", justify="center")
    table.add_column("probe", style="bold")
    table.add_column("last_used")
    table.add_column("total_req", justify="right")
    table.add_column("error_msg", style="red", overflow="fold")
    table.add_column("suggest", style="yellow", overflow="fold")

    for s in statuses:
        probe_color = {
            "ok": "green",
            "rate_limited": "yellow",
            "cookies_bad": "red",
            "error": "red",
            "skipped": "dim",
        }.get(s.probe_status, "white")
        table.add_row(
            s.username,
            "[green]Y[/]" if s.active else "[red]N[/]",
            "[green]Y[/]" if s.logged_in else "[red]N[/]",
            f"[{probe_color}]{s.probe_status}[/]",
            s.last_used or "-",
            str(s.total_req),
            s.error_msg or "-",
            _suggest(s.probe_status),
        )

    console.print(table)


def _print_json(statuses: list[AccountStatus]) -> None:
    try:
        import orjson

        data = [
            {
                "username": s.username,
                "active": s.active,
                "logged_in": s.logged_in,
                "last_used": s.last_used,
                "total_req": s.total_req,
                "error_msg": s.error_msg,
                "probe_status": s.probe_status,
                "probe_detail": s.probe_detail,
                "suggest": _suggest(s.probe_status),
            }
            for s in statuses
        ]
        print(orjson.dumps(data, option=orjson.OPT_INDENT_2).decode("utf-8"))
    except ImportError:
        import json

        data = [
            {
                "username": s.username,
                "active": s.active,
                "logged_in": s.logged_in,
                "last_used": s.last_used,
                "total_req": s.total_req,
                "error_msg": s.error_msg,
                "probe_status": s.probe_status,
                "probe_detail": s.probe_detail,
                "suggest": _suggest(s.probe_status),
            }
            for s in statuses
        ]
        print(json.dumps(data, indent=2, ensure_ascii=False))


def run(args: argparse.Namespace) -> int:
    logger = setup_logging()
    db_path = Path(args.db).expanduser().resolve()

    statuses = asyncio.run(_gather_status(db_path, args.fix, logger))
    if not statuses:
        return 1

    if args.json:
        _print_json(statuses)
    else:
        _print_table(statuses)

    bad_count = sum(1 for s in statuses if s.probe_status in {"cookies_bad", "error"})
    return 0 if bad_count == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="twscrape 账号池健康度检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python health_check.py\n"
            "  python health_check.py --fix\n"
            "  python health_check.py --json > status.json\n"
        ),
    )
    p.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help=f"账号池 DB 路径（默认 {DEFAULT_DB}）",
    )
    p.add_argument(
        "--fix",
        action="store_true",
        help="把 probe_status 为 cookies_bad / error 的账号 set_active(False)",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 而非 rich 表格",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
