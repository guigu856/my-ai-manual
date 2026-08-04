#!/usr/bin/env python3
"""Validate the structural contract of an explainer-video review report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DIMENSIONS = {
    "visual_expression",
    "spatial_continuity",
    "temporal_alignment",
    "subtitle_readability",
}
STATUSES = {"pass", "warn", "fail", "missing_evidence"}
SEVERITIES = {"blocker", "major", "minor", "note"}
CONFIDENCES = {"high", "medium", "low"}


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate(payload: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(payload, dict):
        return {"ok": False, "errors": ["report root must be an object"], "warnings": []}
    for key in ("schema_version", "skill", "run_id", "media", "sampling", "overall", "dimensions", "findings", "handoff", "evidence_boundary"):
        if key not in payload:
            add_error(errors, f"missing root field: {key}")
    if payload.get("skill") != "explainer-video-review":
        add_error(errors, "skill must be explainer-video-review")

    media = payload.get("media")
    if not isinstance(media, dict):
        add_error(errors, "media must be an object")
        duration = None
    else:
        duration = media.get("duration_s")
        if not isinstance(duration, (int, float)) or duration <= 0:
            add_error(errors, "media.duration_s must be greater than 0")
        for key in ("path", "fps", "width", "height"):
            if key not in media:
                add_error(errors, f"media missing field: {key}")

    overall = payload.get("overall")
    if not isinstance(overall, dict):
        add_error(errors, "overall must be an object")
    else:
        for key in ("status", "severity", "confidence"):
            if key not in overall:
                add_error(errors, f"overall missing field: {key}")
        if overall.get("status") not in STATUSES:
            add_error(errors, "overall.status is invalid")
        if overall.get("severity") not in SEVERITIES:
            add_error(errors, "overall.severity is invalid")
        if overall.get("confidence") not in CONFIDENCES:
            add_error(errors, "overall.confidence is invalid")

    dimensions = payload.get("dimensions")
    seen_dimensions: set[str] = set()
    if not isinstance(dimensions, list):
        add_error(errors, "dimensions must be a list")
    else:
        for index, item in enumerate(dimensions):
            if not isinstance(item, dict):
                add_error(errors, f"dimensions[{index}] must be an object")
                continue
            dimension_id = item.get("id")
            if dimension_id in seen_dimensions:
                add_error(errors, f"duplicate dimension id: {dimension_id}")
            seen_dimensions.add(dimension_id)
            if dimension_id not in DIMENSIONS:
                add_error(errors, f"unknown dimension id: {dimension_id}")
            if item.get("status") not in STATUSES:
                add_error(errors, f"dimensions[{index}].status is invalid")
    missing_dimensions = DIMENSIONS - seen_dimensions
    for dimension_id in sorted(missing_dimensions):
        add_error(errors, f"missing dimension: {dimension_id}")

    findings = payload.get("findings")
    seen_findings: set[str] = set()
    if not isinstance(findings, list):
        add_error(errors, "findings must be a list")
    else:
        for index, finding in enumerate(findings):
            if not isinstance(finding, dict):
                add_error(errors, f"findings[{index}] must be an object")
                continue
            finding_id = finding.get("id")
            if not isinstance(finding_id, str) or not finding_id or finding_id in seen_findings:
                add_error(errors, f"findings[{index}] has missing or duplicate id")
            else:
                seen_findings.add(finding_id)
            for key in ("dimension", "status", "severity", "confidence", "evidence", "issue", "repair"):
                if key not in finding:
                    add_error(errors, f"findings[{index}] missing field: {key}")
            if finding.get("dimension") not in DIMENSIONS:
                add_error(errors, f"findings[{index}].dimension is invalid")
            if finding.get("status") not in STATUSES:
                add_error(errors, f"findings[{index}].status is invalid")
            if finding.get("severity") not in SEVERITIES:
                add_error(errors, f"findings[{index}].severity is invalid")
            if finding.get("confidence") not in CONFIDENCES:
                add_error(errors, f"findings[{index}].confidence is invalid")
            evidence = finding.get("evidence")
            if not isinstance(evidence, list) or (finding.get("status") != "missing_evidence" and not evidence):
                add_error(errors, f"findings[{index}] needs evidence unless status is missing_evidence")
            if duration is not None:
                start = finding.get("start_s", 0.0)
                end = finding.get("end_s", start)
                if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                    add_error(errors, f"findings[{index}] timestamps must be numeric")
                elif start < 0 or end < start or end > duration:
                    add_error(errors, f"findings[{index}] timestamps fall outside media duration")

    sampling = payload.get("sampling")
    if not isinstance(sampling, dict):
        add_error(errors, "sampling must be an object")
    elif sampling.get("preset") not in {"quick", "standard", "dense"}:
        add_error(errors, "sampling.preset is invalid")

    handoff = payload.get("handoff")
    if not isinstance(handoff, dict):
        add_error(errors, "handoff must be an object")
    else:
        for key in ("target_skill", "rerender_required", "re_review_required"):
            if key not in handoff:
                add_error(errors, f"handoff missing field: {key}")

    boundary = payload.get("evidence_boundary")
    if not isinstance(boundary, dict):
        add_error(errors, "evidence_boundary must be an object")
    else:
        for key in ("observed", "missing_evidence"):
            if not isinstance(boundary.get(key), list):
                add_error(errors, f"evidence_boundary.{key} must be a list")

    if isinstance(overall, dict) and overall.get("status") == "pass" and findings:
        blocking = [f for f in findings if isinstance(f, dict) and f.get("status") == "fail"]
        if blocking:
            warnings.append("overall.status is pass while fail findings exist")
    return {"ok": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an explainer-video review report.")
    parser.add_argument("--input", type=Path, required=True, help="Path to review-report.json.")
    parser.add_argument("--output", type=Path, help="Optional JSON result path.")
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        result = validate(payload)
    except (OSError, json.JSONDecodeError) as exc:
        result = {"ok": False, "errors": [str(exc)], "warnings": []}
    result["input"] = str(args.input)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
