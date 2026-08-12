#!/usr/bin/env python3
"""Validate explainer-video source locks before render and final delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


COMPLEXITY_LIMITS = {
    "focal_points": 1,
    "content_groups": 4,
    "simultaneous_text_blocks": 4,
    "primary_motion_relations": 1,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.name}")
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid UTF-8 JSON: {path.name}: {exc}")
    return {}


def require_object(parent: dict, key: str, where: str, errors: list[str]) -> dict:
    value = parent.get(key)
    if not isinstance(value, dict):
        errors.append(f"{where}.{key} must be an object")
        return {}
    return value


def probe_duration(path: Path) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    try:
        return float(result.stdout.strip())
    except ValueError:
        return None


def validate_plan(project: Path, plan: dict, errors: list[str]) -> None:
    required = {
        "schema_version", "storyboard_hash", "audio_hash", "production_profile",
        "canvas", "fps", "audio_file", "style_lock", "scenes",
    }
    for key in sorted(required - plan.keys()):
        errors.append(f"render-plan.json missing key: {key}")

    profile = plan.get("production_profile")
    if profile not in {"page-isolated", "continuous-diagram"}:
        errors.append("production_profile must be page-isolated or continuous-diagram")

    style = require_object(plan, "style_lock", "render-plan", errors)
    color_mode = style.get("color_mode")
    if color_mode not in {"dark", "light", "mixed-intentional"}:
        errors.append("style_lock.color_mode must be dark, light, or mixed-intentional")
    background = style.get("background_token")
    if not isinstance(background, str) or not background.strip():
        errors.append("style_lock.background_token must be non-empty")

    caption = require_object(style, "caption", "style_lock", errors)
    for key in ("background", "background_alpha", "outline_px", "shadow", "max_lines"):
        if key not in caption:
            errors.append(f"style_lock.caption missing key: {key}")
    background_alpha = caption.get("background_alpha")
    outline_px = caption.get("outline_px")
    if not isinstance(background_alpha, (int, float)) or not 0 <= background_alpha <= 1:
        errors.append("caption background_alpha must be a number from 0 to 1")
    if caption.get("background") == "none" and background_alpha != 0:
        errors.append("caption background=none requires background_alpha=0")
    if not isinstance(outline_px, (int, float)) or outline_px < 0:
        errors.append("caption outline_px must be a non-negative number")
    if not isinstance(caption.get("shadow"), bool):
        errors.append("caption shadow must be boolean")

    chrome_lock = require_object(style, "page_chrome", "style_lock", errors)
    for key in ("corner_label", "page_number", "headline"):
        if chrome_lock.get(key) not in {"required", "hidden"}:
            errors.append(f"style_lock.page_chrome.{key} must be required or hidden")

    scenes = plan.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        errors.append("render-plan.json scenes must be a non-empty array")
        return

    total = len(scenes)
    previous_end = None
    for index, scene in enumerate(scenes, start=1):
        where = f"scene[{index}]"
        if not isinstance(scene, dict):
            errors.append(f"{where} must be an object")
            continue
        start, end = scene.get("start_frame"), scene.get("end_frame")
        if not isinstance(start, int) or not isinstance(end, int) or end <= start:
            errors.append(f"{where} must have integer end_frame > start_frame")
        elif previous_end is None and start != 0:
            errors.append(f"{where} must start at frame 0")
        elif previous_end is not None and start != previous_end:
            errors.append(f"{where} timeline gap/overlap: start={start}, expected={previous_end}")
        if isinstance(end, int):
            previous_end = end

        scene_background = scene.get("background_token")
        if color_mode != "mixed-intentional" and background and scene_background != background:
            errors.append(f"{where} background_token drifts from style_lock")
        if color_mode == "mixed-intentional" and background and scene_background != background:
            if not str(scene.get("background_change_reason", "")).strip():
                errors.append(f"{where} changes background without background_change_reason")

        chrome = require_object(scene, "chrome", where, errors)
        for key in ("corner_label", "page_number", "headline"):
            if chrome_lock.get(key) == "required" and not str(chrome.get(key, "")).strip():
                errors.append(f"{where}.chrome.{key} is required and cannot be empty")
        page_number = str(chrome.get("page_number", "")).strip()
        if chrome_lock.get("page_number") == "required":
            match = re.fullmatch(r"(\d+)\s*/\s*(\d+)", page_number)
            if not match or int(match.group(1)) != index or int(match.group(2)) != total:
                errors.append(f"{where}.chrome.page_number must identify page {index} / {total}")

        complexity = require_object(scene, "complexity", where, errors)
        for key, limit in COMPLEXITY_LIMITS.items():
            value = complexity.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"{where}.complexity.{key} must be a non-negative integer")
            elif value > limit:
                errors.append(f"{where}.complexity.{key}={value} exceeds default limit {limit}")

        persistent = scene.get("persistent_elements")
        if not isinstance(persistent, list):
            errors.append(f"{where}.persistent_elements must be an array")
        else:
            limit = 0 if profile == "page-isolated" else 1
            if len(persistent) > limit:
                errors.append(f"{where} has {len(persistent)} persistent elements; {profile} allows {limit}")

        if isinstance(start, int) and isinstance(end, int):
            for state in scene.get("states", []):
                if not isinstance(state, dict):
                    errors.append(f"{where}.states contains a non-object")
                    continue
                state_start, state_end = state.get("start_frame"), state.get("end_frame")
                if not isinstance(state_start, int) or not isinstance(state_end, int) or not (start <= state_start < state_end <= end):
                    errors.append(f"{where} state {state.get('id', '?')} falls outside scene frames")
            for event in scene.get("events", []):
                if not isinstance(event, dict):
                    errors.append(f"{where}.events contains a non-object")
                    continue
                event_start = event.get("start_frame")
                if not isinstance(event_start, int) or not (start <= event_start < end):
                    errors.append(f"{where} event {event.get('id', '?')} falls outside scene frames")
                if not str(event.get("cue_ref", "")).strip():
                    errors.append(f"{where} event {event.get('id', '?')} has no cue_ref")

    audio_path = project / str(plan.get("audio_file", ""))
    if not audio_path.is_file():
        errors.append(f"audio_file not found: {audio_path}")
    else:
        expected = plan.get("audio_hash")
        if expected != sha256(audio_path):
            errors.append("audio_hash does not match audio_file")

    storyboard = project / "STORYBOARD.md"
    if not storyboard.is_file():
        errors.append("missing file: STORYBOARD.md")
    elif plan.get("storyboard_hash") != sha256(storyboard):
        errors.append("storyboard_hash does not match STORYBOARD.md")

    caption_file = plan.get("caption_file")
    if caption_file and not (project / str(caption_file)).is_file():
        errors.append(f"caption_file not found: {caption_file}")


def validate_final(project: Path, final_path: Path, errors: list[str]) -> None:
    if not final_path.is_file():
        errors.append(f"final video not found: {final_path}")
        return
    duration = probe_duration(final_path)
    if duration is None:
        errors.append("ffprobe could not read final video")

    audit_path = project / "qc" / "pixel-audit.json"
    audit = read_json(audit_path, errors)
    if not audit:
        return
    declared_final = project / str(audit.get("final_file", ""))
    if declared_final.resolve() != final_path.resolve():
        errors.append("pixel-audit.json final_file does not match --final")
    interval = audit.get("sample_interval_seconds")
    if not isinstance(interval, (int, float)) or not 0 < interval <= 1:
        errors.append("pixel-audit.json sample_interval_seconds must be > 0 and <= 1")
    checks = audit.get("checks")
    required_checks = {"background_consistency", "corner_labels", "caption_appearance", "scene_residue"}
    if not isinstance(checks, dict):
        errors.append("pixel-audit.json checks must be an object")
    else:
        for key in sorted(required_checks):
            if checks.get(key) != "PASS":
                errors.append(f"pixel audit {key} must be PASS")
    evidence = audit.get("evidence_files")
    if not isinstance(evidence, list) or not evidence:
        errors.append("pixel-audit.json must list evidence_files")
    else:
        for item in evidence:
            if not (project / str(item)).is_file():
                errors.append(f"pixel audit evidence not found: {item}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--final", type=Path, help="also validate the encoded MP4 and qc/pixel-audit.json")
    args = parser.parse_args()

    project = args.project.resolve()
    errors: list[str] = []
    plan = read_json(project / "render-plan.json", errors)
    if plan:
        validate_plan(project, plan, errors)
    if args.final:
        final_path = args.final if args.final.is_absolute() else project / args.final
        validate_final(project, final_path.resolve(), errors)

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("PASS")
    print(f"- project: {project}")
    print(f"- profile: {plan.get('production_profile')}")
    print(f"- scenes: {len(plan.get('scenes', []))}")
    if args.final:
        print(f"- final: {final_path.resolve()}")


if __name__ == "__main__":
    main()
