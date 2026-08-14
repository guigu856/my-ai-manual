from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import SkillError, command, emit, fail, run, sha256_file, write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="对指定视频区间进行高密度补充抽帧。")
    parser.add_argument("media", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--interval",
        required=True,
        action="append",
        help="需要补充取证的 START:END 秒区间，可重复传入",
    )
    parser.add_argument("--step", type=float, default=0.1, help="抽帧间隔，最大 0.1 秒")
    return parser


def parse_interval(value: str) -> tuple[float, float]:
    try:
        start_text, end_text = value.split(":", 1)
        start, end = float(start_text), float(end_text)
    except ValueError as error:
        raise SkillError(
            "interval_invalid",
            "区间格式应为 START:END，单位为秒。",
            {"interval": value},
        ) from error
    if start < 0 or end <= start:
        raise SkillError(
            "interval_invalid",
            "区间起点必须大于等于 0，终点必须大于起点。",
            {"interval": value},
        )
    return start, end


def refine(args: argparse.Namespace) -> Path:
    if args.step <= 0:
        raise SkillError("step_invalid", "抽帧间隔必须大于 0。")
    if args.step > 0.1:
        raise SkillError("step_too_large", "加密取证的抽帧间隔不得超过 0.1 秒。")
    media = args.media.expanduser().resolve()
    if not media.is_file():
        raise SkillError("media_missing", "指定的视频文件不存在。", {"path": str(media)})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for interval_index, raw_interval in enumerate(args.interval, start=1):
        start, end = parse_interval(raw_interval)
        timestamp = start
        while timestamp < end - 1e-9:
            milliseconds = round(timestamp * 1000)
            output_path = args.output_dir / f"I{interval_index:02d}-{milliseconds:010d}ms.jpg"
            run(
                [
                    command("ffmpeg"),
                    "-y",
                    "-ss",
                    f"{timestamp:.6f}",
                    "-i",
                    str(media),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale='min(960,iw)':-2",
                    "-q:v",
                    "2",
                    str(output_path),
                ],
                "refine_frame_failed",
                "局部加密抽帧失败。",
            )
            entries.append(
                {
                    "frame_id": f"RF{len(entries) + 1:05d}",
                    "interval": raw_interval,
                    "timestamp_seconds": round(timestamp, 6),
                    "path": str(output_path.resolve()),
                    "sha256": sha256_file(output_path),
                }
            )
            timestamp += args.step
    index_path = args.output_dir / "refined-frames.json"
    write_json(
        index_path,
        {
            "schema_version": "1.0",
            "media_path": str(media),
            "media_sha256": sha256_file(media),
            "step_seconds": args.step,
            "frames": entries,
        },
    )
    return index_path.resolve()


def main() -> int:
    try:
        args = build_parser().parse_args()
        index = refine(args)
        emit({"ok": True, "refined_frames": str(index)})
        return 0
    except SkillError as error:
        return fail(error)


if __name__ == "__main__":
    sys.exit(main())
