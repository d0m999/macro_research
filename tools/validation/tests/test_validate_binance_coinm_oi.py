from __future__ import annotations

import io
import json
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError


MODULE_DIR = Path(__file__).resolve().parents[1]
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import validate_binance_coinm_oi as validator


UTC = timezone.utc


def tv_header() -> list[str]:
    return [
        "time",
        "open",
        "high",
        "low",
        "close",
        "EMA 1",
        "EMA 2",
        "EMA 3",
        "EMA 4",
        "OI OHLC（原生合约张数） (开盘价)",
        "OI OHLC（原生合约张数） (最高价",
        "OI OHLC（原生合约张数） (最低价)",
        "OI OHLC（原生合约张数） (关闭)",
        "Crypto Open Interest (开盘价)",
        "Crypto Open Interest (最高价",
        "Crypto Open Interest (最低价)",
        "Crypto Open Interest (关闭)",
    ]


def tv_row(day: date, values: tuple[str, str, str, str] = ("100", "110", "90", "105")) -> list[str]:
    return [
        day.isoformat(),
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        *values,
        "not-used",
        "not-used",
        "not-used",
        "not-used",
    ]


def write_tv_csv(path: Path, rows: list[list[str]]) -> None:
    import csv

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(tv_header())
        writer.writerows(rows)


def sample_at(day: date, seconds: int, value: int | str = 100) -> validator.LiveSample:
    timestamp = validator.day_start_ms(day) + seconds * 1000
    return validator.LiveSample(timestamp, validator.SYMBOL, validator.PAIR, validator.CONTRACT_TYPE, Decimal(str(value)))


def full_day_samples(day: date, value: int = 100, interval: int = 30) -> list[validator.LiveSample]:
    seconds = list(range(5, 86400, interval))
    if seconds[-1] != 86395:
        seconds.append(86395)
    return [sample_at(day, second, value) for second in seconds]


class FakeResponse:
    def __init__(self, payload: object, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self.status = status
        self.headers = headers or {}
        self.body = json.dumps(payload).encode("utf-8") if not isinstance(payload, bytes) else payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


class FakeOpener:
    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, *_: object, **__: object) -> object:
        self.calls += 1
        if not self.outcomes:
            raise AssertionError("unexpected HTTP call")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class ValidatorTests(unittest.TestCase):
    def test_chinese_header_and_only_columns_10_to_13_are_read(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tv.csv"
            write_tv_csv(path, [tv_row(date(2026, 8, 1), ("123", "456", "100", "234"))])
            rows = validator.read_tradingview_csv(path, UTC)
        self.assertEqual(rows[0].oi, validator.OIBar(Decimal(123), Decimal(456), Decimal(100), Decimal(234)))

    def test_csv_wrong_column_count_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tv.csv"
            write_tv_csv(path, [tv_row(date(2026, 8, 1))[:-1]])
            with self.assertRaises(validator.InputError):
                validator.read_tradingview_csv(path, UTC)

    def test_csv_missing_value_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tv.csv"
            row = tv_row(date(2026, 8, 1))
            row[10] = ""
            write_tv_csv(path, [row])
            with self.assertRaises(validator.InputError):
                validator.read_tradingview_csv(path, UTC)

    def test_csv_duplicate_date_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "tv.csv"
            day = date(2026, 8, 1)
            write_tv_csv(path, [tv_row(day), tv_row(day)])
            with self.assertRaises(validator.InputError):
                validator.read_tradingview_csv(path, UTC)

    def test_contract_count_must_be_integer(self) -> None:
        self.assertEqual(validator.parse_contract_decimal("12055716.00000000", "openInterest"), Decimal(12055716))
        with self.assertRaises(validator.ValidationError):
            validator.parse_contract_decimal("1.5", "openInterest")
        with self.assertRaises(validator.ValidationError):
            validator.parse_contract_decimal("NaN", "openInterest")

    def test_midnight_period_end_belongs_to_previous_utc_day(self) -> None:
        day = date(2026, 8, 1)
        midnight = validator.day_start_ms(day)
        self.assertEqual(validator.bucket_date(midnight), date(2026, 7, 31))
        self.assertEqual(validator.bucket_date(validator.day_end_exclusive_ms(day)), day)
        self.assertEqual(validator.bucket_date(validator.day_end_exclusive_ms(day) - 1), day)

    def test_pagination_deduplicates_records(self) -> None:
        start = validator.day_start_ms(date(2026, 8, 1))
        end = start + 35 * 60 * 1000
        calls: list[tuple[int, int, int]] = []
        sample = validator.HistoricalSample(
            start + 5 * 60 * 1000,
            validator.PAIR,
            validator.CONTRACT_TYPE,
            Decimal(10),
            {"pair": validator.PAIR, "contractType": validator.CONTRACT_TYPE},
        )

        def fetch_page(page_start: int, page_end: int, limit: int) -> list[validator.HistoricalSample]:
            calls.append((page_start, page_end, limit))
            return [sample, sample]

        result = validator.paginate_history(fetch_page, start, end, "5m", limit=3)
        self.assertEqual(len(calls), 4)
        self.assertEqual(result, [sample])

    def test_http_429_obeys_retry_after(self) -> None:
        error = HTTPError(
            "https://example.invalid",
            429,
            "too many requests",
            {"Retry-After": "2"},
            io.BytesIO(b'{"code":-1003,"msg":"rate limit"}'),
        )
        opener = FakeOpener([error, FakeResponse({"ok": True})])
        sleeps: list[float] = []
        client = validator.BinanceHTTPClient(
            base_url="https://example.invalid",
            max_retries=1,
            backoff_seconds=99,
            opener=opener,
            sleep=sleeps.append,
        )
        self.assertEqual(client.get_json("/test", {}), {"ok": True})
        self.assertEqual(sleeps, [2.0])
        self.assertEqual(opener.calls, 2)

    def test_http_5xx_and_timeout_use_bounded_backoff(self) -> None:
        server_error = HTTPError("https://example.invalid", 503, "unavailable", {}, io.BytesIO(b""))
        opener = FakeOpener([server_error, FakeResponse({"ok": True})])
        sleeps: list[float] = []
        client = validator.BinanceHTTPClient(
            max_retries=1,
            backoff_seconds=3,
            opener=opener,
            sleep=sleeps.append,
        )
        self.assertEqual(client.get_json("/test", {}), {"ok": True})
        self.assertEqual(sleeps, [3])

        timeout_opener = FakeOpener([TimeoutError("timed out"), FakeResponse({"ok": True})])
        timeout_sleeps: list[float] = []
        timeout_client = validator.BinanceHTTPClient(
            max_retries=1,
            backoff_seconds=4,
            opener=timeout_opener,
            sleep=timeout_sleeps.append,
        )
        self.assertEqual(timeout_client.get_json("/test", {}), {"ok": True})
        self.assertEqual(timeout_sleeps, [4])

    def test_invalid_json_is_an_api_error_without_retry(self) -> None:
        opener = FakeOpener([FakeResponse(b"not-json")])
        client = validator.BinanceHTTPClient(opener=opener, max_retries=3, sleep=lambda _: None)
        with self.assertRaises(validator.APIError):
            client.get_json("/test", {})
        self.assertEqual(opener.calls, 1)

    def test_live_response_rejects_wrong_contract_and_fractional_oi(self) -> None:
        wrong_contract = FakeResponse(
            {
                "symbol": validator.SYMBOL,
                "pair": validator.PAIR,
                "contractType": "CURRENT_QUARTER",
                "openInterest": "10",
                "time": 1770000000000,
            }
        )
        api = validator.BinanceOIAPI(validator.BinanceHTTPClient(opener=FakeOpener([wrong_contract])))
        with self.assertRaises(validator.APIError):
            api.fetch_live()

        fractional = FakeResponse(
            {
                "symbol": validator.SYMBOL,
                "pair": validator.PAIR,
                "contractType": validator.CONTRACT_TYPE,
                "openInterest": "10.5",
                "time": 1770000000000,
            }
        )
        api = validator.BinanceOIAPI(validator.BinanceHTTPClient(opener=FakeOpener([fractional])))
        with self.assertRaises(validator.APIError):
            api.fetch_live()

    def test_coverage_requires_boundaries_and_gap_limit(self) -> None:
        day = date(2026, 8, 1)
        good = validator.analyze_day_coverage(full_day_samples(day), day, interval_seconds=30)
        self.assertTrue(good.qualified)
        self.assertGreaterEqual(good.coverage_ratio, Decimal("0.99"))

        sparse = [sample_at(day, 5), sample_at(day, 40), sample_at(day, 86395)]
        bad_gap = validator.analyze_day_coverage(sparse, day, interval_seconds=5)
        self.assertFalse(bad_gap.qualified)
        self.assertIn("最大采样缺口超过 30 秒", bad_gap.reasons)

        bad_boundary = [sample_at(day, 11), sample_at(day, 86400 - 11)]
        boundary = validator.analyze_day_coverage(bad_boundary, day, interval_seconds=5)
        self.assertFalse(boundary.qualified)
        self.assertIn("UTC 日界线两侧最近样本超过 10 秒", boundary.reasons)

    def test_current_activity_day_is_excluded_from_qualification(self) -> None:
        current = date(2026, 8, 25)
        previous = current - timedelta(days=1)
        samples = full_day_samples(previous) + full_day_samples(current)
        coverages = validator.qualified_day_coverages(samples, 30, exclude_day=current)
        self.assertEqual([coverage.day for coverage in coverages], [previous])

    def test_snapshot_resume_is_idempotent(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.csv"
            sample = sample_at(date(2026, 8, 1), 5, 123)
            self.assertTrue(validator.append_snapshot(path, sample))
            self.assertFalse(validator.append_snapshot(path, sample))
            loaded = validator.read_snapshot(path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].open_interest, Decimal(123))

    def test_collect_continues_from_existing_snapshot_without_duplicate(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.csv"
            initial = sample_at(date(2026, 8, 1), 5, 100)
            validator.append_snapshot(path, initial)
            next_sample = sample_at(date(2026, 8, 2), 5, 101)

            class FakeAPI:
                def fetch_live(self, received_at: datetime | None = None) -> validator.LiveSample:
                    return next_sample

            samples, coverages, status = validator.collect_samples(
                FakeAPI(),
                path,
                interval_seconds=5,
                target_days=1,
                max_days=14,
                now_fn=lambda: datetime(2026, 8, 2, 12, tzinfo=UTC),
                sleep_fn=lambda _: None,
                max_iterations=1,
            )
            self.assertEqual(status, "iteration_limit_reached")
            self.assertEqual(len(samples), 2)
            self.assertEqual(len(coverages), 0)
            self.assertEqual(len(validator.read_snapshot(path)), 2)

    def test_tolerance_boundaries_are_inclusive(self) -> None:
        tv = validator.OIBar(Decimal("100.1"), Decimal("100.2"), Decimal("99.8"), Decimal("100.1"))
        actual = validator.OIBar(Decimal("100"), Decimal("100"), Decimal("100"), Decimal("100"))
        metrics = validator.compare_bars(tv, actual)
        self.assertTrue(metrics[0].within_tolerance)  # exactly 10 bps
        self.assertTrue(metrics[1].within_tolerance)  # exactly 20 bps
        self.assertTrue(metrics[2].within_tolerance)  # exactly 20 bps
        self.assertTrue(metrics[3].within_tolerance)

        fail = validator.compare_bars(
            validator.OIBar(Decimal("100.11"), Decimal("100.21"), Decimal("99.79"), Decimal("100.11")),
            actual,
        )
        self.assertFalse(fail[0].within_tolerance)
        self.assertFalse(fail[1].within_tolerance)

    def test_compare_report_passes_only_selected_complete_days(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            csv_path = root / "tv.csv"
            snapshot_path = root / "snapshot.csv"
            current = date(2026, 8, 25)
            previous = current - timedelta(days=1)
            write_tv_csv(csv_path, [tv_row(previous, ("100", "100", "100", "100")), tv_row(current)])
            all_samples = full_day_samples(previous) + full_day_samples(current)
            with snapshot_path.open("w", encoding="utf-8", newline="") as handle:
                import csv

                writer = csv.writer(handle, lineterminator="\n")
                writer.writerow(validator.RAW_HEADER)
                for sample in all_samples:
                    writer.writerow((validator.format_timestamp(sample.timestamp_ms), validator.SYMBOL, "100"))
            report = validator.build_compare_report(
                csv_path,
                snapshot_path,
                validator.read_tradingview_csv(csv_path, UTC),
                validator.read_snapshot(snapshot_path),
                interval_seconds=30,
                target_days=1,
                timezone_name="UTC",
                now=datetime(2026, 8, 25, 12, tzinfo=UTC),
                open_close_bps=Decimal(10),
                high_low_bps=Decimal(20),
            )
            self.assertEqual(report["conclusion"], "PASS")
            self.assertEqual(report["selected_dates"], [previous.isoformat()])


if __name__ == "__main__":
    unittest.main()
