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


def _append_common_options(prepared: PreparedManifest, command: list[str]) -> list[str]:
    schedule = prepared.data.get("schedule")
    if schedule:
        command.extend(["--schedule", str(schedule)])
    browser_mode = str(prepared.data.get("browser_mode", "headless"))
    if browser_mode not in {"headless", "headed"}:
        raise ManifestError("browser_mode must be headless or headed")
    command.append(f"--{browser_mode}")
    return command


def build_xiaohongshu_note_command(prepared: PreparedManifest, sau: str) -> list[str]:
    command = [sau, "xiaohongshu", "upload-note", "--account", str(prepared.data["account"]), "--images", *map(str, prepared.media), "--title", prepared.title, "--note", prepared.body]
    tags = prepared.data.get("tags", [])
    if tags:
        command.extend(["--tags", ",".join(tags)])
    return _append_common_options(prepared, command)


def build_douyin_video_command(prepared: PreparedManifest, sau: str) -> list[str]:
    command = [sau, "douyin", "upload-video", "--account", str(prepared.data["account"]), "--file", str(prepared.media[0]), "--title", prepared.title, "--desc", prepared.body]
    tags = prepared.data.get("tags", [])
    if tags:
        command.extend(["--tags", ",".join(tags)])
    if "landscape" in prepared.covers:
        command.extend(["--thumbnail-landscape", str(prepared.covers["landscape"])])
    if "portrait" in prepared.covers:
        command.extend(["--thumbnail-portrait", str(prepared.covers["portrait"])])
    return _append_common_options(prepared, command)


def build_command(prepared: PreparedManifest, sau: str) -> list[str]:
    builders = {"xiaohongshu/note": build_xiaohongshu_note_command, "douyin/video": build_douyin_video_command}
    builder = builders.get(prepared.report["adapter"])
    if builder is None:
        raise ManifestError(f"adapter {prepared.report['adapter']} has no executor")
    return builder(prepared, sau)


def command_summary(prepared: PreparedManifest, command: list[str]) -> dict[str, Any]:
    media_flag = "--images" if prepared.report["adapter"] == "xiaohongshu/note" else "--file"
    summary_command = [command[0], prepared.report["platform"], command[2], "--account", str(prepared.data["account"]), media_flag, f"<{len(prepared.media)} ordered media file(s)>", "--title", f"<UTF-8 text chars={len(prepared.title)} sha256={prepared.title_sha256[:12]}>"]
    body_flag = "--note" if prepared.report["adapter"] == "xiaohongshu/note" else "--desc"
    summary_command.extend([body_flag, f"<UTF-8 text chars={len(prepared.body)} sha256={prepared.body_sha256[:12]}>"])
    if prepared.covers:
        summary_command.extend(["--covers", f"<{','.join(sorted(prepared.covers))}>"])
    return {
        **prepared.report,
        "executor": command[0],
        "command": summary_command,
        "tags_count": len(prepared.data.get("tags", [])),
        "browser_mode": prepared.data.get("browser_mode", "headless"),
        "visibility": prepared.data.get("visibility", "public"),
    }


def run_check(sau: str, platform: str, account: str) -> bool:
    result = subprocess.run([sau, platform, "check", "--account", account], capture_output=True, text=True, encoding="utf-8", errors="replace")
    output = (result.stdout + "\n" + result.stderr).lower()
    return result.returncode == 0 and "valid" in output and "invalid" not in output


def _submission_succeeded(adapter: str, result: subprocess.CompletedProcess[str]) -> bool:
    combined = (result.stdout + "\n" + result.stderr).lower()
    markers = {
        "xiaohongshu/note": ("note upload submitted", "publish/success"),
        "douyin/video": ("douyin video upload submitted", "publish/success"),
    }
    return result.returncode == 0 and any(marker in combined for marker in markers.get(adapter, ()))


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
        command = build_command(prepared, sau)
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
    platform = str(prepared.report["platform"])
    if not run_check(sau, platform, account):
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
    submitted = _submission_succeeded(prepared.report["adapter"], result)
    report = {
        **summary,
        "status": "submitted" if submitted else "submit-failed",
        "submitted_at": datetime.now(timezone.utc).isoformat() if submitted else None,
        "return_code": result.returncode,
        "warnings": summary.get("warnings", []),
        "missing_evidence": ["online title/body/media/cover round-trip"] if submitted else [],
        "report": str(report_path),
    }
    write_json(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if submitted else 6


if __name__ == "__main__":
    raise SystemExit(main())
