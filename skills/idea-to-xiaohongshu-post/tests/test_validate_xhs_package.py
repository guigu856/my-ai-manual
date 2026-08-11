#!/usr/bin/env python3

from __future__ import annotations

import binascii
import importlib.util
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_xhs_package.py"
SPEC = importlib.util.spec_from_file_location("validate_xhs_package", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int) -> None:
    raw = b"".join(b"\x00" + b"\xff\xff\xff" * width for _ in range(height))
    data = (
        MODULE.PNG_SIGNATURE
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def create_package(root: Path, count: int = 5, size: tuple[int, int] = (1080, 1440)) -> None:
    (root / "output").mkdir(parents=True)
    (root / "preview").mkdir()
    (root / "assets").mkdir()
    (root / "post.md").write_text("# 标题\n测试标题\n\n# 正文\n测试正文\n", encoding="utf-8")
    (root / "page-plan.md").write_text("# Page Plan\n", encoding="utf-8")
    (root / "qa-report.md").write_text("# QA Report\n", encoding="utf-8")
    (root / "assets" / "SOURCES.md").write_text("无外部素材\n", encoding="utf-8")
    (root / "preview" / "contact-sheet.jpg").write_bytes(b"preview")
    for index in range(1, count + 1):
        write_png(root / "output" / f"xhs-{index:02d}.png", *size)


class PackageValidationTests(unittest.TestCase):
    def test_valid_package_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            create_package(root)
            findings = MODULE.validate(root)
            self.assertFalse(any(item.level == "FAIL" for item in findings))

    def test_wrong_dimensions_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            create_package(root, size=(1080, 1080))
            findings = MODULE.validate(root)
            self.assertTrue(any(item.code == "P11" and item.level == "FAIL" for item in findings))

    def test_missing_post_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            create_package(root)
            (root / "post.md").unlink()
            findings = MODULE.validate(root)
            self.assertTrue(any(item.code == "P1" and item.level == "FAIL" for item in findings))


if __name__ == "__main__":
    unittest.main()
