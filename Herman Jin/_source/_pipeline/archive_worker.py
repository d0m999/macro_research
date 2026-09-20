#!/usr/bin/env python3
"""串行执行 Herman Jin 视频归档。

这个 worker 只服务于当前归档任务：每次只处理一个视频、一个阶段、一个
外部子进程。完整视频只放在本机临时目录，正式包验收并发布后立即清理。
"""

from __future__ import annotations

import argparse
import bisect
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageEnhance


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE_ROOT = ROOT / "Herman Jin"
ARCHIVE = ARCHIVE_ROOT / "market-overview"
PIPELINE = ARCHIVE_ROOT / "_source" / "_pipeline"
INVENTORY_PATH = PIPELINE / "inventory.jsonl"
STATE_PATH = PIPELINE / "state.json"
STAGING = PIPELINE / "staging"
INDEX_PATH = ARCHIVE_ROOT / "agent-index.json"

YTDLP = Path("/Library/Frameworks/Python.framework/Versions/3.10/bin/yt-dlp")
PYTHON = Path("/Library/Frameworks/Python.framework/Versions/3.10/bin/python3")
FFMPEG = Path("/usr/local/bin/ffmpeg")
FFPROBE = Path("/usr/local/bin/ffprobe")
TESSERACT = Path("/usr/local/bin/tesseract")
TASKPOLICY = Path("/usr/sbin/taskpolicy")
NICE = Path("/usr/bin/nice")

MODEL_GLOB = Path.home() / ".cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/*"

TRANSCRIBE_WORKER = PIPELINE / "transcribe_worker.py"

DOWNLOAD_CPU_GATE = 40.0
PROCESS_CPU_GATE = 40.0
PAUSE_CPU_GATE = 35.0
# --- 2026-09-16 临时放宽记录（已复原，非当前值）---
# 当天为补录 09-01 / 09-15 两期曾把启动阈值 35.0 下调为 28.0：
# 本机 16 GiB 内存 + swap 已用 18+ GiB，memory_pressure 的 free percentage 长时间钉在 31-33%，
# 连续 25 分钟以上拿不到 3 次 >=35% 采样（CPU idle 与磁盘均充裕，唯一卡点即内存）。
# 硬保护 MEMORY_ABORT 全程未动（始终 20.0）。
# **两期跑完后已于 2026-09-16 复原为 35.0**；详见 `.workbuddy/memory/2026-09-16.md`。
MEMORY_GATE = 35.0
MEMORY_ABORT = 20.0
# --- 2026-09-15 临时放宽记录（已复原，非当前值）---
# 当天为补录 09-01 / 09-15 两期曾两次临时下调磁盘闸门：25.0 -> 22.0 -> 21.0，
# 原因：可用磁盘低于原阈值，而单期实际占用 <0.5 GiB，属绝对值阈值与实际需求脱钩。
# 硬保护 DISK_ABORT_GIB 全程未动（始终 20.0）。
# **2026-09-15 22:27 用户指示暂停任务时已复原为 25.0**；两期均未跑完，
# 下次续跑需按当时实测空闲重新判断是否放宽，并再次标注与复原。
# 详见 `.workbuddy/memory/2026-09-15.md`。
DISK_GATE_GIB = 25.0
DISK_ABORT_GIB = 20.0
CHECK_INTERVAL = 30

TRANSCRIPT_FIELDS = ["id", "start", "end", "text", "chapter", "source"]
DECK_FIELDS = [
    "id",
    "time_ranges",
    "title",
    "image",
    "ocr_file",
    "ocr",
    "visual_type",
    "summary",
    "source_file",
    "image_format",
]


class PipelineError(RuntimeError):
    def __init__(self, message: str, *, code: str = "failed", retryable: bool = False):
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ResourceInterruption(PipelineError):
    def __init__(self, message: str):
        super().__init__(message, code="resource_gate", retryable=True)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def now_iso() -> str:
    return now_utc().isoformat(timespec="seconds")


def today() -> str:
    return now_utc().date().isoformat()


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False
        ) as handle:
            temp = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def write_json_atomic(path: Path, value: Any) -> None:
    write_text_atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def safe_remove_tree(path: Path) -> None:
    """只删除 worker 明确创建的临时目录。"""

    path = path.resolve()
    allowed_temp_parents = {Path("/tmp").resolve(), Path("/private/tmp").resolve()}
    if path.parent not in allowed_temp_parents or not path.name.startswith("herman-jin-"):
        raise PipelineError(f"拒绝清理未验证的临时目录: {path}", code="unsafe_cleanup")
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    path.rmdir()


def safe_remove_staging_tree(path: Path) -> None:
    """只删除当前 worker 约定的 staging/work-* 目录。"""

    path = path.resolve()
    if path.parent != STAGING.resolve() or not path.name.startswith("work-"):
        raise PipelineError(f"拒绝清理未验证的 staging 目录: {path}", code="unsafe_cleanup")
    if not path.exists():
        return
    for child in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            child.rmdir()
    path.rmdir()


def probe_stdout(command: list[str]) -> str | None:
    """执行系统探测命令；当执行环境禁止调用该命令时返回 None，不抛异常。"""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError:
        return None
    return result.stdout


def cpu_idle_percent() -> float | None:
    """读取 CPU 空闲百分比。

    首选与历史行为一致的 `/usr/bin/top`。部分执行环境（沙箱/无 Full Disk
    Access 的宿主进程）会直接拒绝执行 top，此时退回到 psutil 的等价实现，
    保证闸门语义（空闲百分比 + 相同阈值）不变。
    """
    output = probe_stdout(["/usr/bin/top", "-l", "1", "-n", "0"])
    if output:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)% idle", output)
        if match:
            return float(match.group(1))
    try:
        import psutil
    except ImportError:
        return None
    return float(psutil.cpu_times_percent(interval=1.0).idle)


def resource_snapshot() -> dict[str, Any]:
    cpu_idle = cpu_idle_percent()

    memory_free = None
    memory_output = probe_stdout(["/usr/bin/memory_pressure", "-Q"])
    if memory_output is None:
        try:
            import psutil

            memory_free = float(psutil.virtual_memory().available / psutil.virtual_memory().total * 100)
        except ImportError:
            memory_free = None
    else:
        match = re.search(r"free percentage:\s*([0-9]+)%", memory_output)
        if match:
            memory_free = float(match.group(1))

    swapouts = None
    vm_output = probe_stdout(["/usr/bin/vm_stat"])
    if vm_output is None:
        try:
            import psutil

            swapouts = int(psutil.swap_memory().sout)
        except ImportError:
            swapouts = None
    else:
        match = re.search(r"Swapouts:\s*([0-9]+)", vm_output)
        if match:
            swapouts = int(match.group(1))

    usage = shutil.disk_usage(ROOT)
    disk_free_gib = usage.free / (1024**3)
    return {
        "cpu_idle_percent": cpu_idle,
        "memory_free_percent": memory_free,
        "swapouts": swapouts,
        "disk_free_gib": round(disk_free_gib, 2),
    }


def gate_ok(snapshot: dict[str, Any], threshold: float, previous_swapouts: int | None) -> bool:
    cpu = snapshot["cpu_idle_percent"]
    memory = snapshot["memory_free_percent"]
    swapouts = snapshot["swapouts"]
    return (
        cpu is not None
        and cpu >= threshold
        and memory is not None
        and memory >= MEMORY_GATE
        and swapouts is not None
        and (previous_swapouts is None or swapouts <= previous_swapouts)
        and snapshot["disk_free_gib"] >= DISK_GATE_GIB
    )


def print_snapshot(label: str, snapshot: dict[str, Any], good: bool) -> None:
    print(
        f"[resource:{label}] cpu_idle={snapshot['cpu_idle_percent']}% "
        f"memory_free={snapshot['memory_free_percent']}% "
        f"swapouts={snapshot['swapouts']} disk_free={snapshot['disk_free_gib']}GiB "
        f"gate={'PASS' if good else 'WAIT'}",
        flush=True,
    )


def wait_for_gate(label: str, threshold: float) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    previous_swapouts: int | None = None
    consecutive = 0
    while consecutive < 3:
        snapshot = resource_snapshot()
        good = gate_ok(snapshot, threshold, previous_swapouts)
        print_snapshot(label, snapshot, good)
        samples.append(snapshot)
        if good:
            consecutive += 1
        else:
            consecutive = 0
        previous_swapouts = snapshot["swapouts"]
        if consecutive < 3:
            time.sleep(CHECK_INTERVAL)
    return samples


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "OMP_THREAD_LIMIT": "1",
        }
    )
    return env


def prioritized_command(command: list[str]) -> list[str]:
    return [str(TASKPOLICY), "-b", str(NICE), "-n", "19", *map(str, command)]


def terminate_process_group(process: subprocess.Popen[Any], sig: signal.Signals) -> None:
    try:
        os.killpg(process.pid, sig)
    except ProcessLookupError:
        pass


def run_logged(
    command: list[str],
    log_path: Path,
    *,
    label: str,
    threshold: float,
    allow_failure: bool = False,
) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"started={now_iso()}\ncommand={' '.join(map(str, command))}\n", encoding="utf-8"
    )
    wrapped = prioritized_command(command)
    with log_path.open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            wrapped,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=command_env(),
            start_new_session=True,
        )
        paused = False
        low_cpu_count = 0
        resume_count = 0
        last_swapouts: int | None = None
        next_resource_check = time.monotonic() + CHECK_INTERVAL
        while True:
            return_code = process.poll()
            if return_code is not None:
                log.write(f"finished={now_iso()} returncode={return_code}\n")
                if return_code != 0 and not allow_failure:
                    raise PipelineError(
                        f"{label} 返回 {return_code}，详见 {log_path}",
                        code="tooling_failure",
                        retryable=True,
                    )
                return return_code

            # 短命令（尤其是单个 Tesseract）应立即返回；只有运行超过
            # CHECK_INTERVAL 的子进程才进入资源采样。
            remaining = next_resource_check - time.monotonic()
            if remaining > 0:
                time.sleep(min(1.0, remaining))
                continue
            next_resource_check = time.monotonic() + CHECK_INTERVAL
            snapshot = resource_snapshot()
            log.write(f"resource={compact_json(snapshot)}\n")
            log.flush()
            cpu = snapshot["cpu_idle_percent"]
            memory = snapshot["memory_free_percent"]
            swapouts = snapshot["swapouts"]
            if memory is not None and memory < MEMORY_ABORT:
                terminate_process_group(process, signal.SIGTERM)
                raise ResourceInterruption(f"{label} 因可用内存低于 {MEMORY_ABORT}% 已终止并重排")
            if snapshot["disk_free_gib"] < DISK_ABORT_GIB:
                terminate_process_group(process, signal.SIGTERM)
                raise ResourceInterruption(f"{label} 因磁盘低于 {DISK_ABORT_GIB}GiB 已终止并重排")
            if swapouts is not None and last_swapouts is not None and swapouts > last_swapouts:
                terminate_process_group(process, signal.SIGTERM)
                raise ResourceInterruption(f"{label} 检测到 swapout 增加，已终止并重排")
            last_swapouts = swapouts

            if cpu is not None and cpu < PAUSE_CPU_GATE:
                low_cpu_count += 1
            else:
                low_cpu_count = 0
            if not paused and low_cpu_count >= 2:
                os.killpg(process.pid, signal.SIGSTOP)
                paused = True
                resume_count = 0
                log.write(f"paused={now_iso()} reason=cpu_idle_below_{PAUSE_CPU_GATE}%\n")
                log.flush()
                continue
            if paused:
                if gate_ok(snapshot, threshold, last_swapouts):
                    resume_count += 1
                else:
                    resume_count = 0
                if resume_count >= 3:
                    os.killpg(process.pid, signal.SIGCONT)
                    paused = False
                    low_cpu_count = 0
                    log.write(f"resumed={now_iso()}\n")
                    log.flush()


def run_capture_to_file(
    command: list[str],
    output_path: Path,
    *,
    label: str,
    threshold: float,
    log_path: Path,
) -> int:
    """让 stdout 进入指定文件，避免 OCR/ffmpeg 输出填满管道。"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(b"")
    # 将 stdout 和 stderr 合并到临时输出文件；调用方读取后再决定用途。
    return run_logged(command, output_path, label=label, threshold=threshold)


def load_inventory() -> list[dict[str, Any]]:
    records = []
    for line in INVENTORY_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def load_state() -> dict[str, Any]:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict[str, Any]) -> None:
    counts = Counter(entry.get("status") for entry in state["entries"].values())
    state["status_counts"] = dict(sorted(counts.items()))
    state["updated_on"] = today()
    write_json_atomic(STATE_PATH, state)


def transition(state: dict[str, Any], video_id: str, status: str, **extra: Any) -> None:
    entry = state["entries"][video_id]
    entry["status"] = status
    entry["last_transition"] = today()
    entry.update(extra)
    save_state(state)


def update_inventory(video_id: str, status: str, **extra: Any) -> None:
    records = load_inventory()
    found = False
    for record in records:
        if record.get("video_id") == video_id:
            record["status"] = status
            record.update(extra)
            if status == "complete":
                for key in ("failure_code", "failure_detail"):
                    record.pop(key, None)
            found = True
            break
    if not found:
        raise PipelineError(f"inventory 中找不到 video_id={video_id}", code="inventory_error")
    write_text_atomic(
        INVENTORY_PATH,
        "".join(compact_json(record) + "\n" for record in records),
    )


def source_paths(package_id: str) -> dict[str, Path]:
    source = ARCHIVE_ROOT / "_source" / package_id
    return {
        "root": source,
        "metadata": source / "metadata",
        "audio": source / "audio",
        "transcript": source / "transcript",
        "frames": source / "frames",
        "selected": source / "frames" / "selected",
        "diagnostics": source / "diagnostics",
    }


def ensure_source_dirs(package_id: str) -> dict[str, Path]:
    paths = source_paths(package_id)
    for key in ("metadata", "audio", "transcript", "frames", "selected", "diagnostics"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def read_or_create_source_metadata(record: dict[str, Any], paths: dict[str, Path]) -> dict[str, Any]:
    metadata_path = paths["metadata"] / "source-metadata.json"
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))
    return {
        "schema_version": "1.0",
        "metadata_type": "youtube-video-source-metadata",
        "observed_on": today(),
        "channel": {
            "name": record.get("channel", "Shanghao Jin"),
            "handle": "@shanghaojin",
            "id": record.get("channel_id"),
            "url": "https://www.youtube.com/@shanghaojin",
        },
        "video": {
            "id": record["video_id"],
            "title": record["title"],
            "source_url": record["source_url"],
            "upload_date": record["upload_date"],
            "timestamp": record.get("timestamp"),
            "timestamp_utc": record.get("timestamp_utc"),
            "duration_seconds": record.get("duration_seconds"),
            "availability": record.get("availability", "public"),
            "live_status": record.get("public_status", "not_live"),
            "channel": record.get("channel", "Shanghao Jin"),
            "channel_id": record.get("channel_id"),
            "playlist_index": record.get("playlist_index"),
        },
        "resolution": {
            "highest_available": record.get("highest_available"),
            "accepted_max_height": 2160,
            "selection_expression": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
        },
        "captions": {
            "automatic_languages": record.get("automatic_caption_languages", []),
            "manual_languages": record.get("manual_caption_languages", []),
        },
    }


def write_source_metadata(metadata: dict[str, Any], paths: dict[str, Path]) -> None:
    write_json_atomic(paths["metadata"] / "source-metadata.json", metadata)


def find_model_path() -> Path:
    matches = sorted(Path.home().glob(str(MODEL_GLOB).split(str(Path.home()) + "/", 1)[-1]))
    for candidate in matches:
        if (candidate / "model.bin").exists():
            return candidate
    raise PipelineError("本地 faster-whisper-small 模型不存在，未自动下载新模型", code="blocked_tooling")


def probe_video(video_path: Path, log_path: Path) -> dict[str, Any]:
    output = log_path.with_suffix(".json")
    command = [
        str(FFPROBE),
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate",
        "-of",
        "json",
        str(video_path),
    ]
    run_logged(command, log_path, label="ffprobe", threshold=PROCESS_CPU_GATE)
    # run_logged 的日志含有 command/resource 行，直接再执行一次轻量 ffprobe 读取 JSON。
    result = subprocess.run(command, capture_output=True, text=True, check=False, env=command_env())
    if result.returncode != 0:
        raise PipelineError("ffprobe 无法读取下载源文件", code="tooling_failure", retryable=True)
    output.write_text(result.stdout, encoding="utf-8")
    value = json.loads(result.stdout)
    duration = float(value.get("format", {}).get("duration") or 0)
    video_stream = next((s for s in value.get("streams", []) if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in value.get("streams", []) if s.get("codec_type") == "audio"), {})
    if duration <= 0 or not video_stream or not audio_stream:
        raise PipelineError("下载源文件缺少有效音视频流", code="tooling_failure", retryable=True)
    return {
        "duration_seconds": duration,
        "width": int(video_stream.get("width") or 0),
        "height": int(video_stream.get("height") or 0),
        "fps": parse_rate(video_stream.get("r_frame_rate")),
        "video_codec": video_stream.get("codec_name"),
        "audio_codec": audio_stream.get("codec_name"),
        "audio_channels": audio_stream.get("channels"),
        "audio_sample_rate": audio_stream.get("sample_rate"),
        "ffprobe_json": "diagnostics/ffprobe.json",
    }


def parse_rate(value: Any) -> float | None:
    if not value or value == "0/0":
        return None
    try:
        numerator, denominator = str(value).split("/", 1)
        return round(float(numerator) / float(denominator), 3)
    except (ValueError, ZeroDivisionError):
        return None


def clean_transcript_text(text: str) -> str:
    text = text.replace("\u200b", "").replace("\ufeff", "")
    text = re.sub(r"[ \t\r\n]+", " ", text).strip()
    return text


def transcript_rows_from_raw(raw_path: Path, duration: float, chapters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    boundaries = [float(chapter["start"]) for chapter in chapters]
    rows: list[dict[str, Any]] = []
    previous_start = 0.0
    for index, segment in enumerate(raw.get("segments", []), start=1):
        start = max(0.0, min(float(segment.get("start", 0.0)), duration))
        end = max(start, min(float(segment.get("end", start)), duration))
        text = clean_transcript_text(str(segment.get("text", "")))
        if not text:
            continue
        if start < previous_start:
            start = previous_start
        chapter_index = max(0, bisect.bisect_right(boundaries, start) - 1)
        chapter_id = chapters[chapter_index]["id"]
        rows.append(
            {
                "id": f"seg-{len(rows) + 1:06d}",
                "start": round(start, 3),
                "end": round(end, 3),
                "text": text,
                "chapter": chapter_id,
                "source": "faster-whisper-small",
            }
        )
        previous_start = start
    return rows


def keyword_label(text: str, fallback: str) -> str:
    groups = [
        ("AI与科技产业", ["AI", "人工智能", "模型", "芯片", "半导体", "云", "英伟达", "OpenAI", "Anthropic"]),
        ("仓位、杠杆与资金流", ["仓位", "杠杆", "CTA", "基金", "资金", "流入", "流出", "对冲", "position"]),
        ("宏观、利率与流动性", ["利率", "收益率", "通胀", "Fed", "美联储", "流动性", "美元", "日元", "债券", "宏观"]),
        ("估值、盈利与市场定价", ["估值", "盈利", "收入", "现金流", "利润", "EPS", "PE", "价格", "市场"]),
        ("风险情景与交易框架", ["风险", "情景", "波动", "下跌", "上涨", "交易", "回撤", "冲击"]),
    ]
    scores = [(sum(text.lower().count(term.lower()) for term in terms), label) for label, terms in groups]
    score, label = max(scores, key=lambda item: item[0])
    return label if score else fallback


def build_chapters(rows: list[dict[str, Any]], duration: float) -> list[dict[str, Any]]:
    count = 6 if duration >= 900 else 5
    sections: list[dict[str, Any]] = []
    for index in range(count):
        start = round(duration * index / count, 3)
        end = round(duration * (index + 1) / count, 3)
        if index == count - 1:
            end = round(duration, 3)
        section_text = " ".join(
            row["text"] for row in rows if float(row["start"]) >= start and float(row["start"]) < end
        )
        fallback = ["开场与市场总览", "仓位与资金流", "宏观与利率", "AI与科技产业", "风险情景", "收尾与观察"][
            min(index, 5)
        ]
        sections.append(
            {
                "id": f"chapter-{index + 1:02d}",
                "start": start,
                "end": end,
                "label": keyword_label(section_text, fallback),
            }
        )
    return sections


def image_hash(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        gray = image.convert("L").resize((32, 18))
        pixels = list(gray.getdata())
    average = sum(pixels) / len(pixels)
    bits = 0
    for pixel in pixels:
        bits = (bits << 1) | int(pixel >= average)
    return bits, len(pixels)


def hash_distance(left: tuple[int, int], right: tuple[int, int]) -> int:
    return (left[0] ^ right[0]).bit_count()


def normalize_ocr(text: str) -> str:
    lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            lines.append(line)
    return ("\n".join(lines) + "\n") if lines else ""


def text_similarity(left: str, right: str) -> float:
    def tokens(value: str) -> set[str]:
        return set(re.findall(r"[A-Za-z0-9\u3400-\u9fff]+", value.lower()))

    a, b = tokens(left), tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def ocr_score(text: str) -> tuple[int, int, int]:
    chars = re.findall(r"[A-Za-z0-9\u3400-\u9fff]", text)
    digits = re.findall(r"[0-9]", text)
    lines = [line for line in text.splitlines() if line.strip()]
    return len(chars), len(digits), len(lines)


def acceptable_ocr(text: str) -> bool:
    chars, digits, lines = ocr_score(text)
    if chars >= 18:
        return True
    return chars >= 10 and (digits >= 2 or lines >= 2)


def visual_types(text: str) -> list[str]:
    lowered = text.lower()
    result = ["slide"]
    if any(term in lowered for term in ["%", "chart", "图", "同比", "y/y", "qoq", "曲线"]):
        result.append("chart")
    if any(term in lowered for term in ["rate", "yield", "利率", "收益率", "债券"]):
        result.append("rates")
    if any(term in lowered for term in ["ai", "芯片", "半导体", "openai", "anthropic", "模型"]):
        result.append("ai")
    if any(term in lowered for term in ["flow", "flows", "资金", "仓位", "杠杆", "cta"]):
        result.append("positioning")
    return result


def slide_title(ocr: str, index: int) -> str:
    preferred_markers = [
        "executive summary",
        "positioning",
        "momentum",
        "the fed",
        "earnings",
        "capex",
        "volatility",
        "conclusion",
        "rates",
        "yen",
        "market",
        "leverage",
        "funding",
        "geopolitic",
        "AI",
        "人工智能",
        "市场",
        "总结",
    ]
    marker_lines = [
        line.strip(" |:-")
        for line in ocr.splitlines()
        if any(marker.lower() in line.lower() for marker in preferred_markers)
        and len(re.findall(r"[A-Za-z0-9\u3400-\u9fff]", line)) >= 4
    ]
    if marker_lines:
        return max(marker_lines, key=lambda line: len(re.findall(r"[A-Za-z0-9\u3400-\u9fff]", line)))[:120]
    candidates: list[tuple[int, str]] = []
    for line in ocr.splitlines():
        line = line.strip(" |:-")
        meaningful = re.findall(r"[A-Za-z0-9\u3400-\u9fff]", line)
        if len(meaningful) < 4:
            continue
        words = re.findall(r"[A-Za-z]{3,}|[\u3400-\u9fff]{2,}", line)
        noise = len(re.findall(r"[^A-Za-z0-9\u3400-\u9fff %&:/'().+?-]", line))
        score = len(meaningful) + len(words) * 8 - noise * 4
        if len(line) > 120:
            score -= len(line) - 120
        candidates.append((score, line))
    if candidates:
        return max(candidates, key=lambda item: item[0])[1][:120]
    return f"第{index}页信息画面"


def slide_summary(title: str, ocr: str) -> str:
    types = visual_types(ocr)
    category = {
        "rates": "利率与宏观",
        "ai": "AI 与科技产业",
        "positioning": "仓位与资金流",
        "chart": "图表与数据",
    }
    labels = [category[item] for item in types if item in category]
    focus = "、".join(dict.fromkeys(labels)) if labels else "文字和图表"
    return f"画面以{focus}信息为主，标题识别为“{title}”；OCR 属自动识别结果，具体数字和专有名词需结合原始画面复核。"


def parse_scene_times(log_text: str) -> list[float]:
    return [float(value) for value in re.findall(r"pts_time:([0-9]+(?:\.[0-9]+)?)", log_text)]


def run_scene_candidates(video_path: Path, temp_dir: Path, paths: dict[str, Path]) -> list[tuple[Path, float]]:
    candidate_dir = temp_dir / "candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    scene_log = paths["diagnostics"] / "scene-detection.log"
    scene_prefix = candidate_dir / "scene-%06d.png"
    scene_command = [
        str(FFMPEG),
        "-hide_banner",
        "-loglevel",
        "info",
        "-i",
        str(video_path),
        "-vf",
        "select='gt(scene,0.12)',showinfo",
        "-fps_mode",
        "vfr",
        "-q:v",
        "2",
        "-an",
        str(scene_prefix),
    ]
    run_logged(scene_command, scene_log, label="scene-detection", threshold=PROCESS_CPU_GATE)
    log_text = scene_log.read_text(encoding="utf-8", errors="replace")
    scene_times = parse_scene_times(log_text)
    scene_files = sorted(candidate_dir.glob("scene-*.png"))
    candidates: list[tuple[Path, float]] = []
    for index, path in enumerate(scene_files):
        if index < len(scene_times):
            candidates.append((path, scene_times[index]))

    sample_log = paths["diagnostics"] / "sample-frames.log"
    sample_prefix = candidate_dir / "sample-%06d.png"
    sample_command = [
        str(FFMPEG),
        "-hide_banner",
        "-loglevel",
        "info",
        "-i",
        str(video_path),
        "-vf",
        "fps=1/20",
        "-q:v",
        "2",
        "-an",
        str(sample_prefix),
    ]
    run_logged(sample_command, sample_log, label="sample-frames", threshold=PROCESS_CPU_GATE)
    sample_files = sorted(candidate_dir.glob("sample-*.png"))
    for index, path in enumerate(sample_files):
        candidates.append((path, float(index) * 20.0))
    return sorted(candidates, key=lambda item: item[1])


def collect_deck(video_path: Path, duration: float, temp_dir: Path, paths: dict[str, Path]) -> list[dict[str, Any]]:
    candidates = run_scene_candidates(video_path, temp_dir, paths)
    unique_exact: set[str] = set()
    accepted: list[dict[str, Any]] = []
    ocr_dir = temp_dir / "ocr-candidates"
    ocr_dir.mkdir(parents=True, exist_ok=True)

    for index, (candidate, timestamp) in enumerate(candidates, start=1):
        if timestamp > duration + 1:
            continue
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest in unique_exact:
            continue
        unique_exact.add(digest)
        try:
            current_hash = image_hash(candidate)
        except Exception:
            continue
        duplicate = next(
            (item for item in accepted if hash_distance(current_hash, item["hash"]) <= 8),
            None,
        )
        if duplicate is not None:
            duplicate["times"].append(round(max(0.0, timestamp), 2))
            continue

        # macOS 上 Tesseract 对 /tmp 符号链接路径存在读取异常，统一传入
        # 解析后的 /private/tmp 物理路径；输出路径也使用同一物理路径。
        ocr_image = (ocr_dir / f"image-{index:06d}.png").resolve()
        with Image.open(candidate) as source_image:
            # 只对 OCR 临时副本放大；正式 slide 仍复制原始分辨率帧。
            enhanced = source_image.convert("RGB").resize(
                (source_image.width * 2, source_image.height * 2), Image.Resampling.LANCZOS
            )
            enhanced = ImageEnhance.Contrast(enhanced).enhance(1.15)
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.3)
            enhanced.save(ocr_image)
        ocr_base = (ocr_dir / f"ocr-{index:06d}").resolve()
        ocr_output = ocr_base.with_suffix(".txt")
        ocr_log = ocr_base.with_suffix(".log")
        ocr_command = [
            str(TESSERACT),
            str(ocr_image),
            str(ocr_base),
            "-l",
            "eng+chi_sim+chi_tra",
            "--psm",
            "6",
        ]
        try:
            run_logged(ocr_command, ocr_log, label="tesseract", threshold=PROCESS_CPU_GATE)
        except PipelineError:
            continue
        if not ocr_output.exists():
            continue
        ocr_text = normalize_ocr(ocr_output.read_text(encoding="utf-8", errors="replace"))
        if not acceptable_ocr(ocr_text):
            continue

        duplicate = next(
            (
                item
                for item in accepted
                if hash_distance(current_hash, item["hash"]) <= 10
                or text_similarity(ocr_text, item["ocr"]) >= 0.72
            ),
            None,
        )
        if duplicate is not None:
            duplicate["times"].append(round(max(0.0, timestamp), 2))
            if ocr_score(ocr_text) > ocr_score(duplicate["ocr"]):
                duplicate["candidate"] = candidate
                duplicate["ocr"] = ocr_text
                duplicate["hash"] = current_hash
            continue
        accepted.append(
            {
                "candidate": candidate,
                "timestamp": round(max(0.0, timestamp), 2),
                "times": [round(max(0.0, timestamp), 2)],
                "ocr": ocr_text,
                "hash": current_hash,
            }
        )

    accepted.sort(key=lambda item: min(item["times"]))
    deck_items: list[dict[str, Any]] = []
    for index, item in enumerate(accepted, start=1):
        title = slide_title(item["ocr"], index)
        deck_items.append(
            {
                "id": f"slide-{index:03d}",
                "time_ranges": [[time, time] for time in sorted(set(item["times"]))],
                "title": title,
                "ocr": item["ocr"],
                "visual_type": visual_types(item["ocr"]),
                "summary": slide_summary(title, item["ocr"]),
                "candidate": item["candidate"],
            }
        )
    return deck_items


def write_standard_package(
    record: dict[str, Any],
    source_info: dict[str, Any],
    paths: dict[str, Path],
    duration: float,
    rows: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
    deck_items: list[dict[str, Any]],
    acquisition: dict[str, Any],
) -> Path:
    package_id = record["package_id"]
    target = ARCHIVE / package_id
    if target.exists():
        raise PipelineError(f"正式目录已存在，拒绝覆盖: {target}", code="package_conflict")
    work = STAGING / f"work-{package_id}"
    if work.exists():
        safe_remove_staging_tree(work)
    work.mkdir(parents=True, exist_ok=False)
    (work / "slides").mkdir()
    (work / "ocr").mkdir()

    transcript_path = work / "transcript.jsonl"
    write_text_atomic(transcript_path, "".join(compact_json(row) + "\n" for row in rows))

    deck_rows: list[dict[str, Any]] = []
    expected_source_frames = {f"slide-{index:03d}.png" for index in range(1, len(deck_items) + 1)}
    for stale_frame in paths["selected"].glob("slide-*.png"):
        if stale_frame.name not in expected_source_frames:
            stale_frame.unlink()
    for index, item in enumerate(deck_items, start=1):
        filename = f"slide-{index:03d}.png"
        source_frame = paths["selected"] / filename
        shutil.copy2(item["candidate"], source_frame)
        package_frame = work / "slides" / filename
        shutil.copy2(source_frame, package_frame)
        ocr_filename = f"slide-{index:03d}.txt"
        ocr_path = work / "ocr" / ocr_filename
        write_text_atomic(ocr_path, item["ocr"])
        deck_rows.append(
            {
                "id": item["id"],
                "time_ranges": item["time_ranges"],
                "title": item["title"],
                "image": f"slides/{filename}",
                "ocr_file": f"ocr/{ocr_filename}",
                "ocr": item["ocr"],
                "visual_type": item["visual_type"],
                "summary": item["summary"],
                "source_file": f"../../_source/{package_id}/frames/selected/{filename}",
                "image_format": "png",
            }
        )
    write_text_atomic(work / "deck.jsonl", "".join(compact_json(row) + "\n" for row in deck_rows))

    manifest = {
        "schema_version": "1.0",
        "package_type": "video-research-agent-data",
        "video": {
            "id": package_id,
            "title": record["title"],
            "date": record["upload_date"],
            "source_url": record["source_url"],
            "duration_seconds": round(duration, 3),
            "language": "zh",
        },
        "files": {
            "transcript": "transcript.jsonl",
            "deck": "deck.jsonl",
            "slides_directory": "slides/",
            "ocr_directory": "ocr/",
        },
        "related_materials": {
            "readable_html": None,
            "source_directory": f"../../_source/{package_id}/",
        },
        "transcript": {
            "record_count": len(rows),
            "kind": "automatic_generated",
            "timing": "native_segment_start_end",
            "source_label": "faster-whisper small on audio extracted from YouTube progressive format 18",
            "original_file": None,
            "fields": TRANSCRIPT_FIELDS,
        },
        "deck": {
            "record_count": len(deck_rows),
            "image_format": "png",
            "image_role": "visual evidence; OCR is the primary retrieval field",
            "fields": DECK_FIELDS,
        },
        "chapters": chapters,
        "acquisition": acquisition,
        "evidence_boundary": "Automatic transcript and OCR may misrecognize proper nouns, figures, and labels. Use source media for verification.",
        "generated_on": today(),
    }
    write_json_atomic(work / "manifest.json", manifest)
    return work


def validate_package(work: Path, package_id: str, duration: float, paths: dict[str, Path]) -> dict[str, Any]:
    expected_top = {"manifest.json", "transcript.jsonl", "deck.jsonl", "slides", "ocr"}
    actual_top = {child.name for child in work.iterdir()}
    if actual_top != expected_top:
        raise PipelineError(f"标准包顶层不符合白名单: {sorted(actual_top)}", code="validation_failure")
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    transcript_rows = [
        json.loads(line)
        for line in (work / "transcript.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    deck_rows = [
        json.loads(line)
        for line in (work / "deck.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if manifest["related_materials"]["readable_html"] is not None:
        raise PipelineError("新包 readable_html 不是 null", code="validation_failure")
    if manifest["transcript"]["record_count"] != len(transcript_rows):
        raise PipelineError("manifest transcript 数量不一致", code="validation_failure")
    if manifest["deck"]["record_count"] != len(deck_rows):
        raise PipelineError("manifest deck 数量不一致", code="validation_failure")
    if manifest["transcript"]["fields"] != TRANSCRIPT_FIELDS or manifest["deck"]["fields"] != DECK_FIELDS:
        raise PipelineError("标准字段集合不一致", code="validation_failure")

    transcript_ids = set()
    last_start = -1.0
    last_end = -1.0
    for row in transcript_rows:
        if set(row) != set(TRANSCRIPT_FIELDS):
            raise PipelineError("transcript 字段不一致", code="validation_failure")
        if row["id"] in transcript_ids:
            raise PipelineError("transcript ID 重复", code="validation_failure")
        transcript_ids.add(row["id"])
        start, end = float(row["start"]), float(row["end"])
        if not (0 <= start <= end <= duration + 1e-3):
            raise PipelineError("transcript 时间越界", code="validation_failure")
        if start < last_start - 1e-3 or end < last_end - 1e-3:
            raise PipelineError("transcript 时间不单调", code="validation_failure")
        last_start, last_end = start, end

    deck_ids = set()
    for row in deck_rows:
        if set(row) != set(DECK_FIELDS):
            raise PipelineError("deck 字段不一致", code="validation_failure")
        if row["id"] in deck_ids:
            raise PipelineError("deck ID 重复", code="validation_failure")
        deck_ids.add(row["id"])
        image = Path(row["image"])
        ocr_file = Path(row["ocr_file"])
        source_file = Path(row["source_file"])
        if image.is_absolute() or ocr_file.is_absolute() or source_file.is_absolute():
            raise PipelineError("标准包出现绝对路径", code="validation_failure")
        if not str(image).startswith("slides/") or not str(ocr_file).startswith("ocr/"):
            raise PipelineError("deck image/ocr_file 越界", code="validation_failure")
        image_path = work / image
        ocr_path = work / ocr_file
        expected_source_prefix = f"../../_source/{package_id}/"
        if not str(source_file).startswith(expected_source_prefix):
            raise PipelineError("deck source_file 未指向对应 source 包", code="validation_failure")
        # staging 位于 Herman Jin/_source/_pipeline/staging，而正式包位于
        # Herman Jin/market-overview/；因此 source_file 的相对路径只能在正式包发布后解析。
        # 验收阶段用已登记的 source selected frame 做等价检查。
        source_path = paths["selected"] / source_file.name
        if not image_path.exists() or not ocr_path.exists() or not source_path.exists():
            raise PipelineError("deck 引用文件不存在", code="validation_failure")
        if ocr_path.read_bytes().decode("utf-8") != row["ocr"]:
            raise PipelineError("OCR 文件与 deck.jsonl 不一致", code="validation_failure")
        with Image.open(image_path) as image_obj:
            if image_obj.format != "PNG":
                raise PipelineError("slide 不是 PNG", code="validation_failure")
            image_size = image_obj.size
        with Image.open(source_path) as source_obj:
            if source_obj.format not in {"PNG", "JPEG", "WEBP"}:
                raise PipelineError("source frame 不是图像", code="validation_failure")
            if source_obj.size != image_size:
                raise PipelineError("slide 被改变分辨率", code="validation_failure")
        for time_range in row["time_ranges"]:
            if not (0 <= float(time_range[0]) <= float(time_range[1]) <= duration + 1):
                raise PipelineError("deck 时间越界", code="validation_failure")

    for path in work.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".html", ".mp3", ".m4a", ".wav", ".srt", ".vtt"}:
            raise PipelineError(f"标准包包含禁止文件: {path}", code="validation_failure")
    chapters = manifest.get("chapters", [])
    if chapters and abs(float(chapters[-1]["end"]) - duration) > 0.01:
        raise PipelineError("最后章节没有结束于视频时长", code="validation_failure")
    expected_frames = {Path(row["image"]).name for row in deck_rows}
    if paths["selected"].exists():
        for frame in paths["selected"].glob("*.png"):
            if frame.name not in expected_frames:
                raise PipelineError("source selected frame 存在未被当前 Deck 采用的旧帧", code="validation_failure")
            with Image.open(frame) as frame_obj:
                with Image.open(work / "slides" / frame.name) as package_obj:
                    if frame_obj.size != package_obj.size:
                        raise PipelineError("source selected frame 与正式 slide 尺寸不一致", code="validation_failure")
    return {"transcript_count": len(transcript_rows), "deck_count": len(deck_rows)}


def update_index(record: dict[str, Any]) -> None:
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    packages = list(index.get("packages", []))
    if any(package.get("id") == record["package_id"] for package in packages):
        raise PipelineError("agent-index 已存在目标 package ID", code="index_conflict")
    packages.append(
        {
            "id": record["package_id"],
            "title": record["title"],
            "date": record["upload_date"],
            "manifest": f"market-overview/{record['package_id']}/manifest.json",
            "readable": None,
            "source": f"_source/{record['package_id']}/",
        }
    )
    packages.sort(key=lambda item: (item.get("date", ""), item.get("id", "")), reverse=True)
    index["packages"] = packages
    index["generated_on"] = today()
    write_json_atomic(INDEX_PATH, index)


def update_metadata_after_success(
    metadata: dict[str, Any],
    paths: dict[str, Path],
    source_info: dict[str, Any],
    acquisition: dict[str, Any],
) -> None:
    metadata["observed_on"] = today()
    metadata["actual_media"] = source_info
    metadata["acquisition"] = acquisition
    metadata["artifacts"] = {
        "audio_directory": "audio/",
        "transcript_directory": "transcript/",
        "selected_frames_directory": "frames/selected/",
        "temporary_source_deleted": True,
    }
    write_source_metadata(metadata, paths)
    write_json_atomic(
        paths["diagnostics"] / f"recovery-{today()}.json",
        {
            "observed_on": today(),
            "video_id": metadata.get("video", {}).get("id"),
            "download_method": acquisition["method"],
            "fallback_reason": acquisition["fallback_reason"],
            "temporary_source_deleted": True,
            "signed_urls_retained": False,
        },
    )


def remove_downloaded_source(temp_dir: Path) -> None:
    safe_remove_tree(temp_dir)
    print(f"[cleanup] 已删除本期临时源文件目录: {temp_dir}", flush=True)


def choose_next(records: list[dict[str, Any]], state: dict[str, Any]) -> dict[str, Any] | None:
    for record in sorted(records, key=lambda item: (item["upload_date"], item["video_id"]), reverse=True):
        status = state["entries"].get(record["video_id"], {}).get("status")
        if status not in {"complete_existing", "complete"}:
            return record
    return None


def process_video(record: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    video_id = record["video_id"]
    package_id = record["package_id"]
    paths = ensure_source_dirs(package_id)
    metadata = read_or_create_source_metadata(record, paths)
    temp_dir = Path(tempfile.mkdtemp(prefix=f"herman-jin-{video_id}-", dir="/tmp"))
    source_video: Path | None = None
    published = False
    try:
        transition(state, video_id, "downloading", attempts=state["entries"][video_id].get("attempts", 0) + 1)
        wait_for_gate("download", DOWNLOAD_CPU_GATE)
        source_prefix = temp_dir / "source.%(ext)s"
        download_log = paths["diagnostics"] / f"download-fallback-{today()}.log"
        download_command = [
            str(YTDLP),
            "--format",
            "18/17",
            "--output",
            str(source_prefix),
            "--no-playlist",
            "--no-mtime",
            "--no-part",
            "--retries",
            "3",
            "--fragment-retries",
            "3",
            "--socket-timeout",
            "30",
            record["source_url"],
        ]
        run_logged(download_command, download_log, label="yt-dlp progressive download", threshold=DOWNLOAD_CPU_GATE)
        candidates = [path for path in temp_dir.glob("source.*") if path.is_file() and not path.name.endswith(".json")]
        if not candidates:
            raise PipelineError("yt-dlp 未产生视频文件", code="blocked_tooling", retryable=True)
        source_video = max(candidates, key=lambda path: path.stat().st_size)
        if source_video.stat().st_size < 1024 * 1024:
            raise PipelineError("下载视频文件异常过小", code="blocked_tooling", retryable=True)
        actual_format_id = "18" if source_video.suffix.lower() == ".mp4" else "17"
        print(f"[download] {package_id}: {source_video.stat().st_size / 1024 / 1024:.1f} MiB", flush=True)

        transition(state, video_id, "transcribing")
        wait_for_gate("audio", PROCESS_CPU_GATE)
        source_info = probe_video(source_video, paths["diagnostics"] / "ffprobe.log")
        audio_output = paths["audio"] / "source.m4a"
        # 临时文件仍保留 m4a 后缀，否则 ffmpeg 无法自动选择输出 muxer。
        audio_temp = paths["audio"] / "source.part.m4a"
        raw_transcript = paths["transcript"] / "transcript_raw_zh.json"
        standard_transcript = paths["transcript"] / "transcript.jsonl"
        if not (audio_output.exists() and audio_output.stat().st_size > 1024 * 1024):
            if audio_temp.exists():
                audio_temp.unlink()
            audio_command = [
                str(FFMPEG),
                "-hide_banner",
                "-y",
                "-threads",
                "1",
                "-filter_threads",
                "1",
                "-filter_complex_threads",
                "1",
                "-i",
                str(source_video),
                "-map",
                "0:a:0",
                "-vn",
                "-c:a",
                "copy",
                str(audio_temp),
            ]
            run_logged(audio_command, paths["diagnostics"] / "audio-extract.log", label="audio-extract", threshold=PROCESS_CPU_GATE)
            os.replace(audio_temp, audio_output)
        else:
            print(f"[resume] {package_id}: reuse existing source audio", flush=True)

        if not (raw_transcript.exists() and standard_transcript.exists()):
            model_path = find_model_path()
            transition(state, video_id, "transcribing", model="faster-whisper-small", audio_format="m4a")
            wait_for_gate("transcribe", PROCESS_CPU_GATE)
            transcribe_command = [
                str(PYTHON),
                str(TRANSCRIBE_WORKER),
                "--audio",
                str(audio_output),
                "--out-dir",
                str(paths["transcript"]),
                "--duration",
                str(source_info["duration_seconds"]),
                "--model-path",
                str(model_path),
            ]
            run_logged(transcribe_command, paths["diagnostics"] / "transcribe.log", label="faster-whisper", threshold=PROCESS_CPU_GATE)
        else:
            print(f"[resume] {package_id}: reuse existing Whisper transcript", flush=True)
        if not raw_transcript.exists():
            raise PipelineError("Whisper 没有产生原始 JSON", code="transcription_failure", retryable=True)
        initial_raw = json.loads(raw_transcript.read_text(encoding="utf-8"))
        initial_rows = [
            {
                "start": float(item.get("start", 0)),
                "end": float(item.get("end", 0)),
                "text": clean_transcript_text(item.get("text", "")),
            }
            for item in initial_raw.get("segments", [])
            if clean_transcript_text(item.get("text", ""))
        ]
        chapters = build_chapters(initial_rows, source_info["duration_seconds"])
        rows = transcript_rows_from_raw(raw_transcript, source_info["duration_seconds"], chapters)
        write_text_atomic(
            paths["transcript"] / "transcript.jsonl",
            "".join(compact_json(row) + "\n" for row in rows),
        )
        if not rows:
            raise PipelineError("Whisper 原始结果没有有效片段", code="transcription_failure", retryable=True)
        print(f"[transcript] {package_id}: {len(rows)} segments", flush=True)

        transition(state, video_id, "slides")
        wait_for_gate("slides", PROCESS_CPU_GATE)
        deck_items = collect_deck(source_video, source_info["duration_seconds"], temp_dir, paths)
        print(f"[deck] {package_id}: {len(deck_items)} unique visual frames", flush=True)

        transition(state, video_id, "validating")
        wait_for_gate("validation", PROCESS_CPU_GATE)
        acquisition = {
            "method": "yt-dlp public progressive format fallback",
            "requested_format": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",
            "actual_format_id": actual_format_id,
            "actual_container": source_video.suffix.lower().lstrip("."),
            "actual_width": source_info["width"],
            "actual_height": source_info["height"],
            "actual_fps": source_info["fps"],
            "fallback_reason": "DASH media streams returned HTTP 403 after a nonzero byte offset; public progressive format 18 was readable.",
            "temporary_source_retained_only_during_processing": True,
        }
        work = write_standard_package(
            record,
            source_info,
            paths,
            source_info["duration_seconds"],
            rows,
            chapters,
            deck_items,
            acquisition,
        )
        validation = validate_package(work, package_id, source_info["duration_seconds"], paths)
        target = ARCHIVE / package_id
        os.replace(work, target)
        published = True
        update_metadata_after_success(metadata, paths, source_info, acquisition)
        transition(
            state,
            video_id,
            "complete",
            failure_code=None,
            failure_detail=None,
            download_format=actual_format_id,
            actual_resolution=f"{source_info['width']}x{source_info['height']}",
            transcript_count=validation["transcript_count"],
            deck_count=validation["deck_count"],
            completed_on=today(),
        )
        update_inventory(
            video_id,
            "complete",
            download_format=actual_format_id,
            actual_resolution=f"{source_info['width']}x{source_info['height']}",
            transcript_count=validation["transcript_count"],
            deck_count=validation["deck_count"],
        )
        # 按计划：索引是本期正式归档的最后一步。
        update_index(record)
        print(f"[complete] {package_id}: package published and indexed", flush=True)
        return {"package_id": package_id, **validation}
    except ResourceInterruption:
        transition(state, video_id, "discovered", failure_code="resource_gate", failure_detail="resource gate interrupted current stage")
        raise
    except PipelineError as error:
        status = "unavailable" if error.code == "unavailable" else ("blocked" if error.code == "blocked_tooling" else "failed")
        transition(state, video_id, status, failure_code=error.code, failure_detail=str(error))
        update_inventory(video_id, status, failure_code=error.code)
        raise
    finally:
        if source_video is not None and source_video.exists():
            source_video.unlink()
        if temp_dir.exists():
            remove_downloaded_source(temp_dir)
        if not published:
            work = STAGING / f"work-{package_id}"
            if work.exists():
                safe_remove_staging_tree(work)


def acquire_lock() -> Any:
    lock_path = PIPELINE / "archive_worker.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = lock_path.open("a+")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        handle.close()
        raise PipelineError("已有 Herman Jin 管线正在运行", code="pipeline_lock") from exc
    handle.seek(0)
    handle.truncate()
    handle.write(f"pid={os.getpid()} started={now_iso()}\n")
    handle.flush()
    return handle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--one", help="只处理指定 YouTube video ID")
    parser.add_argument("--limit", type=int, default=0, help="最多处理多少期，0 表示直到队列为空")
    args = parser.parse_args()
    lock_handle = acquire_lock()
    try:
        records = load_inventory()
        state = load_state()
        processed = 0
        while args.limit <= 0 or processed < args.limit:
            records = load_inventory()
            state = load_state()
            record = None
            if args.one:
                record = next((item for item in records if item["video_id"] == args.one), None)
                if record is None:
                    raise PipelineError(f"找不到 video ID: {args.one}", code="inventory_error")
                current_status = state["entries"][args.one].get("status")
                if current_status in {"complete_existing", "complete"}:
                    print(f"[skip] {record['package_id']} 已完成", flush=True)
                    break
            else:
                record = choose_next(records, state)
            if record is None:
                print("[queue] 没有待处理视频", flush=True)
                break
            print(
                f"[start] {record['package_id']} video_id={record['video_id']} "
                f"date={record['upload_date']}",
                flush=True,
            )
            try:
                process_video(record, state)
            except ResourceInterruption as error:
                print(f"[requeue] {error}", file=sys.stderr, flush=True)
                return 75
            except PipelineError as error:
                print(f"[failed] {record['package_id']}: {error}", file=sys.stderr, flush=True)
                if args.one:
                    return 1
            processed += 1
            if args.one:
                break
        return 0
    finally:
        lock_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
