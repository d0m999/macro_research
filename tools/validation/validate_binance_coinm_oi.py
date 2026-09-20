#!/usr/bin/env python3
"""Read-only validation of TradingView OI candles against Binance COIN-M OI.

The module deliberately has no trading, account, database, service, or
deployment code.  It uses only Python's standard library and keeps the two
data paths explicit:

* ``/dapi/v1/openInterest`` is the realtime source of ``BTCUSD_PERP``
  contracts.
* ``/futures/data/openInterestHist`` is historical statistical data and is
  reported as diagnostic evidence only.

TradingView CSV columns are positional because TradingView exports can contain
unquoted Chinese punctuation in the header.  Only columns 10--13 (1-based)
are read; price, EMA, and columns 14--17 are never used.
"""

from __future__ import annotations

import argparse
import csv
import email.utils
import hashlib
import json
import os
import socket
import ssl
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


UTC = timezone.utc
API_BASE_URL = "https://dapi.binance.com"
SYMBOL = "BTCUSD_PERP"
PAIR = "BTCUSD"
CONTRACT_TYPE = "PERPETUAL"
HISTORY_PATH = "/futures/data/openInterestHist"
LIVE_PATH = "/dapi/v1/openInterest"

CSV_COLUMN_COUNT = 17
CSV_TIME_COLUMN = 0
CSV_OI_START_COLUMN = 9
CSV_OI_END_COLUMN = 13
CSV_OI_HEADER_MARKERS = ("开盘价", "最高价", "最低价", "关闭")
RAW_HEADER = ("timestamp_utc", "symbol", "open_interest_contracts")
DEFAULT_RAW_DIR = Path("data/raw/binance-oi")
DEFAULT_REPORT_DIR = Path("data/reports")

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_INCONCLUSIVE = 2
EXIT_ERROR = 3

DEFAULT_INTERVAL_SECONDS = 5
DEFAULT_TARGET_DAYS = 7
DEFAULT_MAX_DAYS = 14
DEFAULT_MAX_RETRIES = 3
DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_OPEN_CLOSE_BPS = Decimal("10")
DEFAULT_HIGH_LOW_BPS = Decimal("20")


class ValidationError(Exception):
    """Base class for input and API validation failures."""


class InputError(ValidationError):
    """The local input or command arguments are invalid."""


class APIError(ValidationError):
    """The public API failed or returned an invalid schema/value."""


@dataclass(frozen=True)
class OIBar:
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    def values(self) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        return (self.open, self.high, self.low, self.close)

    def as_dict(self) -> dict[str, str]:
        return {
            "open": decimal_to_string(self.open),
            "high": decimal_to_string(self.high),
            "low": decimal_to_string(self.low),
            "close": decimal_to_string(self.close),
        }


@dataclass(frozen=True)
class TVRow:
    day: date
    oi: OIBar
    line_number: int


@dataclass(frozen=True)
class LiveSample:
    timestamp_ms: int
    symbol: str
    pair: str
    contract_type: str
    open_interest: Decimal
    received_at_utc: str | None = None

    def as_dict(self) -> dict[str, str | int]:
        result: dict[str, str | int] = {
            "timestamp_ms": self.timestamp_ms,
            "timestamp_utc": format_timestamp(self.timestamp_ms),
            "symbol": self.symbol,
            "pair": self.pair,
            "contract_type": self.contract_type,
            "open_interest_contracts": decimal_to_string(self.open_interest),
        }
        if self.received_at_utc is not None:
            result["received_at_utc"] = self.received_at_utc
        return result


@dataclass(frozen=True)
class HistoricalSample:
    timestamp_ms: int
    pair: str
    contract_type: str
    sum_open_interest: Decimal
    raw: Mapping[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp_ms": self.timestamp_ms,
            "timestamp_utc": format_timestamp(self.timestamp_ms),
            "pair": self.pair,
            "contract_type": self.contract_type,
            "sum_open_interest_contracts": decimal_to_string(
                self.sum_open_interest
            ),
        }


@dataclass(frozen=True)
class DayCoverage:
    day: date
    sample_count: int
    coverage_ratio: Decimal
    max_gap_seconds: Decimal
    leading_gap_seconds: Decimal
    trailing_gap_seconds: Decimal
    qualified: bool
    reasons: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "date": self.day.isoformat(),
            "sample_count": self.sample_count,
            "coverage_ratio": decimal_to_string(self.coverage_ratio),
            "coverage_percent": decimal_to_string(self.coverage_ratio * 100),
            "max_gap_seconds": decimal_to_string(self.max_gap_seconds),
            "leading_gap_seconds": decimal_to_string(self.leading_gap_seconds),
            "trailing_gap_seconds": decimal_to_string(self.trailing_gap_seconds),
            "qualified": self.qualified,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class ComparisonMetric:
    field: str
    tv_value: Decimal
    binance_value: Decimal
    difference_contracts: Decimal
    absolute_difference_contracts: Decimal
    relative_error: Decimal | None
    error_bps: Decimal | None
    tolerance_bps: Decimal
    within_tolerance: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "field": self.field,
            "tv_value_contracts": decimal_to_string(self.tv_value),
            "binance_value_contracts": decimal_to_string(self.binance_value),
            "difference_contracts_tv_minus_binance": decimal_to_string(
                self.difference_contracts
            ),
            "absolute_difference_contracts": decimal_to_string(
                self.absolute_difference_contracts
            ),
            "relative_error": decimal_to_optional_string(self.relative_error),
            "error_bps": decimal_to_optional_string(self.error_bps),
            "tolerance_bps": decimal_to_string(self.tolerance_bps),
            "within_tolerance": self.within_tolerance,
        }


def decimal_to_string(value: Decimal) -> str:
    """Serialize Decimal without losing integer precision."""

    if value.is_nan():
        return "NaN"
    if value.is_infinite():
        return "Infinity" if value > 0 else "-Infinity"
    return format(value, "f")


def decimal_to_optional_string(value: Decimal | None) -> str | None:
    return None if value is None else decimal_to_string(value)


def parse_contract_decimal(value: Any, field_name: str) -> Decimal:
    """Parse a non-negative integer contract count exactly with Decimal."""

    if value is None or isinstance(value, bool):
        raise ValidationError(f"{field_name} 缺失或类型无效")
    text = str(value).strip()
    if not text:
        raise ValidationError(f"{field_name} 缺失")
    try:
        parsed = Decimal(text)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"{field_name} 不是有效数字: {text!r}") from exc
    if not parsed.is_finite():
        raise ValidationError(f"{field_name} 不能是 NaN 或无穷大")
    if parsed < 0 or parsed != parsed.to_integral_value():
        raise ValidationError(f"{field_name} 必须是非负整数合约张数: {text!r}")
    return parsed


def parse_timestamp_ms(value: Any, field_name: str = "timestamp") -> int:
    if value is None or isinstance(value, bool):
        raise ValidationError(f"{field_name} 缺失或类型无效")
    text = str(value).strip()
    if not text or not text.isdigit():
        raise ValidationError(f"{field_name} 必须是毫秒整数: {value!r}")
    parsed = int(text)
    if parsed <= 0:
        raise ValidationError(f"{field_name} 必须为正数")
    return parsed


def format_timestamp(timestamp_ms: int) -> str:
    seconds, millis = divmod(timestamp_ms, 1000)
    value = datetime.fromtimestamp(seconds, UTC).replace(microsecond=millis * 1000)
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def bucket_date(timestamp_ms: int) -> date:
    """Return the UTC day ending at an API period-end timestamp.

    Binance historical ``timestamp`` is the end time of a period.  Subtracting
    one millisecond means an exact midnight end belongs to the preceding UTC
    day, rather than being incorrectly assigned to the next day.
    """

    adjusted = timestamp_ms - 1
    seconds, _ = divmod(adjusted, 1000)
    return datetime.fromtimestamp(seconds, UTC).date()


def day_start_ms(day: date) -> int:
    return int(datetime(day.year, day.month, day.day, tzinfo=UTC).timestamp() * 1000)


def day_end_exclusive_ms(day: date) -> int:
    return day_start_ms(day + timedelta(days=1))


def parse_timezone(name: str | None) -> timezone:
    """Parse the supported validation timezone.

    The forward acceptance path is intentionally UTC-only.  ``UTC`` and
    common zero-offset spellings are accepted; other zones are rejected so a
    caller cannot accidentally claim a UTC-day comparison with local dates.
    """

    if name is None:
        raise InputError("必须明确指定 --timezone UTC")
    normalized = name.strip().upper()
    if normalized in {"UTC", "Z", "GMT", "ETC/UTC"}:
        return UTC
    raise InputError("本工具的前瞻核验只接受 --timezone UTC")


def parse_csv_day(value: str, timezone_value: timezone) -> date:
    text = value.strip().lstrip("\ufeff")
    if not text:
        raise InputError("CSV 日期为空")
    try:
        if len(text) == 10 and text[4] == "-" and text[7] == "-":
            return date.fromisoformat(text)
        if text.isdigit():
            numeric = int(text)
            milliseconds = numeric if numeric >= 10**11 else numeric * 1000
            return bucket_date(milliseconds)
        iso_text = text[:-1] + "+00:00" if text.endswith("Z") else text
        parsed = datetime.fromisoformat(iso_text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone_value)
        return parsed.astimezone(UTC).date()
    except (ValueError, OverflowError) as exc:
        raise InputError(f"CSV 日期/时间无法解析: {value!r}") from exc


def normalize_header(value: str) -> str:
    return "".join(value.strip().lower().split())


def validate_tv_header(header: Sequence[str]) -> None:
    if len(header) != CSV_COLUMN_COUNT:
        raise InputError(
            f"TradingView CSV 表头必须为 {CSV_COLUMN_COUNT} 列，实际 {len(header)} 列"
        )
    time_header = normalize_header(header[CSV_TIME_COLUMN])
    if time_header not in {"time", "date", "日期", "时间"}:
        raise InputError(f"TradingView CSV 第 1 列不是时间列: {header[0]!r}")
    for offset, marker in enumerate(CSV_OI_HEADER_MARKERS):
        column = CSV_OI_START_COLUMN + offset
        normalized = normalize_header(header[column])
        if "oi" not in normalized or "原生合约张数" not in normalized:
            raise InputError(
                f"TradingView CSV 第 {column + 1} 列不是 OI OHLC 原生合约张数列: "
                f"{header[column]!r}"
            )
        if marker not in normalized:
            raise InputError(
                f"TradingView CSV 第 {column + 1} 列缺少中文字段 {marker!r}: "
                f"{header[column]!r}"
            )
    # The aggregate OI columns at positions 14--17 are intentionally not
    # validated or read.  Their presence cannot shift the selected positional
    # range because the complete export shape is checked above.


def read_tradingview_csv(path: Path, timezone_value: timezone = UTC) -> list[TVRow]:
    if not path.is_file():
        raise InputError(f"TradingView CSV 不存在: {path}")
    rows: list[TVRow] = []
    seen_dates: set[date] = set()
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise InputError("TradingView CSV 为空") from exc
            validate_tv_header(header)
            for line_number, row in enumerate(reader, start=2):
                if not row or all(not cell.strip() for cell in row):
                    continue
                if len(row) != CSV_COLUMN_COUNT:
                    raise InputError(
                        f"TradingView CSV 第 {line_number} 行必须为 "
                        f"{CSV_COLUMN_COUNT} 列，实际 {len(row)} 列"
                    )
                day = parse_csv_day(row[CSV_TIME_COLUMN], timezone_value)
                if day in seen_dates:
                    raise InputError(f"TradingView CSV 存在重复日期: {day.isoformat()}")
                values: list[Decimal] = []
                for column in range(CSV_OI_START_COLUMN, CSV_OI_END_COLUMN):
                    try:
                        values.append(
                            parse_contract_decimal(row[column], f"CSV 第 {line_number} 行第 {column + 1} 列")
                        )
                    except ValidationError as exc:
                        raise InputError(str(exc)) from exc
                seen_dates.add(day)
                rows.append(TVRow(day, OIBar(*values), line_number))
    except csv.Error as exc:
        raise InputError(f"TradingView CSV 解析失败: {exc}") from exc
    rows.sort(key=lambda item: item.day)
    if not rows:
        raise InputError("TradingView CSV 没有数据行")
    return rows


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise InputError(f"文件不存在，无法计算 SHA-256: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def retry_after_seconds(headers: Any) -> float | None:
    if headers is None:
        return None
    try:
        value = headers.get("Retry-After")
    except AttributeError:
        return None
    if value is None:
        return None
    try:
        delay = float(str(value).strip())
        return max(0.0, delay)
    except ValueError:
        try:
            retry_at = email.utils.parsedate_to_datetime(str(value))
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=UTC)
            return max(0.0, retry_at.timestamp() - time.time())
        except (TypeError, ValueError, OverflowError):
            return None


class BinanceHTTPClient:
    """Small injectable GET client with bounded transient retries."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_seconds: float = 1.0,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
        ssl_context: ssl.SSLContext | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise InputError("timeout 必须为正数")
        if max_retries < 0:
            raise InputError("max-retries 不能为负数")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_seconds = max(0.0, backoff_seconds)
        self.opener = opener
        self.sleep = sleep
        self.ssl_context = ssl_context or default_ssl_context()
        self.requests: list[dict[str, Any]] = []

    def get_json(self, path: str, params: Mapping[str, Any]) -> Any:
        query = urlencode({key: value for key, value in params.items() if value is not None})
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"
        self.requests.append({"method": "GET", "path": path, "params": dict(params)})
        request = Request(
            url,
            method="GET",
            headers={"Accept": "application/json", "User-Agent": "vibe-trading-oi-validator/1.0"},
        )
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                opener_kwargs: dict[str, Any] = {"timeout": self.timeout_seconds}
                if self.opener is urlopen:
                    opener_kwargs["context"] = self.ssl_context
                with self.opener(request, **opener_kwargs) as response:
                    status = int(getattr(response, "status", 200))
                    body = response.read()
                    headers = getattr(response, "headers", None)
                if status == 429 or 500 <= status <= 599:
                    if attempt < self.max_retries:
                        self.sleep(self._retry_delay(attempt, headers, status))
                        continue
                    raise APIError(f"Binance HTTP {status}，重试次数已耗尽")
                if status < 200 or status >= 300:
                    raise APIError(f"Binance HTTP {status}")
                return self._decode_json(body)
            except HTTPError as exc:
                last_error = exc
                status = int(exc.code)
                headers = getattr(exc, "headers", None)
                if status == 429 or 500 <= status <= 599:
                    if attempt < self.max_retries:
                        self.sleep(self._retry_delay(attempt, headers, status))
                        continue
                raise APIError(f"Binance HTTP {status}: {self._error_body(exc)}") from exc
            except (URLError, TimeoutError, socket.timeout, OSError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    self.sleep(self._retry_delay(attempt, None, None))
                    continue
                raise APIError(f"Binance 请求失败，重试次数已耗尽: {exc}") from exc
            except json.JSONDecodeError as exc:
                raise APIError(f"Binance 返回无效 JSON: {exc}") from exc
        raise APIError(f"Binance 请求失败: {last_error}")

    def _retry_delay(self, attempt: int, headers: Any, status: int | None) -> float:
        if status == 429:
            retry_after = retry_after_seconds(headers)
            if retry_after is not None:
                return retry_after
        return self.backoff_seconds * (2**attempt)

    @staticmethod
    def _decode_json(body: bytes | str) -> Any:
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        payload = json.loads(body)
        if isinstance(payload, dict) and isinstance(payload.get("code"), int) and payload["code"] < 0:
            raise APIError(f"Binance API error {payload['code']}: {payload.get('msg', '')}")
        return payload

    @staticmethod
    def _error_body(error: HTTPError) -> str:
        try:
            body = error.read().decode("utf-8", errors="replace")
        except Exception:
            return str(error)
        return body[:500]


def default_ssl_context() -> ssl.SSLContext:
    """Build a verifying context using the host's available CA bundle.

    The Python 3.10 framework on some macOS installations points OpenSSL at a
    bundle that is not installed, while ``curl`` uses ``/etc/ssl/cert.pem``.
    Trying existing system bundles keeps verification enabled and avoids the
    unsafe ``CERT_NONE`` fallback.
    """

    candidates: list[str] = []
    for variable in ("SSL_CERT_FILE", "CURL_CA_BUNDLE"):
        configured = os.environ.get(variable)
        if configured:
            candidates.append(configured)
    verify_paths = ssl.get_default_verify_paths()
    if verify_paths.cafile:
        candidates.append(verify_paths.cafile)
    candidates.extend(("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"))
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen or not os.path.isfile(candidate):
            continue
        seen.add(candidate)
        try:
            context = ssl.create_default_context(cafile=candidate)
        except (OSError, ssl.SSLError):
            continue
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        return context
    context = ssl.create_default_context()
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


class BinanceOIAPI:
    def __init__(self, client: BinanceHTTPClient) -> None:
        self.client = client

    def fetch_live(self, received_at: datetime | None = None) -> LiveSample:
        payload = self.client.get_json(LIVE_PATH, {"symbol": SYMBOL})
        try:
            if not isinstance(payload, dict):
                raise ValidationError("实时 OI 响应不是对象")
            validate_exact(payload, "symbol", SYMBOL)
            validate_exact(payload, "pair", PAIR)
            validate_exact(payload, "contractType", CONTRACT_TYPE)
            timestamp_ms = parse_timestamp_ms(payload.get("time"), "实时 OI time")
            open_interest = parse_contract_decimal(payload.get("openInterest"), "实时 openInterest")
        except ValidationError as exc:
            raise APIError(str(exc)) from exc
        return LiveSample(
            timestamp_ms=timestamp_ms,
            symbol=SYMBOL,
            pair=PAIR,
            contract_type=CONTRACT_TYPE,
            open_interest=open_interest,
            received_at_utc=(received_at or datetime.now(UTC)).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        )

    def fetch_history(
        self,
        period: str,
        start_time_ms: int,
        end_time_ms: int,
        limit: int = 500,
    ) -> list[HistoricalSample]:
        payload = self.client.get_json(
            HISTORY_PATH,
            {
                "pair": PAIR,
                "contractType": CONTRACT_TYPE,
                "period": period,
                "limit": limit,
                "startTime": start_time_ms,
                "endTime": end_time_ms,
            },
        )
        if not isinstance(payload, list):
            raise APIError("历史 OI 响应不是数组")
        result: list[HistoricalSample] = []
        for index, item in enumerate(payload):
            try:
                if not isinstance(item, dict):
                    raise ValidationError(f"历史 OI 第 {index} 项不是对象")
                validate_exact(item, "pair", PAIR)
                validate_exact(item, "contractType", CONTRACT_TYPE)
                timestamp_ms = parse_timestamp_ms(item.get("timestamp"), "历史 timestamp")
                value = parse_contract_decimal(item.get("sumOpenInterest"), "历史 sumOpenInterest")
            except ValidationError as exc:
                raise APIError(str(exc)) from exc
            result.append(
                HistoricalSample(
                    timestamp_ms=timestamp_ms,
                    pair=PAIR,
                    contract_type=CONTRACT_TYPE,
                    sum_open_interest=value,
                    raw=item,
                )
            )
        return result


def validate_exact(payload: Mapping[str, Any], key: str, expected: str) -> None:
    actual = payload.get(key)
    if actual != expected:
        raise ValidationError(f"{key} 必须为 {expected!r}，实际为 {actual!r}")


def period_milliseconds(period: str) -> int:
    values = {"5m": 5 * 60 * 1000, "1d": 24 * 60 * 60 * 1000}
    try:
        return values[period]
    except KeyError as exc:
        raise InputError(f"不支持的历史周期: {period}") from exc


def paginate_history(
    fetch_page: Callable[[int, int, int], Sequence[HistoricalSample]],
    start_time_ms: int,
    end_time_ms: int,
    period: str,
    limit: int = 500,
) -> list[HistoricalSample]:
    """Fetch a bounded history in windows and de-duplicate by timestamp.

    Binance's statistical endpoint caps ``limit`` at 500.  Time windows are
    sized to fit at most ``limit`` period slots, which remains safe whether a
    response is oldest-first or newest-first.  A timestamp set makes an
    overlapping page harmless and provides the explicit pagination de-dupe
    behavior required by the validation report.
    """

    if start_time_ms <= 0 or end_time_ms < start_time_ms:
        raise InputError("历史时间范围无效")
    if not 1 <= limit <= 500:
        raise InputError("历史 limit 必须在 1..500")
    period_ms = period_milliseconds(period)
    cursor = start_time_ms
    by_timestamp: dict[int, HistoricalSample] = {}
    while cursor <= end_time_ms:
        window_end = min(end_time_ms, cursor + period_ms * (limit - 1))
        page = list(fetch_page(cursor, window_end, limit))
        for item in page:
            if not start_time_ms <= item.timestamp_ms <= end_time_ms:
                continue
            by_timestamp.setdefault(item.timestamp_ms, item)
        if window_end >= end_time_ms:
            break
        cursor = window_end + 1
    return [by_timestamp[key] for key in sorted(by_timestamp)]


def aggregate_oi_bars(samples: Iterable[LiveSample | HistoricalSample]) -> dict[date, OIBar]:
    grouped: dict[date, list[LiveSample | HistoricalSample]] = {}
    for sample in samples:
        grouped.setdefault(bucket_date(sample.timestamp_ms), []).append(sample)
    result: dict[date, OIBar] = {}
    for day, values in grouped.items():
        values.sort(key=lambda item: item.timestamp_ms)
        numbers = [
            item.open_interest if isinstance(item, LiveSample) else item.sum_open_interest
            for item in values
        ]
        result[day] = OIBar(numbers[0], max(numbers), min(numbers), numbers[-1])
    return result


def analyze_day_coverage(
    samples: Sequence[LiveSample],
    day: date,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
) -> DayCoverage:
    if interval_seconds <= 0:
        raise InputError("interval-seconds 必须为正数")
    day_samples = sorted(
        {sample.timestamp_ms: sample for sample in samples if bucket_date(sample.timestamp_ms) == day}.values(),
        key=lambda item: item.timestamp_ms,
    )
    if not day_samples:
        return DayCoverage(
            day=day,
            sample_count=0,
            coverage_ratio=Decimal("0"),
            max_gap_seconds=Decimal("Infinity"),
            leading_gap_seconds=Decimal("Infinity"),
            trailing_gap_seconds=Decimal("Infinity"),
            qualified=False,
            reasons=("没有样本",),
        )
    start_ms = day_start_ms(day)
    end_ms = day_end_exclusive_ms(day)
    first_ms = day_samples[0].timestamp_ms
    last_ms = day_samples[-1].timestamp_ms
    leading = Decimal(first_ms - start_ms) / Decimal(1000)
    trailing = Decimal(end_ms - last_ms) / Decimal(1000)
    gaps = [
        Decimal(current.timestamp_ms - previous.timestamp_ms) / Decimal(1000)
        for previous, current in zip(day_samples, day_samples[1:])
    ]
    max_gap = max(gaps, default=Decimal("Infinity"))
    missing_seconds = leading + trailing
    missing_seconds += sum(
        (gap - Decimal(interval_seconds) for gap in gaps if gap > interval_seconds),
        Decimal("0"),
    )
    coverage = max(Decimal("0"), Decimal("1") - missing_seconds / Decimal(86400))
    reasons: list[str] = []
    if coverage < Decimal("0.99"):
        reasons.append("覆盖率低于 99%")
    if max_gap > Decimal("30"):
        reasons.append("最大采样缺口超过 30 秒")
    if leading > Decimal("10") or trailing > Decimal("10"):
        reasons.append("UTC 日界线两侧最近样本超过 10 秒")
    qualified = not reasons and len(day_samples) >= 2
    if len(day_samples) < 2:
        reasons.append("样本少于 2 个")
    return DayCoverage(
        day=day,
        sample_count=len(day_samples),
        coverage_ratio=coverage,
        max_gap_seconds=max_gap,
        leading_gap_seconds=leading,
        trailing_gap_seconds=trailing,
        qualified=qualified,
        reasons=tuple(reasons),
    )


def qualified_day_coverages(
    samples: Sequence[LiveSample],
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    candidate_days: Iterable[date] | None = None,
    exclude_day: date | None = None,
) -> list[DayCoverage]:
    days = {bucket_date(sample.timestamp_ms) for sample in samples}
    if candidate_days is not None:
        days &= set(candidate_days)
    if exclude_day is not None:
        days.discard(exclude_day)
    coverages = [analyze_day_coverage(samples, day, interval_seconds) for day in sorted(days)]
    return [coverage for coverage in coverages if coverage.qualified]


def read_snapshot(path: Path) -> list[LiveSample]:
    if not path.exists():
        return []
    if not path.is_file():
        raise InputError(f"采样文件不是普通文件: {path}")
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration as exc:
                raise InputError("采样文件为空") from exc
            if tuple(header) != RAW_HEADER:
                raise InputError(f"采样文件表头必须为 {list(RAW_HEADER)!r}")
            by_timestamp: dict[int, LiveSample] = {}
            for line_number, row in enumerate(reader, start=2):
                if not row or all(not cell.strip() for cell in row):
                    continue
                if len(row) != len(RAW_HEADER):
                    raise InputError(f"采样文件第 {line_number} 行列数无效")
                try:
                    # The CSV stores an ISO timestamp for human readability.
                    timestamp_ms = parse_snapshot_timestamp(row[0])
                    validate_exact({"symbol": row[1]}, "symbol", SYMBOL)
                    open_interest = parse_contract_decimal(row[2], "采样 open_interest_contracts")
                except ValidationError as exc:
                    raise InputError(f"采样文件第 {line_number} 行: {exc}") from exc
                sample = LiveSample(timestamp_ms, SYMBOL, PAIR, CONTRACT_TYPE, open_interest)
                previous = by_timestamp.get(timestamp_ms)
                if previous is not None and previous.open_interest != open_interest:
                    raise InputError(f"采样文件时间戳重复且数值冲突: {timestamp_ms}")
                by_timestamp[timestamp_ms] = sample
    except csv.Error as exc:
        raise InputError(f"采样文件解析失败: {exc}") from exc
    return [by_timestamp[key] for key in sorted(by_timestamp)]


def parse_snapshot_timestamp(value: str) -> int:
    text = value.strip()
    if not text.endswith("Z"):
        raise ValidationError("采样 timestamp 必须为 UTC ISO 时间")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationError("采样 timestamp 不是有效 UTC ISO 时间") from exc
    if parsed.tzinfo is None:
        raise ValidationError("采样 timestamp 缺少时区")
    return int(parsed.timestamp() * 1000)


def append_snapshot(
    path: Path,
    sample: LiveSample,
    known_samples: dict[int, LiveSample] | None = None,
) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    by_timestamp = known_samples if known_samples is not None else {
        item.timestamp_ms: item for item in read_snapshot(path)
    }
    previous = by_timestamp.get(sample.timestamp_ms)
    if previous is not None:
        if previous.open_interest != sample.open_interest:
            raise InputError(f"采样时间戳已有不同 OI 值: {sample.timestamp_ms}")
        return False
    needs_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        if needs_header:
            writer.writerow(RAW_HEADER)
        writer.writerow(
            (
                format_timestamp(sample.timestamp_ms),
                SYMBOL,
                decimal_to_string(sample.open_interest),
            )
        )
    by_timestamp[sample.timestamp_ms] = sample
    return True


def relative_error(actual: Decimal, expected: Decimal) -> tuple[Decimal | None, Decimal | None]:
    difference = abs(actual - expected)
    if expected == 0:
        if difference == 0:
            return Decimal("0"), Decimal("0")
        return None, None
    ratio = difference / abs(expected)
    return ratio, ratio * Decimal(10000)


def compare_bars(
    tv_bar: OIBar,
    binance_bar: OIBar,
    open_close_tolerance_bps: Decimal = DEFAULT_OPEN_CLOSE_BPS,
    high_low_tolerance_bps: Decimal = DEFAULT_HIGH_LOW_BPS,
) -> list[ComparisonMetric]:
    metrics: list[ComparisonMetric] = []
    for field, tv_value, binance_value in zip(
        ("open", "high", "low", "close"), tv_bar.values(), binance_bar.values()
    ):
        tolerance = high_low_tolerance_bps if field in {"high", "low"} else open_close_tolerance_bps
        ratio, error_bps = relative_error(tv_value, binance_value)
        within = error_bps is not None and error_bps <= tolerance
        metrics.append(
            ComparisonMetric(
                field=field,
                tv_value=tv_value,
                binance_value=binance_value,
                difference_contracts=tv_value - binance_value,
                absolute_difference_contracts=abs(tv_value - binance_value),
                relative_error=ratio,
                error_bps=error_bps,
                tolerance_bps=tolerance,
                within_tolerance=within,
            )
        )
    return metrics


def filter_rows_by_days(rows: Sequence[TVRow], days: Iterable[date]) -> dict[date, TVRow]:
    allowed = set(days)
    return {row.day: row for row in rows if row.day in allowed}


def serialize_request_log(client: BinanceHTTPClient) -> list[dict[str, Any]]:
    return [
        {
            "method": item["method"],
            "path": item["path"],
            "params": {key: str(value) for key, value in item["params"].items()},
        }
        for item in client.requests
    ]


def utc_now_string(now: datetime | None = None) -> str:
    value = now or datetime.now(UTC)
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def write_report(
    report: Mapping[str, Any],
    out_dir: Path,
    prefix: str,
    generated_at: datetime | None = None,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = (generated_at or datetime.now(UTC)).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"{prefix}-{stamp}.json"
    markdown_path = out_dir / f"{prefix}-{stamp}.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(report_to_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def report_to_markdown(report: Mapping[str, Any]) -> str:
    conclusion = report.get("conclusion", "UNKNOWN")
    lines = [
        f"# Binance BTCUSD COIN-M OI 核验报告: {conclusion}",
        "",
        f"- 生成时间（UTC）: `{report.get('generated_at_utc', '')}`",
        f"- 数据源: `{report.get('source_kind', '')}`",
        f"- 退出码: `{report.get('exit_code', '')}`",
    ]
    if report.get("csv_sha256"):
        lines.append(f"- TradingView CSV SHA-256: `{report['csv_sha256']}`")
    if report.get("snapshot_sha256"):
        lines.append(f"- 原始采样 SHA-256: `{report['snapshot_sha256']}`")
    reasons = report.get("reasons") or report.get("limitations") or []
    if reasons:
        lines.extend(["", "## 结论与限制", ""])
        lines.extend(f"- {reason}" for reason in reasons)
    coverages = report.get("coverage") or []
    if coverages:
        lines.extend(["", "## 每日覆盖", "", "| 日期 | 样本数 | 覆盖率 | 最大缺口秒 | 合格 |", "| --- | ---: | ---: | ---: | --- |"])
        for item in coverages:
            lines.append(
                f"| {item.get('date')} | {item.get('sample_count')} | "
                f"{item.get('coverage_percent', '')}% | {item.get('max_gap_seconds')} | "
                f"{'是' if item.get('qualified') else '否'} |"
            )
    comparisons = report.get("comparisons") or []
    if comparisons:
        lines.extend(["", "## 逐日误差", ""])
        for comparison in comparisons:
            lines.extend([f"### {comparison.get('date')}", "", "| 字段 | TV | Binance | 差值（TV-Binance） | 误差 bps | 容差 bps |", "| --- | ---: | ---: | ---: | ---: | ---: |"])
            for metric in comparison.get("metrics", []):
                lines.append(
                    f"| {metric.get('field')} | {metric.get('tv_value_contracts')} | "
                    f"{metric.get('binance_value_contracts')} | "
                    f"{metric.get('difference_contracts_tv_minus_binance')} | "
                    f"{metric.get('error_bps') or 'N/A'} | {metric.get('tolerance_bps')} |"
                )
    if report.get("requests"):
        lines.extend(["", "## 请求参数", "", "```json", json.dumps(report["requests"], ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines) + "\n"


def fetch_history_windowed(
    api: BinanceOIAPI,
    period: str,
    start_time_ms: int,
    end_time_ms: int,
    limit: int = 500,
) -> list[HistoricalSample]:
    return paginate_history(
        lambda start, end, page_limit: api.fetch_history(period, start, end, page_limit),
        start_time_ms,
        end_time_ms,
        period,
        limit,
    )


def build_historical_report(
    csv_path: Path,
    rows: Sequence[TVRow],
    daily_samples: Sequence[HistoricalSample],
    five_minute_samples: Sequence[HistoricalSample],
    client: BinanceHTTPClient,
    days: int,
    now: datetime,
) -> dict[str, Any]:
    completed_end = now.astimezone(UTC).date() - timedelta(days=1)
    start_day = completed_end - timedelta(days=days - 1)
    tv_by_day = filter_rows_by_days(rows, (start_day + timedelta(days=i) for i in range(days)))
    daily_by_day = aggregate_oi_bars(daily_samples)
    five_by_day = aggregate_oi_bars(five_minute_samples)
    comparisons: list[dict[str, Any]] = []
    for day in sorted(set(tv_by_day) & set(five_by_day)):
        tv_bar = tv_by_day[day].oi
        five_bar = five_by_day[day]
        metrics = compare_bars(tv_bar, five_bar)
        daily_close_metric: list[dict[str, Any]] = []
        if day in daily_by_day:
            daily_close_metric = [metric.as_dict() for metric in compare_bars(
                OIBar(tv_bar.close, tv_bar.close, tv_bar.close, tv_bar.close),
                OIBar(daily_by_day[day].close, daily_by_day[day].close, daily_by_day[day].close, daily_by_day[day].close),
            ) if metric.field == "close"]
        comparisons.append(
            {
                "date": day.isoformat(),
                "source": "5m_history_approximate_daily_ohlc",
                "metrics": [metric.as_dict() for metric in metrics],
                "daily_close_diagnostic": daily_close_metric,
                "all_within_tolerance": all(metric.within_tolerance for metric in metrics),
            }
        )
    report: dict[str, Any] = {
        "generated_at_utc": utc_now_string(now),
        "source_kind": "historical_statistics_diagnostic",
        "conclusion": "INCONCLUSIVE",
        "exit_code": EXIT_INCONCLUSIVE,
        "csv_sha256": sha256_file(csv_path),
        "csv_path": str(csv_path),
        "requested_days": days,
        "date_range_utc": {"start": start_day.isoformat(), "end": completed_end.isoformat()},
        "daily_record_count": len(daily_samples),
        "five_minute_record_count": len(five_minute_samples),
        "tv_record_count_in_range": len(tv_by_day),
        "daily_dates": sorted(day.isoformat() for day in daily_by_day),
        "five_minute_dates": sorted(day.isoformat() for day in five_by_day),
        "comparisons": comparisons,
        "requests": serialize_request_log(client),
        "reasons": [
            "历史接口返回的是 openInterestHist 统计快照，不是实时单合约账本流。",
            "历史结果只用于诊断，不能作为 TradingView 数据真实性 PASS/FAIL 依据。",
            "5m 统计点聚合为日线 OHLC 只是近似，不能替代前瞻实时采样。",
        ],
        "limitations": [
            "Binance 历史接口仅保留最近 30 天。",
            "只读取 sumOpenInterest contracts；未读取或比较 sumOpenInterestValue 基础资产口径。",
        ],
    }
    return report


def run_historical(args: argparse.Namespace) -> int:
    csv_path = Path(args.csv)
    if not 1 <= args.days <= 30:
        raise InputError("historical --days 必须在 1..30；Binance 历史接口只保留最近 30 天")
    rows = read_tradingview_csv(csv_path, UTC)
    now = datetime.now(UTC)
    end_day = now.date() - timedelta(days=1)
    start_day = end_day - timedelta(days=args.days - 1)
    start_ms = day_start_ms(start_day)
    end_ms = day_end_exclusive_ms(end_day) - 1
    client = BinanceHTTPClient(
        base_url=args.base_url,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
    )
    api = BinanceOIAPI(client)
    daily_samples = fetch_history_windowed(api, "1d", start_ms, end_ms)
    five_minute_samples = fetch_history_windowed(api, "5m", start_ms, end_ms)
    raw_dir = Path(args.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"historical-{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    raw_path.write_text(
        json.dumps(
            {
                "generated_at_utc": utc_now_string(now),
                "symbol": SYMBOL,
                "pair": PAIR,
                "contract_type": CONTRACT_TYPE,
                "daily": [item.as_dict() for item in daily_samples],
                "five_minute": [item.as_dict() for item in five_minute_samples],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    report = build_historical_report(csv_path, rows, daily_samples, five_minute_samples, client, args.days, now)
    report["raw_path"] = str(raw_path)
    json_path, markdown_path = write_report(report, Path(args.out_dir), "binance-oi-historical", now)
    print(f"INCONCLUSIVE: 历史诊断完成；不会作为真实性通过/失败依据。")
    print(f"raw: {raw_path}")
    print(f"json: {json_path}")
    print(f"markdown: {markdown_path}")
    return EXIT_INCONCLUSIVE


def build_compare_report(
    csv_path: Path,
    snapshot_path: Path,
    rows: Sequence[TVRow],
    samples: Sequence[LiveSample],
    interval_seconds: int,
    target_days: int,
    timezone_name: str,
    now: datetime,
    open_close_bps: Decimal,
    high_low_bps: Decimal,
) -> dict[str, Any]:
    current_day = now.astimezone(UTC).date()
    coverage = qualified_day_coverages(samples, interval_seconds, exclude_day=current_day)
    selected_coverage = coverage[:target_days]
    selected_days = [item.day for item in selected_coverage]
    bars = aggregate_oi_bars(samples)
    tv_by_day = filter_rows_by_days(rows, selected_days)
    comparisons: list[dict[str, Any]] = []
    missing_tv = [day.isoformat() for day in selected_days if day not in tv_by_day]
    for item in selected_coverage:
        if item.day not in tv_by_day or item.day not in bars:
            continue
        metrics = compare_bars(tv_by_day[item.day].oi, bars[item.day], open_close_bps, high_low_bps)
        comparisons.append(
            {
                "date": item.day.isoformat(),
                "metrics": [metric.as_dict() for metric in metrics],
                "all_within_tolerance": all(metric.within_tolerance for metric in metrics),
            }
        )
    all_coverage = [item.as_dict() for item in coverage]
    reasons: list[str] = []
    if timezone_name.strip().upper() not in {"UTC", "Z", "GMT", "ETC/UTC"}:
        reasons.append("前瞻核验必须使用 UTC 时区")
    if len(selected_coverage) < target_days:
        reasons.append(f"覆盖合格日只有 {len(selected_coverage)} 天，目标为 {target_days} 天")
    if missing_tv:
        reasons.append("TradingView CSV 缺少合格采样日: " + ", ".join(missing_tv))
    if len(comparisons) < target_days:
        reasons.append("可对齐比较日不足目标天数")
    all_values_pass = len(comparisons) == target_days and all(
        comparison["all_within_tolerance"] for comparison in comparisons
    )
    if not reasons and all_values_pass:
        conclusion = "PASS"
        exit_code = EXIT_PASS
    elif len(selected_coverage) >= target_days and not missing_tv and len(comparisons) >= target_days:
        conclusion = "FAIL"
        exit_code = EXIT_FAIL
    else:
        conclusion = "INCONCLUSIVE"
        exit_code = EXIT_INCONCLUSIVE
    return {
        "generated_at_utc": utc_now_string(now),
        "source_kind": "realtime_open_interest",
        "symbol": SYMBOL,
        "pair": PAIR,
        "contract_type": CONTRACT_TYPE,
        "timezone": timezone_name,
        "conclusion": conclusion,
        "exit_code": exit_code,
        "csv_path": str(csv_path),
        "csv_sha256": sha256_file(csv_path),
        "snapshot_path": str(snapshot_path),
        "snapshot_sha256": sha256_file(snapshot_path),
        "interval_seconds": interval_seconds,
        "target_days": target_days,
        "tolerances_bps": {
            "open": decimal_to_string(open_close_bps),
            "close": decimal_to_string(open_close_bps),
            "high": decimal_to_string(high_low_bps),
            "low": decimal_to_string(high_low_bps),
        },
        "sample_count": len(samples),
        "coverage": all_coverage,
        "selected_dates": [day.isoformat() for day in selected_days],
        "comparisons": comparisons,
        "reasons": reasons,
        "limitations": [
            "PASS 仅表示 TradingView 数据与 Binance 公开实时 API 在本次样本和容差内一致。",
            "PASS 不证明 Binance 内部账本绝对真实，也不代表全市场或 Binance 全部 BTC OI。",
            "只比较 openInterest contracts 张数；不比较 sumOpenInterestValue 基础资产口径。",
        ],
    }


def run_compare(args: argparse.Namespace) -> int:
    timezone_value = parse_timezone(args.timezone)
    if args.target_days <= 0:
        raise InputError("compare --target-days 必须为正数")
    if args.interval_seconds <= 0:
        raise InputError("compare --interval-seconds 必须为正数")
    if args.open_close_bps < 0 or args.high_low_bps < 0:
        raise InputError("比较容差不能为负数")
    csv_path = Path(args.csv)
    snapshot_path = Path(args.snapshot_file)
    rows = read_tradingview_csv(csv_path, timezone_value)
    samples = read_snapshot(snapshot_path)
    report = build_compare_report(
        csv_path,
        snapshot_path,
        rows,
        samples,
        args.interval_seconds,
        args.target_days,
        args.timezone,
        datetime.now(UTC),
        args.open_close_bps,
        args.high_low_bps,
    )
    json_path, markdown_path = write_report(report, Path(args.out_dir), "binance-oi-compare")
    print(f"{report['conclusion']}: compare 完成。")
    print(f"json: {json_path}")
    print(f"markdown: {markdown_path}")
    return int(report["exit_code"])


def collection_window(samples: Sequence[LiveSample], now: datetime, max_days: int) -> tuple[date, date]:
    if samples:
        first_day = min(bucket_date(sample.timestamp_ms) for sample in samples)
    else:
        first_day = now.astimezone(UTC).date()
    start_day = first_day + timedelta(days=1)
    end_day = start_day + timedelta(days=max_days - 1)
    return start_day, end_day


def collect_samples(
    api: BinanceOIAPI,
    snapshot_path: Path,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    target_days: int = DEFAULT_TARGET_DAYS,
    max_days: int = DEFAULT_MAX_DAYS,
    now_fn: Callable[[], datetime] | None = None,
    sleep_fn: Callable[[float], None] | None = None,
    max_iterations: int | None = None,
    monotonic_fn: Callable[[], float] | None = None,
) -> tuple[list[LiveSample], list[DayCoverage], str]:
    """Collect realtime samples until enough complete days or the window ends.

    The first observed UTC day is deliberately excluded from the qualification
    window.  This makes a newly started collector wait for the next complete
    UTC day instead of treating a partial first day as acceptance evidence.
    """

    if interval_seconds <= 0 or target_days <= 0 or max_days < target_days:
        raise InputError("collect 参数必须满足 interval>0、target>0、max-days>=target-days")
    now_fn = now_fn or (lambda: datetime.now(UTC))
    sleep_fn = sleep_fn or time.sleep
    monotonic_fn = monotonic_fn or time.monotonic
    samples = read_snapshot(snapshot_path)
    known_samples = {sample.timestamp_ms: sample for sample in samples}
    iterations = 0
    next_due = monotonic_fn()
    while True:
        now = now_fn().astimezone(UTC)
        start_day, end_day = collection_window(samples, now, max_days)
        eligible_days = (start_day + timedelta(days=i) for i in range(max_days))
        coverages = qualified_day_coverages(
            samples,
            interval_seconds,
            candidate_days=eligible_days,
            exclude_day=now.date(),
        )
        if len(coverages) >= target_days:
            return samples, coverages[:target_days], "ready_for_compare"
        if now.date() > end_day:
            return samples, coverages, "max_days_reached"
        if max_iterations is not None and iterations >= max_iterations:
            return samples, coverages, "iteration_limit_reached"
        sample = api.fetch_live(received_at=now)
        if append_snapshot(snapshot_path, sample, known_samples):
            samples.append(sample)
            samples.sort(key=lambda item: item.timestamp_ms)
        iterations += 1
        next_due += interval_seconds
        sleep_fn(max(0.0, next_due - monotonic_fn()))


def run_collect(args: argparse.Namespace) -> int:
    client = BinanceHTTPClient(
        base_url=args.base_url,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
    )
    api = BinanceOIAPI(client)
    snapshot_path = Path(args.snapshot_file)
    try:
        samples, coverages, status = collect_samples(
            api,
            snapshot_path,
            args.interval_seconds,
            args.target_days,
            args.max_days,
            max_iterations=args.max_iterations,
        )
    except KeyboardInterrupt:
        print("INCONCLUSIVE: 已中断；已写入的采样可从 snapshot-file 续传。", file=sys.stderr)
        return EXIT_INCONCLUSIVE
    print(f"INCONCLUSIVE: collect 状态={status}，样本 {len(samples)} 条，合格日 {len(coverages)} 天。")
    print(f"snapshot: {snapshot_path}")
    if len(coverages) >= args.target_days:
        print("采样已覆盖目标天数；请重新导出覆盖这些 UTC 日的 TradingView CSV 后运行 compare。")
    return EXIT_INCONCLUSIVE


class ValidationArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InputError(message)


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("必须是整数") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("必须为正数")
    return parsed


def nonnegative_decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("必须是数字") from exc
    if not parsed.is_finite() or parsed < 0:
        raise argparse.ArgumentTypeError("必须是非负有限数字")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = ValidationArgumentParser(
        description="只读核验 TradingView OI OHLC 与 Binance BTCUSD_PERP COIN-M contracts"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    historical = subparsers.add_parser("historical", help="历史诊断，不产生真实性 PASS/FAIL")
    historical.add_argument("--csv", required=True)
    historical.add_argument("--days", type=positive_int, default=30)
    historical.add_argument("--out-dir", default=str(DEFAULT_REPORT_DIR))
    historical.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR))
    add_api_arguments(historical)

    collect = subparsers.add_parser("collect", help="每 interval 秒采集实时 OI 并支持续传")
    collect.add_argument("--snapshot-file", required=True)
    collect.add_argument("--interval-seconds", type=positive_int, default=DEFAULT_INTERVAL_SECONDS)
    collect.add_argument("--target-days", type=positive_int, default=DEFAULT_TARGET_DAYS)
    collect.add_argument("--max-days", type=positive_int, default=DEFAULT_MAX_DAYS)
    collect.add_argument("--max-iterations", type=positive_int, default=None)
    add_api_arguments(collect)

    compare = subparsers.add_parser("compare", help="比较实时采样与 TradingView UTC 日线 CSV")
    compare.add_argument("--csv", required=True)
    compare.add_argument("--snapshot-file", required=True)
    compare.add_argument("--timezone", required=True)
    compare.add_argument("--target-days", type=positive_int, default=DEFAULT_TARGET_DAYS)
    compare.add_argument("--interval-seconds", type=positive_int, default=DEFAULT_INTERVAL_SECONDS)
    compare.add_argument("--open-close-bps", type=nonnegative_decimal, default=DEFAULT_OPEN_CLOSE_BPS)
    compare.add_argument("--high-low-bps", type=nonnegative_decimal, default=DEFAULT_HIGH_LOW_BPS)
    compare.add_argument("--out-dir", default=str(DEFAULT_REPORT_DIR))
    return parser


def add_api_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-url", default=API_BASE_URL)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if hasattr(args, "timeout") and args.timeout <= 0:
            raise InputError("--timeout 必须为正数")
        if hasattr(args, "max_retries") and args.max_retries < 0:
            raise InputError("--max-retries 不能为负数")
        if args.command == "historical":
            return run_historical(args)
        if args.command == "collect":
            return run_collect(args)
        if args.command == "compare":
            return run_compare(args)
        raise InputError(f"未知命令: {args.command}")
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except APIError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except OSError as exc:
        print(f"ERROR: 文件操作失败: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
