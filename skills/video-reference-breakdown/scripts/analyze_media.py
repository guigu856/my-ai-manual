from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import wave
from array import array
from pathlib import Path
from typing import Any

from _common import SkillError, command, emit, fail, run, sha256_file, write_json


PTS_PATTERN = re.compile(r"pts_time:([0-9.]+)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成视频拆解所需的画面和声音证据。")
    parser.add_argument("media", type=Path, help="本地视频文件")
    parser.add_argument("--output-dir", required=True, type=Path, help="分析输出目录")
    parser.add_argument("--overview-interval", type=float, help="全片概览抽帧间隔，单位秒")
    parser.add_argument("--scene-threshold", type=float, default=0.30)
    return parser


def probe_media(media: Path) -> dict[str, Any]:
    result = run(
        [
            command("ffprobe"),
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(media),
        ],
        "probe_failed",
        "FFprobe 读取媒体信息失败。",
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if video is None:
        raise SkillError("video_stream_missing", "媒体文件中没有视频流。")
    duration = float(payload.get("format", {}).get("duration") or video.get("duration") or 0)
    if duration <= 0:
        raise SkillError("duration_invalid", "媒体时长缺失或无效。")
    return {
        "duration_seconds": duration,
        "format_name": payload.get("format", {}).get("format_name"),
        "size_bytes": int(payload.get("format", {}).get("size") or media.stat().st_size),
        "video": {
            "codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "frame_rate": video.get("avg_frame_rate"),
            "time_base": video.get("time_base"),
            "start_time": video.get("start_time"),
        },
        "audio": None
        if audio is None
        else {
            "codec": audio.get("codec_name"),
            "sample_rate": int(audio.get("sample_rate") or 0),
            "channels": audio.get("channels"),
            "time_base": audio.get("time_base"),
        },
    }


def frame_entries(directory: Path, stderr: str) -> list[dict[str, Any]]:
    files = sorted(directory.glob("frame-*.jpg"))
    timestamps = [float(value) for value in PTS_PATTERN.findall(stderr)]
    entries: list[dict[str, Any]] = []
    for index, path in enumerate(files):
        timestamp = timestamps[index] if index < len(timestamps) else None
        entries.append(
            {
                "frame_id": f"F{index + 1:04d}",
                "timestamp_seconds": timestamp,
                "path": str(path.resolve()),
                "sha256": sha256_file(path),
            }
        )
    return entries


def extract_overview(media: Path, directory: Path, interval: float) -> list[dict[str, Any]]:
    directory.mkdir(parents=True, exist_ok=True)
    result = run(
        [
            command("ffmpeg"),
            "-y",
            "-i",
            str(media),
            "-vf",
            f"fps=1/{interval:.6f},showinfo,scale='min(960,iw)':-2",
            "-q:v",
            "2",
            str(directory / "frame-%04d.jpg"),
        ],
        "overview_frames_failed",
        "全片概览抽帧失败。",
    )
    entries = frame_entries(directory, result.stderr)
    if not entries:
        raise SkillError("overview_frames_empty", "全片概览没有生成任何画面帧。")
    return entries


def extract_scene_candidates(
    media: Path, directory: Path, threshold: float
) -> list[dict[str, Any]]:
    directory.mkdir(parents=True, exist_ok=True)
    filter_value = (
        f"select=gt(scene\\,{threshold:.3f}),showinfo,scale='min(960,iw)':-2"
    )
    result = subprocess.run(
        [
            command("ffmpeg"),
            "-y",
            "-i",
            str(media),
            "-vf",
            filter_value,
            "-fps_mode",
            "vfr",
            "-frames:v",
            "80",
            "-q:v",
            "2",
            str(directory / "frame-%04d.jpg"),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 and not (
        "No filtered frames" in result.stderr or "Nothing was written" in result.stderr
    ):
        raise SkillError(
            "scene_candidates_failed",
            "场景变化候选抽帧失败。",
            {"returncode": result.returncode, "stderr": result.stderr[-4000:]},
        )
    return frame_entries(directory, result.stderr)


def concat_line(path: Path) -> str:
    escaped = path.resolve().as_posix().replace("'", "'\\''")
    return f"file '{escaped}'"


def create_contact_sheets(
    frames: list[dict[str, Any]], directory: Path, page_size: int = 32
) -> list[dict[str, Any]]:
    directory.mkdir(parents=True, exist_ok=True)
    sheets: list[dict[str, Any]] = []
    for page_index, start in enumerate(range(0, len(frames), page_size), start=1):
        page = frames[start : start + page_size]
        list_path = directory / f"page-{page_index:03d}.txt"
        list_path.write_text(
            "\n".join(concat_line(Path(item["path"])) for item in page) + "\n",
            encoding="utf-8",
        )
        output_path = directory / f"contact-sheet-{page_index:03d}.jpg"
        run(
            [
                command("ffmpeg"),
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_path),
                "-vf",
                (
                    "scale=320:180:force_original_aspect_ratio=decrease,"
                    "pad=320:180:(ow-iw)/2:(oh-ih)/2:black,"
                    "tile=4x8:padding=4:margin=4"
                ),
                "-frames:v",
                "1",
                str(output_path),
            ],
            "contact_sheet_failed",
            "联系表生成失败。",
        )
        sheets.append(
            {
                "page": page_index,
                "frame_count": len(page),
                "path": str(output_path.resolve()),
                "sha256": sha256_file(output_path),
            }
        )
    return sheets


def dbfs(value: float) -> float:
    return 20 * math.log10(max(value, 1e-12))


def wav_analysis(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as handle:
        sample_rate = handle.getframerate()
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        frames = handle.getnframes()
        raw = handle.readframes(frames)
    if sample_width != 2:
        raise SkillError("audio_format_unsupported", "分析音轨不是 16 位 PCM。")
    samples = array("h")
    samples.frombytes(raw)
    if sys.byteorder != "little":
        samples.byteswap()
    if channels > 1:
        samples = array("h", samples[::channels])
    normalized = [sample / 32768.0 for sample in samples]
    peak = max((abs(sample) for sample in normalized), default=0.0)
    rms = math.sqrt(sum(sample * sample for sample in normalized) / max(1, len(normalized)))
    window = max(1, int(sample_rate * 0.02))
    envelope: list[float] = []
    for start in range(0, len(normalized), window):
        segment = normalized[start : start + window]
        if segment:
            envelope.append(math.sqrt(sum(value * value for value in segment) / len(segment)))
    onset = [max(0.0, envelope[index] - envelope[index - 1]) for index in range(1, len(envelope))]
    envelope_rate = sample_rate / window
    min_lag = max(1, int(envelope_rate * 60 / 180))
    max_lag = max(min_lag + 1, int(envelope_rate * 60 / 60))
    scores: list[tuple[float, int]] = []
    for lag in range(min_lag, min(max_lag, len(onset) - 1) + 1):
        score = sum(onset[index] * onset[index - lag] for index in range(lag, len(onset)))
        scores.append((score, lag))
    best_score, best_lag = max(scores, default=(0.0, 1))
    total_onset = sum(value * value for value in onset) or 1.0
    confidence = min(1.0, best_score / total_onset)
    tempo = 60 * envelope_rate / best_lag if best_score > 0 else None
    event_threshold = (sum(onset) / max(1, len(onset))) * 3
    events = []
    for index in range(1, len(onset) - 1):
        if onset[index] >= event_threshold and onset[index] >= onset[index - 1] and onset[index] >= onset[index + 1]:
            events.append(
                {
                    "event_id": f"A{len(events) + 1:03d}",
                    "timestamp_seconds": round((index + 1) / envelope_rate, 3),
                    "strength": round(onset[index], 6),
                    "status": "candidate",
                }
            )
        if len(events) >= 100:
            break
    energy_points = []
    group = max(1, int(0.5 * envelope_rate))
    for start in range(0, len(envelope), group):
        segment = envelope[start : start + group]
        if segment:
            energy_points.append(
                {
                    "start_seconds": round(start / envelope_rate, 3),
                    "end_seconds": round((start + len(segment)) / envelope_rate, 3),
                    "rms_dbfs": round(dbfs(sum(segment) / len(segment)), 2),
                }
            )
    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "duration_seconds": frames / sample_rate,
        "rms_dbfs": round(dbfs(rms), 2),
        "peak_dbfs": round(dbfs(peak), 2),
        "tempo_candidate": None
        if tempo is None
        else {"bpm": round(tempo, 2), "confidence": round(confidence, 3), "status": "candidate"},
        "important_sound_changes": events,
        "energy_points": energy_points,
    }


def analyze_audio(media: Path, directory: Path) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    wav_path = directory / "analysis.wav"
    run(
        [
            command("ffmpeg"),
            "-y",
            "-i",
            str(media),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(wav_path),
        ],
        "audio_extract_failed",
        "音轨提取失败。",
    )
    waveform = directory / "waveform.png"
    run(
        [
            command("ffmpeg"),
            "-y",
            "-i",
            str(wav_path),
            "-filter_complex",
            "showwavespic=s=1600x360:colors=0x2E74B5",
            "-frames:v",
            "1",
            str(waveform),
        ],
        "waveform_failed",
        "波形图生成失败。",
    )
    result = wav_analysis(wav_path)
    result.update(
        {
            "present": True,
            "analysis_wav_path": str(wav_path.resolve()),
            "analysis_wav_sha256": sha256_file(wav_path),
            "waveform_path": str(waveform.resolve()),
            "waveform_sha256": sha256_file(waveform),
        }
    )
    return result


def analyze(args: argparse.Namespace) -> Path:
    media = args.media.expanduser().resolve()
    if not media.is_file():
        raise SkillError("media_missing", "指定的视频文件不存在。", {"path": str(media)})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    probe = probe_media(media)
    interval = args.overview_interval
    if interval is None:
        interval = min(10.0, max(0.5, probe["duration_seconds"] / 32))
    if interval <= 0:
        raise SkillError("overview_interval_invalid", "概览抽帧间隔必须大于 0。")
    overview = extract_overview(media, args.output_dir / "frames" / "overview", interval)
    scenes = extract_scene_candidates(
        media, args.output_dir / "frames" / "scene-candidates", args.scene_threshold
    )
    contact_sheets = create_contact_sheets(overview, args.output_dir / "contact-sheets")
    audio = (
        analyze_audio(media, args.output_dir / "audio")
        if probe["audio"] is not None
        else {"present": False, "waveform_path": None, "tempo_candidate": None}
    )
    manifest = {
        "schema_version": "1.0",
        "media": {
            "path": str(media),
            "sha256": sha256_file(media),
        },
        "probe": probe,
        "overview_interval_seconds": interval,
        "overview_frames": overview,
        "scene_change_candidates": scenes,
        "contact_sheets": contact_sheets,
        "audio": audio,
    }
    manifest_path = args.output_dir / "analysis-manifest.json"
    write_json(manifest_path, manifest)
    return manifest_path.resolve()


def main() -> int:
    try:
        args = build_parser().parse_args()
        manifest = analyze(args)
        emit({"ok": True, "analysis_manifest": str(manifest)})
        return 0
    except (SkillError, json.JSONDecodeError) as error:
        if isinstance(error, SkillError):
            return fail(error)
        return fail(SkillError("probe_output_invalid", "FFprobe 返回了无效 JSON。"))


if __name__ == "__main__":
    sys.exit(main())
