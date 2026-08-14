from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "validate_report.py"
HEADINGS = (
    "第一部分：这条视频是怎么立起来的",
    "第二部分：它用了什么素材和音乐",
    "第三部分：它怎么一段段剪出来的",
    "第四部分：如果重新做一条，应该学什么",
)


def write_docx(path: Path, paragraphs: list[str]) -> None:
    body = "".join(
        f"<w:p><w:r><w:t>{escape(text)}</w:t></w:r></w:p>" for text in paragraphs
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f"<w:body>{body}<w:sectPr/></w:body></w:document>"
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("word/document.xml", document)


class ValidateReportTests(unittest.TestCase):
    def run_validator(self, docx: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(docx)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_plain_language_four_part_report_passes(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            report = Path(temp_dir) / "report.docx"
            write_docx(
                report,
                [
                    *HEADINGS,
                    "00:00–00:02 画面构成：人物出现；画面处理：从下方进入后放大；"
                    "附加效果：颗粒；声音与节拍：第一重拍；与下一段的衔接：相同方向连接。",
                    "画面依据：F001；声音依据：A001；把握程度：高。",
                ],
            )
            result = self.run_validator(report)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)["ok"])

    def test_missing_timeline_column_warns(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            report = Path(temp_dir) / "report.docx"
            write_docx(
                report,
                [
                    *HEADINGS,
                    "00:00–00:02 主要画面出现人物，音乐逐渐增强。",
                    "画面依据：F001；声音依据：A001；把握程度：高。",
                ],
            )
            result = self.run_validator(report)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(any("时间线缺列" in warning for warning in payload["warnings"]))

    def test_internal_terms_fail(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            report = Path(temp_dir) / "report.docx"
            write_docx(report, [*HEADINGS, "RhythmUnit 与 MainShot", "00:01，把握程度：中"])
            result = self.run_validator(report)
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertIn("forbidden_terms", payload["errors"])


if __name__ == "__main__":
    unittest.main()
