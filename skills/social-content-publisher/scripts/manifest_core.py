from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "internal-module"


SECRET_KEYS = {
    "api_key",
    "apikey",
    "cookie",
    "cookies",
    "password",
    "private_key",
    "secret",
    "token",
}
ALLOWED_SECRET_PATH_KEYS = {"account_file"}
QUESTION_RUN = re.compile(r"\?{4,}")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class PreparedManifest:
    path: Path
    data: dict[str, Any]
    title: str
    body: str
    media: tuple[Path, ...]
    title_sha256: str
    body_sha256: str
    media_sha256: tuple[str, ...]
    publish_intent_id: str
    report: dict[str, Any]


def load_utf8_json(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        raise ManifestError(f"manifest is not strict UTF-8: {path}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"invalid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError("manifest root must be an object")
    return data


def resolve_path(manifest_path: Path, value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = manifest_path.parent / path
    return path.resolve()


def read_utf8(path: Path, label: str) -> str:
    if not path.is_file():
        raise ManifestError(f"{label} file does not exist: {path}")
    try:
        return path.read_text(encoding="utf-8-sig", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise ManifestError(f"{label} is not strict UTF-8: {path}") from exc


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_cjk(value: str) -> int:
    return len(CJK.findall(value))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _scan_secret_keys(value: Any, path: str = "root") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_lower = str(key).lower()
            if key_lower in SECRET_KEYS and key_lower not in ALLOWED_SECRET_PATH_KEYS:
                findings.append(f"{path}.{key}")
            findings.extend(_scan_secret_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(_scan_secret_keys(child, f"{path}[{index}]"))
    return findings


def _require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{key} must be a non-empty string")
    return value.strip()


def prepare_manifest(path_value: str | Path) -> PreparedManifest:
    path = Path(path_value).expanduser().resolve()
    data = load_utf8_json(path)
    if data.get("schema_version") != "1.0":
        raise ManifestError("schema_version must be '1.0'")

    platform = _require_string(data, "platform").lower()
    content_type = _require_string(data, "content_type").lower()
    account = _require_string(data, "account")
    title_file = resolve_path(path, _require_string(data, "title_file"))
    body_file = resolve_path(path, _require_string(data, "body_file"))
    title = read_utf8(title_file, "title")
    body = read_utf8(body_file, "body")

    secret_findings = _scan_secret_keys(data)
    if secret_findings:
        raise ManifestError("secret-like fields are forbidden: " + ", ".join(secret_findings))

    if "\ufffd" in title or "\ufffd" in body:
        raise ManifestError("Unicode replacement character detected")
    if QUESTION_RUN.search(title) or QUESTION_RUN.search(body):
        raise ManifestError("suspicious run of question marks detected")

    expected_language = str(data.get("expected_language", "zh-CN"))
    if expected_language.lower().startswith("zh"):
        if count_cjk(title) == 0:
            raise ManifestError("Chinese title contains no CJK characters")
        if count_cjk(body) == 0:
            raise ManifestError("Chinese body contains no CJK characters")

    media_raw = data.get("media")
    if not isinstance(media_raw, list) or not media_raw:
        raise ManifestError("media must be a non-empty list")
    media: list[Path] = []
    for index, item in enumerate(media_raw):
        if not isinstance(item, str) or not item.strip():
            raise ManifestError(f"media[{index}] must be a path string")
        media_path = resolve_path(path, item)
        if not media_path.is_file():
            raise ManifestError(f"media file does not exist: {media_path}")
        media.append(media_path)
    normalized_paths = [str(item).casefold() for item in media]
    if len(normalized_paths) != len(set(normalized_paths)):
        raise ManifestError("duplicate media paths are not allowed")

    tags = data.get("tags", [])
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise ManifestError("tags must be a list of strings")

    adapter = f"{platform}/{content_type}"
    warnings: list[str] = []
    status = "adapter-reserved"
    if adapter == "xiaohongshu/note":
        status = "preflight-passed"
        if len(title) > 20:
            raise ManifestError("xiaohongshu/note title exceeds 20-character adapter safety limit")
        if len(media) > 18:
            raise ManifestError("xiaohongshu/note media count exceeds observed 18-image limit")
        allowed = {".jpg", ".jpeg", ".png"}
        invalid = [str(item) for item in media if item.suffix.lower() not in allowed]
        if invalid:
            raise ManifestError("xiaohongshu/note only accepts PNG/JPEG in this adapter: " + ", ".join(invalid))
        unreadable: list[str] = []
        for item in media:
            header = item.read_bytes()[:8]
            if item.suffix.lower() == ".png" and header != b"\x89PNG\r\n\x1a\n":
                unreadable.append(str(item))
            if item.suffix.lower() in {".jpg", ".jpeg"} and not header.startswith(b"\xff\xd8\xff"):
                unreadable.append(str(item))
        if unreadable:
            raise ManifestError("media signature does not match extension: " + ", ".join(unreadable))
    else:
        warnings.append(f"adapter {adapter} is reserved and lacks local end-to-end evidence")

    title_hash = sha256_text(title)
    body_hash = sha256_text(body)
    media_hashes = tuple(sha256_file(item) for item in media)
    intent_payload = {
        "platform": platform,
        "content_type": content_type,
        "account": account,
        "title_sha256": title_hash,
        "body_sha256": body_hash,
        "media_sha256": media_hashes,
        "schedule": data.get("schedule"),
        "visibility": data.get("visibility", "public"),
    }
    intent_id = "sha256:" + sha256_text(json.dumps(intent_payload, ensure_ascii=False, sort_keys=True))
    report = {
        "status": status,
        "adapter": adapter,
        "platform": platform,
        "content_type": content_type,
        "account": account,
        "publish_intent_id": intent_id,
        "title_chars": len(title),
        "title_cjk": count_cjk(title),
        "title_sha256": title_hash,
        "body_chars": len(body),
        "body_cjk": count_cjk(body),
        "body_sha256": body_hash,
        "media_count": len(media),
        "media_sha256": media_hashes,
        "schedule": data.get("schedule"),
        "warnings": warnings,
    }
    return PreparedManifest(
        path=path,
        data=data,
        title=title,
        body=body,
        media=tuple(media),
        title_sha256=title_hash,
        body_sha256=body_hash,
        media_sha256=media_hashes,
        publish_intent_id=intent_id,
        report=report,
    )


def default_report_path(prepared: PreparedManifest) -> Path:
    directory = prepared.path.parent / ".publish-reports"
    safe_id = prepared.publish_intent_id.split(":", 1)[1][:16]
    return directory / f"{safe_id}.json"


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
