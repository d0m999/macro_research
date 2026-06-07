"""往 twscrape 账号池新增一个 X 小号。

两种模式（推荐 cookies 模式，最稳）：

方式 A — cookies (推荐):
    python add_account.py --username u1 \
        --cookies "auth_token=xxx; ct0=yyy"

方式 B — 账号密码 + 邮箱 (twscrape 自动登录, 不稳, 部分邮箱不支持 IMAP):
    python add_account.py --username u1 --password "p1" \
        --email u1@x.com --email-password "mp1"

cookies 怎么从浏览器拿:
    1. Chrome / Edge / Firefox 登录 https://x.com
    2. 打开 DevTools (F12) -> Application -> Cookies -> https://x.com
    3. 复制 auth_token 和 ct0 两个 cookie 的值
    4. 拼成: "auth_token=<value>; ct0=<value>"

依赖:
    twscrape>=0.17.0
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

# 允许以脚本直接运行也能 import 同目录上层 _common
_PKG_DIR = Path(__file__).resolve().parent
_SCRIPTS_DIR = _PKG_DIR.parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from _common import setup_logging  # noqa: E402

# account_pool/ -> scripts/ -> x-trader-analysis/ -> .account_pool/accounts.db
DEFAULT_DB = Path(__file__).resolve().parents[2] / ".account_pool" / "accounts.db"
TEST_USER_LOGIN = "x"  # X 官方账号，公开稳定，用于一次性测试调用


def _mask(s: str | None) -> str:
    """简单脱敏：保留首尾 2 字符。"""
    if not s:
        return "<empty>"
    if len(s) <= 4:
        return "***"
    return f"{s[:2]}***{s[-2:]}"


async def _add_with_cookies(
    db_path: Path,
    username: str,
    cookies: str,
    email: str | None,
    email_password: str | None,
    password: str | None,
    logger: Any,
) -> int:
    """方式 A：cookies 模式（最推荐）。"""
    try:
        from twscrape import API
    except ImportError:
        logger.error("缺少 twscrape 依赖")
        print(
            "错误：未安装 twscrape。请执行：\n  uv pip install 'twscrape>=0.17.0'",
            file=sys.stderr,
        )
        return 3

    db_path.parent.mkdir(parents=True, exist_ok=True)
    api = API(str(db_path))

    # twscrape add_account 需要 username/password/email/email_password 四参数即使走 cookies
    # 没提供时给占位值（仅用于占位，cookies 已足够认证）
    pwd = password or "_placeholder_"
    em = email or f"{username}@placeholder.local"
    em_pw = email_password or "_placeholder_"

    try:
        await api.pool.add_account(
            username,
            pwd,
            em,
            em_pw,
            cookies=cookies,
        )
    except Exception as exc:
        logger.exception("add_account 失败")
        print(
            f"错误：向账号池注册账号 {username} 失败 — {exc}\n"
            "请检查：1) cookies 格式是否为 'auth_token=...; ct0=...'  "
            "2) DB 路径是否可写  3) twscrape 版本是否 >= 0.17.0",
            file=sys.stderr,
        )
        return 4

    logger.info(
        "账号已注册",
        extra={"username": username, "cookies_preview": _mask(cookies)},
    )

    # 立即做一次测试调用：用 user_by_login 验证 cookies 真实可用
    print(f"已注册账号 {username}，正在测试 cookies 可用性...")
    try:
        user = await api.user_by_login(TEST_USER_LOGIN)
        if not user:
            raise RuntimeError("user_by_login 返回空对象（cookies 可能已过期）")
        # 简单验证拿到的对象有合理字段
        if not (getattr(user, "id", None) or getattr(user, "id_str", None)):
            raise RuntimeError("user_by_login 返回缺少 id 字段（API 异常）")
    except Exception as exc:
        logger.exception("测试调用失败")
        print(
            f"警告：账号 {username} 已写入 DB，但测试调用失败 — {exc}\n"
            "可能原因：cookies 过期 / 账号被风控 / 网络问题。\n"
            "建议：重新从浏览器导出 cookies 后再次运行本命令（同 username 会覆盖）。",
            file=sys.stderr,
        )
        return 5

    print(f"账号 {username} 注册成功，已通过可用性测试。DB: {db_path}")
    return 0


async def _add_with_credentials(
    db_path: Path,
    username: str,
    password: str,
    email: str,
    email_password: str,
    logger: Any,
) -> int:
    """方式 B：账号密码 + 邮箱（twscrape 调 IMAP 拿验证码）。

    注意：不是所有邮箱都支持，ProtonMail/网易等可能失败；推荐 Gmail / Outlook + 应用专用密码。
    """
    try:
        from twscrape import API
    except ImportError:
        logger.error("缺少 twscrape 依赖")
        print(
            "错误：未安装 twscrape。请执行：\n  uv pip install 'twscrape>=0.17.0'",
            file=sys.stderr,
        )
        return 3

    db_path.parent.mkdir(parents=True, exist_ok=True)
    api = API(str(db_path))

    try:
        await api.pool.add_account(username, password, email, email_password)
    except Exception as exc:
        logger.exception("add_account 失败")
        print(
            f"错误：向账号池注册账号 {username} 失败 — {exc}",
            file=sys.stderr,
        )
        return 4

    logger.info(
        "账号已注册，正在尝试自动登录",
        extra={
            "username": username,
            "email": _mask(email),
        },
    )
    print(f"账号 {username} 已写入 DB，正在尝试自动登录...")

    try:
        await api.pool.login_all()
    except Exception as exc:
        logger.exception("login_all 失败")
        print(
            f"警告：账号 {username} 已写入 DB，但 login_all 失败 — {exc}\n"
            "建议：改用 cookies 模式（--cookies 'auth_token=...; ct0=...'）。",
            file=sys.stderr,
        )
        return 5

    # 同样做一次测试调用
    print("登录完成，正在测试可用性...")
    try:
        user = await api.user_by_login(TEST_USER_LOGIN)
        if not user:
            raise RuntimeError("user_by_login 返回空")
    except Exception as exc:
        logger.exception("测试调用失败")
        print(
            f"警告：登录成功但测试调用失败 — {exc}\n"
            "可能账号被风控，建议切换为 cookies 模式。",
            file=sys.stderr,
        )
        return 5

    print(f"账号 {username} 注册并登录成功，已通过可用性测试。DB: {db_path}")
    return 0


def run(args: argparse.Namespace) -> int:
    logger = setup_logging()
    db_path = Path(args.db).expanduser().resolve()

    if args.cookies:
        # 方式 A: cookies 模式
        return asyncio.run(
            _add_with_cookies(
                db_path=db_path,
                username=args.username,
                cookies=args.cookies,
                email=args.email,
                email_password=args.email_password,
                password=args.password,
                logger=logger,
            )
        )

    # 方式 B: 账号密码 + 邮箱
    missing = []
    if not args.password:
        missing.append("--password")
    if not args.email:
        missing.append("--email")
    if not args.email_password:
        missing.append("--email-password")
    if missing:
        print(
            "错误：使用账号密码模式时必须同时提供 "
            f"{', '.join(missing)}（或改用 --cookies 模式，更稳定）",
            file=sys.stderr,
        )
        return 2

    return asyncio.run(
        _add_with_credentials(
            db_path=db_path,
            username=args.username,
            password=args.password,
            email=args.email,
            email_password=args.email_password,
            logger=logger,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "往 twscrape 账号池新增 X 小号。"
            " 两种模式：cookies（推荐，最稳）/ 账号密码+邮箱（自动登录，不稳）。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  方式 A (cookies, 推荐):\n"
            '    python add_account.py --username u1 --cookies "auth_token=xxx; ct0=yyy"\n'
            "\n"
            "  方式 B (账号密码 + 邮箱, 自动登录):\n"
            "    python add_account.py --username u1 --password p1 \\\n"
            "        --email u1@gmail.com --email-password mp1\n"
            "\n"
            "cookies 怎么从浏览器拿：\n"
            "  1) Chrome / Firefox 登录 https://x.com\n"
            "  2) F12 -> Application -> Cookies -> https://x.com\n"
            "  3) 复制 auth_token 与 ct0 的值\n"
            '  4) 拼成 "auth_token=<value>; ct0=<value>"\n'
        ),
    )
    p.add_argument("--username", required=True, help="X 小号用户名（不含 @）")
    p.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help=f"账号池 DB 路径（默认 {DEFAULT_DB}）",
    )

    # 方式 A 字段
    p.add_argument(
        "--cookies",
        help=(
            '推荐：浏览器 cookies 字符串，至少含 auth_token 与 ct0。'
            ' 例如 "auth_token=xxx; ct0=yyy"'
        ),
    )

    # 方式 B 字段（也可作为方式 A 的可选补充）
    p.add_argument("--password", help="X 账号密码（方式 B 必填）")
    p.add_argument(
        "--email",
        help="X 账号绑定的邮箱（方式 B 必填，twscrape 用 IMAP 取验证码）",
    )
    p.add_argument(
        "--email-password",
        dest="email_password",
        help="邮箱密码（方式 B 必填；Gmail 建议用应用专用密码）",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
