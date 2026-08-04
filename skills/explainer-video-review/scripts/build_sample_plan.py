#!/usr/bin/env python3
"""Build a deterministic evidence sampling plan for a rendered video."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PRESETS = {
    "quick": {"interval_s": 2.0, "boundary_offsets": [0.0]},
    "standard": {"interval_s": 1.0, "boundary_offsets": [-0.25, 0.0, 0.25]},
    "dense": {"interval_s": 0.5, "boundary_offsets": [-0.25, 0.0, 0.25]},
}


def clamp(value: float, duration: float) -> float:
    return max(0.0, min(value, max(0.0, duration - 0.01)))


def load_boundaries(path: Path | None) -> list[float]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        raw = payload.get("boundaries_s", payload.get("boundaries", []))
        if isinstance(raw, list):
            return [float(item) for item in raw if isinstance(item, (int, float))]
        segments = payload.get("segments", [])
        if isinstance(segments, list):
            values: list[float] = []
            for segment in segments:
                if not isinstance(segment, dict):
                    continue
                for key in ("start_s", "end_s", "start", "end"):
                    if isinstance(segment.get(key), (int, float)):
                        values.append(float(segment[key]))
            return values
    if isinstance(payload, list):
        return [float(item) for item in payload if isinstance(item, (int, float))]
    return []


def build_plan(duration: float, preset: str, boundaries: list[float]) -> dict[str, Any]:
    if duration <= 0:
        raise ValueError("duration must be greater than 0")
    config = PRESETS[preset]
    timestamps: set[float] = {0.0, clamp(duration, duration)}
    interval = config["interval_s"]
    count = int(duration / interval)
    timestamps.update(clamp(i * interval, duration) for i in range(count + 1))
    for boundary in boundaries:
        for offset in config["boundary_offsets"]:
            timestamps.add(round(clamp(boundary + offset, duration), 2))
    ordered = sorted(round(value, 2) for value in timestamps)
    ordered = list(dict.fromkeys(ordered))
    return {
        "schema_version": "1.0",
        "preset": preset,
        "duration_s": round(duration, 3),
        "interval_s": config["interval_s"],
        "boundary_count": len(boundaries),
        "timestamps_s": ordered,
        "sample_count": len(ordered),
        "rules": [
            "include first and last valid frame",
            "include base interval samples",
            "include boundary offsets and deduplicate after 0.01s quantization",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic video review sampling plan.")
    parser.add_argument("--duration", type=float, required=True, help="Video duration in seconds.")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="standard")
    parser.add_argument("--boundaries", type=Path, help="Optional JSON list/object containing segment boundaries.")
    parser.add_argument("--output", type=Path, help="Write JSON to this path; stdout when omitted.")
    args = parser.parse_args()
    try:
        plan = build_plan(args.duration, args.preset, load_boundaries(args.boundaries))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    rendered = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
