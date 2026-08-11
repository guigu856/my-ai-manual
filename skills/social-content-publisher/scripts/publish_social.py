from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from manifest_core import ManifestError, PreparedManifest, default_report_path, prepare_manifest, write_json


def resolve_sau(prepared: PreparedManifest, explicit: str | None) -> str:
    runtime = prepared.data.get("runtime", {})
    configured = runtime.get("sau_path") if isinstance(runtime, dict) else None
    candidate = explicit or configured or shutil.which("sau")
    if not candidate:
        raise ManifestError("sau executable not found; set runtime.sau_path or --sau")
    path = Path(candidate).expanduser()
    if path.is_absolute() and not path.is_file():
        raise ManifestError(f"configured sau executable does not exist: {path}")
    return str(path if path.is_absolute() else candidate)


def build_xiaohongshu_note_command(prepared: PreparedManifest, sau: str) -> list[str]:
    command = [
        sau,
        "xiaohongshu",
        "upload-note",
        "--account",
        str(prepared.data["account"]),
        "--images",
        *[str(item) for item in prepared.media],
        "--title",
        prepared.title,
        "--note",
        prepared.body,
    ]
    tags = prepared.data.get("tags", [])
    if tags:
        command.extend(["--tags", ",".join(tags)])
    schedule = prepared.data.get("schedule")
    if schedule:
        command.extend(["--schedule", str(schedule)])
    browser_mode = str(prepared.data.get("browser_mode", "headless"))
    if browser_mode == "headless":
        command.append("--headless")
    elif browser_mode == "headed":
        command.append("--headed")
    else:
        raise ManifestError("browser_mode must be headless or headed")
    return command


def command_summary(prepared: PreparedManifest, command: list[str]) -> dict[str, Any]:
    return {
        **prepared.report,
        "executor": command[0],
        "command": [
            command[0],
            "xiaohongshu",
            "upload-note",
            "--account",
            str(prepared.data["account"]),
            "--images",
            f"<{len(prepared.media)} ordered media files>",
            "--title",
            f"<UTF-8 text chars={len(prepared.title)} sha256={prepared.title_sha256[:12]}>",
            "--note",
            f"<UTF-8 text chars={len(prepared.body)} sha256={prepared.body_sha256[:12]}>",
        ],
    }


def run_check(sau: str, account: str) -> bool:
    result = subprocess.run(
        [sau, "xiaohongshu", "check", "--account", account],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output = (result.stdout + "\n" + result.stderr).lower()
    return result.returncode == 0 and "valid" in output and "invalid" not in output


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or submit a social content publish manifest.")
    parser.add_argument("manifest")
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--sau")
    parser.add_argument("--report")
    args = parser.parse_args()
    try:
        prepared = prepare_manifest(args.manifest)
        if prepared.report["status"] != "preflight-passed":
            print(json.dumps(prepared.report, ensure_ascii=False, indent=2))
            return 3
        sau = resolve_sau(prepared, args.sau)
        command = build_xiaohongshu_note_command(prepared, sau)
    except ManifestError as exc:
        print(json.dumps({"status": "preflight-failed", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    report_path = Path(args.report).expanduser().resolve() if args.report else default_report_path(prepared)
    if report_path.is_file():
        existing = json.loads(report_path.read_text(encoding="utf-8"))
        if existing.get("status") == "published-verified":
            print(json.dumps({"status": "duplicate-blocked", "report": str(report_path)}, ensure_ascii=False, indent=2))
            return 4

    summary = command_summary(prepared, command)
    if not args.submit:
        write_json(report_path, {**summary, "status": "preflight-passed", "dry_run": True})
        print(json.dumps({**summary, "report": str(report_path)}, ensure_ascii=False, indent=2))
        return 0

    account = str(prepared.data["account"])
    if not run_check(sau, account):
        report = {**summary, "status": "auth-required", "report": str(report_path)}
        write_json(report_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 5

    environment = os.environ.copy()
    environment.setdefault("PYTHONUTF8", "1")
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=environment)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    combined = result.stdout + "\n" + result.stderr
    submitted = result.returncode == 0 and (
        "note upload submitted" in combined.lower() or "图文发布成功" in combined or "publish/success" in combined
    )
    report = {
        **summary,
        "status": "submitted" if submitted else "submit-failed",
        "submitted_at": datetime.now(timezone.utc).isoformat() if submitted else None,
        "return_code": result.returncode,
        "warnings": summary.get("warnings", []),
        "missing_evidence": ["online title/body/media round-trip"] if submitted else [],
        "report": str(report_path),
    }
    write_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if submitted else 6


if __name__ == "__main__":
    raise SystemExit(main())
