#!/usr/bin/env python3
"""Validate the deterministic structure of a publish-ready XHS image package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
CARD_NAME = re.compile(r"^xhs-(\d{2})\.png$", re.IGNORECASE)


@dataclass
class Finding:
    level: str
    code: str
    message: str


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError("not a valid PNG IHDR header")
    return struct.unpack(">II", header[16:24])


def section_text(markdown: str, heading: str) -> str:
    pattern = re.compile(
        rf"(?ms)^#\s+{re.escape(heading)}\s*$\n(.*?)(?=^#\s+|\Z)"
    )
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def validate(package: Path) -> list[Finding]:
    findings: list[Finding] = []

    def add(level: str, code: str, message: str) -> None:
        findings.append(Finding(level, code, message))

    if not package.is_dir():
        return [Finding("FAIL", "P0", f"package directory not found: {package}")]

    post = package / "post.md"
    if not post.is_file():
        add("FAIL", "P1", "missing post.md")
    else:
        markdown = post.read_text(encoding="utf-8")
        if not section_text(markdown, "标题"):
            add("FAIL", "P2", "post.md has no non-empty '# 标题' section")
        if not section_text(markdown, "正文"):
            add("FAIL", "P3", "post.md has no non-empty '# 正文' section")

    if not (package / "page-plan.md").is_file():
        add("FAIL", "P4", "missing page-plan.md")
    if not (package / "qa-report.md").is_file():
        add("FAIL", "P5", "missing qa-report.md")

    output = package / "output"
    cards = sorted(output.glob("xhs-*.png")) if output.is_dir() else []
    if not output.is_dir():
        add("FAIL", "P6", "missing output directory")
    if not 5 <= len(cards) <= 18:
        add("FAIL", "P7", f"expected 5-18 cards, found {len(cards)}")

    expected_names = [f"xhs-{index:02d}.png" for index in range(1, len(cards) + 1)]
    actual_names = [card.name.lower() for card in cards]
    if cards and actual_names != expected_names:
        add("FAIL", "P8", f"card names are not contiguous: {actual_names}")

    digests: dict[str, list[str]] = {}
    for card in cards:
        if not CARD_NAME.match(card.name):
            add("FAIL", "P9", f"invalid card filename: {card.name}")
            continue
        try:
            width, height = png_size(card)
        except ValueError as exc:
            add("FAIL", "P10", f"{card.name}: {exc}")
            continue
        if (width, height) != (1080, 1440):
            add("FAIL", "P11", f"{card.name}: expected 1080x1440, got {width}x{height}")
        if card.stat().st_size > 20 * 1024 * 1024:
            add("WARN", "P12", f"{card.name}: larger than 20 MiB")
        digest = hashlib.sha256(card.read_bytes()).hexdigest()
        digests.setdefault(digest, []).append(card.name)

    for names in digests.values():
        if len(names) > 1:
            add("WARN", "P13", f"byte-identical cards: {', '.join(names)}")

    previews = [
        package / "preview" / "contact-sheet.jpg",
        package / "preview" / "contact-sheet.png",
        output / "contact-sheet.jpg",
        output / "contact-sheet.png",
    ]
    if not any(path.is_file() for path in previews):
        add("FAIL", "P14", "missing contact sheet in preview/ or output/")

    sources = package / "assets" / "SOURCES.md"
    if not sources.is_file():
        add("WARN", "P15", "missing assets/SOURCES.md; add '无外部素材' when applicable")

    if not findings:
        add("PASS", "P16", f"package structure and {len(cards)} PNG cards passed")
    elif not any(item.level == "FAIL" for item in findings):
        add("PASS", "P16", f"package passed with {len(cards)} PNG cards and warnings")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()

    findings = validate(args.package.resolve())
    payload = {
        "package": str(args.package.resolve()),
        "status": "fail" if any(item.level == "FAIL" for item in findings) else "pass",
        "findings": [asdict(item) for item in findings],
    }
    for item in findings:
        print(f"{item.level} {item.code}: {item.message}")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
