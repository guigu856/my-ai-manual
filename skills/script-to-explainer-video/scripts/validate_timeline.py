#!/usr/bin/env python3
"""Validate the script-to-explainer-video timeline contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def as_list(payload: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get(key), list):
        return [item for item in payload[key] if isinstance(item, dict)]
    return []


def integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate(project: Path, timeline_name: str, segments_name: str) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    timeline_path = project / timeline_name
    segments_path = project / segments_name
    if not timeline_path.is_file():
        failures.append(f"missing timeline: {timeline_name}")
        return {"ok": False, "project": str(project), "failures": failures, "warnings": warnings}

    try:
        timeline_payload = load_json(timeline_path)
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"invalid timeline JSON: {exc}")
        return {"ok": False, "project": str(project), "failures": failures, "warnings": warnings}

    if not isinstance(timeline_payload, dict):
        failures.append("timeline.json must be an object")
        return {"ok": False, "project": str(project), "failures": failures, "warnings": warnings}

    for field in ("version", "fps", "duration_frames", "segments"):
        if field not in timeline_payload:
            failures.append(f"timeline.json missing field: {field}")
    fps = timeline_payload.get("fps")
    duration = timeline_payload.get("duration_frames")
    if not integer(fps) and not isinstance(fps, float):
        failures.append("timeline.fps must be numeric")
    elif fps <= 0:
        failures.append("timeline.fps must be positive")
    if not integer(duration) or duration <= 0:
        failures.append("timeline.duration_frames must be a positive integer")

    timeline_segments = as_list(timeline_payload.get("segments"), "segments")
    if not timeline_segments:
        failures.append("timeline.segments must contain at least one object")

    segment_ids: list[str] = []
    previous_end = -1
    max_end = 0
    cue_ids: set[str] = set()
    for index, segment in enumerate(timeline_segments):
        prefix = f"timeline.segments[{index}]"
        segment_id = segment.get("id")
        if not isinstance(segment_id, str) or not segment_id.strip():
            failures.append(f"{prefix}.id must be a non-empty string")
        else:
            if segment_id in segment_ids:
                failures.append(f"duplicate segment id: {segment_id}")
            segment_ids.append(segment_id)
        start = segment.get("start_frame")
        end = segment.get("end_frame")
        if not integer(start) or not integer(end):
            failures.append(f"{prefix} start_frame/end_frame must be integers")
            continue
        if start < 0 or end <= start:
            failures.append(f"{prefix} must satisfy 0 <= start_frame < end_frame")
        if start < previous_end:
            failures.append(f"{prefix} overlaps or is out of order")
        previous_end = end
        max_end = max(max_end, end)
        cues = as_list(segment.get("cues", []), "cues")
        previous_cue_end = start
        for cue_index, cue in enumerate(cues):
            cue_prefix = f"{prefix}.cues[{cue_index}]"
            cue_id = cue.get("id")
            if not isinstance(cue_id, str) or not cue_id.strip():
                failures.append(f"{cue_prefix}.id must be a non-empty string")
            elif cue_id in cue_ids:
                failures.append(f"duplicate cue id: {cue_id}")
            else:
                cue_ids.add(cue_id)
            cue_start = cue.get("start_frame")
            cue_end = cue.get("end_frame")
            if not integer(cue_start) or not integer(cue_end):
                failures.append(f"{cue_prefix} start_frame/end_frame must be integers")
                continue
            if cue_start < start or cue_end > end or cue_end <= cue_start:
                failures.append(f"{cue_prefix} must be inside its parent segment")
            if cue_start < previous_cue_end:
                failures.append(f"{cue_prefix} overlaps or is out of order")
            previous_cue_end = cue_end
            if not isinstance(cue.get("text"), str) or not cue.get("text", "").strip():
                failures.append(f"{cue_prefix}.text must be non-empty")

    if integer(duration) and max_end > duration:
        failures.append("timeline.duration_frames must cover the last segment")
    if integer(duration) and max_end < duration:
        warnings.append("timeline has trailing frames after the last segment; confirm they are an intentional end card or hold")

    if segments_path.is_file():
        try:
            segment_payload = load_json(segments_path)
            source_segments = as_list(segment_payload, "segments")
            source_ids = [item.get("id") for item in source_segments]
            if any(not isinstance(value, str) for value in source_ids):
                failures.append("segments.json contains a segment without a string id")
            elif set(source_ids) != set(segment_ids):
                failures.append("segments.json ids do not match timeline.json segment ids")
            for index, item in enumerate(source_segments):
                if not isinstance(item.get("title"), str) or not item.get("title", "").strip():
                    failures.append(f"segments.json segments[{index}].title must be non-empty")
                if not isinstance(item.get("text"), str) or not item.get("text", "").strip():
                    failures.append(f"segments.json segments[{index}].text must be non-empty")
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"invalid segments JSON: {exc}")
    else:
        warnings.append(f"segments file not found: {segments_name}; timeline-only validation ran")

    return {
        "ok": not failures,
        "project": str(project),
        "timeline": timeline_name,
        "segments": segments_name,
        "failures": failures,
        "warnings": warnings,
        "summary": {
            "segment_count": len(timeline_segments),
            "cue_count": len(cue_ids),
            "duration_frames": duration,
            "max_segment_end": max_end,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate segments.json and timeline.json for the explainer-video Skill.")
    parser.add_argument("--project", default=".", help="Project directory")
    parser.add_argument("--timeline", default="timeline.json", help="Timeline filename")
    parser.add_argument("--segments", default="segments.json", help="Segments filename")
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args()
    result = validate(Path(args.project).resolve(), args.timeline, args.segments)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = Path(args.project).resolve() / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not result["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()