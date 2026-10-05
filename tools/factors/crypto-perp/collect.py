#!/usr/bin/env python3
"""
Binance USDⓈ-M 永续日频数据采集器（加密线）。

边界（重要）
------------
本脚本只做「公开行情只读采集 + 落本地 CSV」，不接任何下单、账户、签名或执行接口。
按 CLAUDE.md，本仓库禁止重新引入 Python 交易执行层（FreqTrade / 下单 / Docker / 交易库）。
本脚本属于离线分析层，不属于执行层。不要在此目录引入订单或仓位相关代码。

数据窗口（2026-09-20 实测）
--------------------------
长历史（可回溯至合约上线）：
    /fapi/v1/klines        永续日线 OHLCV + taker 买量
    /api/v3/klines         现货日线 OHLCV（用于基差类因子）
    /fapi/v1/fundingRate   资金费结算记录（每 8h 一条）
30 天窗口（Binance 只保留最近 30 天，只能靠本脚本每日累积）：
    /futures/data/openInterestHist
    /futures/data/globalLongShortAccountRatio
    /futures/data/topLongShortAccountRatio
    /futures/data/topLongShortPositionRatio
    /futures/data/takerlongshortRatio
=> 30 天窗口的数据集是「累积型」：每次运行把新窗口并入本地文件，历史随时间增长。
   不启动采集，这些序列永远只有 30 天。

网络
----
fapi.binance.com 位于墙外，实测需经本机代理 127.0.0.1:7897（见 ~/.codex/config.toml）。
现货 api.binance.com 同样需代理；data-api.binance.vision 可直连但只镜像现货 /api/v3/*。

用法
----
    python3 collect.py                    # 全量：长历史 + 30 天窗口
    python3 collect.py --only window      # 只刷 30 天窗口（建议每日跑）
    python3 collect.py --no-proxy         # 直连（仅现货可能可用）
    python3 collect.py --proxy http://127.0.0.1:7897
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

REPO = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)
DEFAULT_OUT = os.path.join(REPO, "data", "raw", "binance-futures")
DEFAULT_PROXY = "http://127.0.0.1:7897"

FUT = "https://fapi.binance.com"
SPOT = "https://api.binance.com"
SPOT_PUBLIC = "https://data-api.binance.vision"

UA = "vibe-trading-factor-collector/1.0 (research; read-only public market data)"

# 永续合约上线时间，长历史分页起点
START_MS = int(datetime(2019, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)


def iso_of(ts_ms):
    return datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def make_opener(proxy):
    handlers = []
    if proxy:
        handlers.append(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    else:
        handlers.append(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener(*handlers)


def get_json(opener, url, params=None, retries=3, timeout=25):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with opener.open(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (418, 429):
                time.sleep(3.0 * (attempt + 1))
                continue
            if e.code == 404:
                raise
            time.sleep(1.0 * (attempt + 1))
        except Exception as e:  # noqa: BLE001 - 网络异常统一重试
            last = e
            time.sleep(1.0 * (attempt + 1))
    raise RuntimeError("GET failed: %s (%s)" % (url, last))


def probe(opener, log):
    """探测哪些 base 可用，返回 (spot_base, fut_base)。"""
    spot_base = None
    for base in (SPOT, SPOT_PUBLIC):
        try:
            get_json(opener, base + "/api/v3/ping", retries=1)
            spot_base = base
            break
        except Exception:  # noqa: BLE001
            continue
    fut_base = None
    try:
        get_json(opener, FUT + "/fapi/v1/ping", retries=1)
        fut_base = FUT
    except Exception:  # noqa: BLE001
        pass
    log("probe: spot=%s futures=%s" % (spot_base or "UNREACHABLE", fut_base or "UNREACHABLE"))
    return spot_base, fut_base


def merge_csv(path, header, rows, key_pos=0):
    """按第一列（ts_ms）去重合并，保留新旧全部记录，返回 (新增数, 总行数)。"""
    existing = {}
    if os.path.exists(path):
        with open(path, "r", newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            for i, rec in enumerate(reader):
                if i == 0 or not rec:
                    continue
                existing[rec[key_pos]] = rec
    before = len(existing)
    for rec in rows:
        existing[str(rec[key_pos])] = [str(c) for c in rec]
    ordered = sorted(existing.values(), key=lambda r: int(r[key_pos]))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(ordered)
    os.replace(tmp, path)
    return len(ordered) - before, len(ordered)


def paginate(opener, url, base_params, limit, ts_field, sleep):
    """按时间戳游标分页拉取，直到返回不足 limit 条。"""
    out = []
    cursor = base_params.pop("startTime", None)
    while True:
        params = dict(base_params)
        params["limit"] = limit
        if cursor is not None:
            params["startTime"] = cursor
        batch = get_json(opener, url, params)
        if not batch:
            break
        out.extend(batch)
        last_ts = int(batch[-1][ts_field] if isinstance(batch[-1], dict) else batch[-1][0])
        if cursor is not None and last_ts < cursor:
            break
        cursor = last_ts + 1
        if len(batch) < limit:
            break
        time.sleep(sleep)
    return out


def collect_klines(opener, base, path, symbol, sleep):
    url = base + path
    raw = paginate(
        opener, url, {"symbol": symbol, "interval": "1d", "startTime": START_MS},
        1000, 0, sleep,
    )
    rows = []
    for k in raw:
        ts = int(k[0])
        rows.append([ts, iso_of(ts), k[1], k[2], k[3], k[4], k[5], k[7], k[8], k[9], k[10]])
    return rows


def collect_funding(opener, symbol, sleep):
    url = FUT + "/fapi/v1/fundingRate"
    raw = paginate(
        opener, url, {"symbol": symbol, "startTime": START_MS}, 1000, "fundingTime", sleep
    )
    rows = []
    for r in raw:
        ts = int(r["fundingTime"])
        rows.append([ts, iso_of(ts), r["fundingRate"], r.get("markPrice", "")])
    return rows


def collect_oi(opener, symbol):
    url = FUT + "/futures/data/openInterestHist"
    raw = get_json(opener, url, {"symbol": symbol, "period": "1d", "limit": 500})
    rows = []
    for r in raw:
        ts = int(r["timestamp"])
        rows.append([ts, iso_of(ts), r["sumOpenInterest"], r["sumOpenInterestValue"]])
    return rows


def collect_lsr(opener, symbol, kind):
    url = FUT + "/futures/data/" + kind
    raw = get_json(opener, url, {"symbol": symbol, "period": "1d", "limit": 500})
    rows = []
    for r in raw:
        ts = int(r["timestamp"])
        rows.append(
            [ts, iso_of(ts), r["longShortRatio"], r["longAccount"], r["shortAccount"]]
        )
    return rows


def collect_taker(opener, symbol):
    url = FUT + "/futures/data/takerlongshortRatio"
    raw = get_json(opener, url, {"symbol": symbol, "period": "1d", "limit": 500})
    rows = []
    for r in raw:
        ts = int(r["timestamp"])
        rows.append([ts, iso_of(ts), r["buySellRatio"], r["buyVol"], r["sellVol"]])
    return rows


LONG_DATASETS = ("perp_1d", "spot_1d", "funding")
WINDOW_DATASETS = ("oi_1d", "lsr_global", "lsr_top_account", "lsr_top_position", "taker_ratio")

HEADERS = {
    "perp_1d": ["ts_ms", "iso_utc", "open", "high", "low", "close", "volume",
                "quote_volume", "trades", "taker_buy_base", "taker_buy_quote"],
    "spot_1d": ["ts_ms", "iso_utc", "open", "high", "low", "close", "volume",
                "quote_volume", "trades", "taker_buy_base", "taker_buy_quote"],
    "funding": ["ts_ms", "iso_utc", "funding_rate", "mark_price"],
    "oi_1d": ["ts_ms", "iso_utc", "sum_open_interest", "sum_open_interest_value"],
    "lsr_global": ["ts_ms", "iso_utc", "long_short_ratio", "long_account", "short_account"],
    "lsr_top_account": ["ts_ms", "iso_utc", "long_short_ratio", "long_account", "short_account"],
    "lsr_top_position": ["ts_ms", "iso_utc", "long_short_ratio", "long_account", "short_account"],
    "taker_ratio": ["ts_ms", "iso_utc", "buy_sell_ratio", "buy_vol", "sell_vol"],
}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Binance 永续日频数据采集（只读）")
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--outdir", default=DEFAULT_OUT)
    ap.add_argument("--proxy", default=DEFAULT_PROXY)
    ap.add_argument("--no-proxy", action="store_true")
    ap.add_argument("--only", choices=("all", "long", "window"), default="all")
    ap.add_argument("--sleep", type=float, default=0.25, help="分页请求间隔秒")
    args = ap.parse_args(argv)

    proxy = None if args.no_proxy else args.proxy
    logs = []

    def log(msg):
        line = "[%s] %s" % (datetime.now().strftime("%H:%M:%S"), msg)
        logs.append(line)
        print(line, flush=True)

    opener = make_opener(proxy)
    log("symbol=%s proxy=%s outdir=%s" % (args.symbol, proxy or "direct", args.outdir))
    spot_base, fut_base = probe(opener, log)

    if args.only in ("all", "long") and not (spot_base and fut_base):
        log("!! 长历史需要 spot 与 futures 同时可达，跳过 long")
    if args.only in ("all", "window") and not fut_base:
        log("!! 30 天窗口需要 futures 可达，无法继续")
        return 2

    state_path = os.path.join(args.outdir, "_state.json")
    state = {"last_run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "symbol": args.symbol, "datasets": {}}
    if os.path.exists(state_path):
        try:
            with open(state_path, encoding="utf-8") as fh:
                previous = json.load(fh)
            state["previous_run_utc"] = previous.get("last_run_utc")
        except Exception:  # noqa: BLE001
            pass

    def write(dataset, rows):
        path = os.path.join(args.outdir, "%s_%s.csv" % (args.symbol, dataset))
        added, total = merge_csv(path, HEADERS[dataset], rows)
        state["datasets"][dataset] = {
            "path": os.path.relpath(path, REPO),
            "rows_total": total,
            "rows_added": added,
            "first_ts_ms": int(rows[0][0]) if rows else None,
            "last_ts_ms": int(rows[-1][0]) if rows else None,
        }
        log("%-18s +%-5d total=%-6d %s" % (dataset, added, total, os.path.basename(path)))
        return added

    try:
        if args.only in ("all", "long") and spot_base and fut_base:
            log("--- 长历史 ---")
            write("perp_1d", collect_klines(opener, fut_base, "/fapi/v1/klines",
                                           args.symbol, args.sleep))
            write("spot_1d", collect_klines(opener, spot_base, "/api/v3/klines",
                                           args.symbol, args.sleep))
            write("funding", collect_funding(opener, args.symbol, args.sleep))

        if args.only in ("all", "window"):
            log("--- 30 天窗口（累积型） ---")
            write("oi_1d", collect_oi(opener, args.symbol))
            write("lsr_global", collect_lsr(opener, args.symbol, "globalLongShortAccountRatio"))
            write("lsr_top_account", collect_lsr(opener, args.symbol, "topLongShortAccountRatio"))
            write("lsr_top_position", collect_lsr(opener, args.symbol, "topLongShortPositionRatio"))
            write("taker_ratio", collect_taker(opener, args.symbol))
    finally:
        os.makedirs(args.outdir, exist_ok=True)
        with open(state_path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        log("state -> %s" % os.path.relpath(state_path, REPO))

    return 0


if __name__ == "__main__":
    sys.exit(main())
