#!/usr/bin/env python3
"""使用本地 faster-whisper small 生成可复核的原始转录资产。"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from faster_whisper import WhisperModel


def clean_text(text: str) -> str:
    text = text.replace("\u200b", "").replace("\ufeff", "")
    return re.sub(r"[ \t\r\n]+", " ", text).strip()


def timestamp(seconds: float, comma: bool = True) -> str:
    total_ms = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    separator = "," if comma else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{millis:03d}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--duration", required=True, type=float)
    parser.add_argument("--model-path", required=True)
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = WhisperModel(
        args.model_path,
        device="cpu",
        compute_type="int8",
        cpu_threads=1,
        num_workers=1,
        local_files_only=True,
    )
    segments, info = model.transcribe(
        str(args.audio),
        language="zh",
        task="transcribe",
        beam_size=5,
        temperature=0.0,
        condition_on_previous_text=True,
        vad_filter=False,
    )

    raw_segments = []
    for index, segment in enumerate(segments):
        text = clean_text(segment.text)
        if not text:
            continue
        start = max(0.0, min(float(segment.start), args.duration))
        end = max(start, min(float(segment.end), args.duration))
        raw_segments.append(
            {
                "id": index,
                "start": round(start, 3),
                "end": round(end, 3),
                "text": text,
                "avg_logprob": getattr(segment, "avg_logprob", None),
                "no_speech_prob": getattr(segment, "no_speech_prob", None),
                "compression_ratio": getattr(segment, "compression_ratio", None),
            }
        )

    raw = {
        "language": getattr(info, "language", "zh"),
        "language_probability": getattr(info, "language_probability", None),
        "duration_seconds": args.duration,
        "segments": raw_segments,
        "text": " ".join(item["text"] for item in raw_segments),
    }
    (out_dir / "transcript_raw_zh.json").write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    srt_lines = []
    vtt_lines = ["WEBVTT", ""]
    txt_lines = []
    for index, item in enumerate(raw_segments, start=1):
        srt_lines.extend(
            [
                str(index),
                f"{timestamp(item['start'])} --> {timestamp(item['end'])}",
                item["text"],
                "",
            ]
        )
        vtt_lines.extend(
            [
                f"{timestamp(item['start'], comma=False)} --> {timestamp(item['end'], comma=False)}",
                item["text"],
                "",
            ]
        )
        txt_lines.append(item["text"])
    (out_dir / "transcript_raw_zh.srt").write_text("\n".join(srt_lines), encoding="utf-8")
    (out_dir / "transcript_raw_zh.vtt").write_text("\n".join(vtt_lines), encoding="utf-8")
    (out_dir / "transcript_raw_zh.txt").write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    if not raw_segments:
        raise SystemExit("no valid transcript segments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
