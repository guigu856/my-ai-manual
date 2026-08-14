from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from _common import SkillError, emit, fail


WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
HEADINGS = (
    "第一部分：这条视频是怎么立起来的",
    "第二部分：它用了什么素材和音乐",
    "第三部分：它怎么一段段剪出来的",
    "第四部分：如果重新做一条，应该学什么",
)
TIMELINE_COLUMNS = ("画面构成", "画面处理", "附加效果", "声音与节拍", "与下一段的衔接")
FORBIDDEN_TERMS = (
    "MusicSection",
    "MusicLayer",
    "AudioEvent",
    "EnergyCurve",
    "RhythmUnit",
    "MainShot",
    "InShotEvent",
    "AudioVisualBinding",
    "EditingSentence",
    "algorithm_candidate",
    "agent_inference",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="检查四部分通俗版视频拆解 DOCX。")
    parser.add_argument("report", type=Path)
    parser.add_argument("--rendered-pages-dir", type=Path)
    return parser


def document_text(path: Path) -> str:
    if not path.is_file():
        raise SkillError("report_missing", "指定的 DOCX 报告不存在。", {"path": str(path)})
    try:
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError) as error:
        raise SkillError("report_invalid", "文件不是有效的 DOCX 报告。") from error
    root = ElementTree.fromstring(xml)
    paragraphs = []
    for paragraph in root.iter(WORD_NS + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(WORD_NS + "t"))
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def validate(report: Path, rendered_pages_dir: Path | None) -> dict[str, object]:
    text = document_text(report)
    errors: dict[str, object] = {}
    warnings: list[str] = []
    positions = [text.find(heading) for heading in HEADINGS]
    missing = [heading for heading, position in zip(HEADINGS, positions) if position < 0]
    if missing:
        errors["missing_headings"] = missing
    elif positions != sorted(positions):
        errors["heading_order"] = "四部分标题没有按固定顺序出现"
    forbidden = [term for term in FORBIDDEN_TERMS if term in text]
    if forbidden:
        errors["forbidden_terms"] = forbidden
    if not re.search(r"\b\d{2}:\d{2}(?::\d{2})?\b", text):
        warnings.append("报告中没有找到时间戳")
    if not re.search(r"(画面依据|声音依据|证据)", text):
        warnings.append("报告中没有找到证据说明")
    if not re.search(r"把握程度[：:]?\s*(高|中|低)", text):
        warnings.append("报告中没有找到把握程度")
    missing_columns = [column for column in TIMELINE_COLUMNS if column not in text]
    if missing_columns:
        warnings.append(f"时间线缺列：{'、'.join(missing_columns)}")
    rendered_pages = []
    if rendered_pages_dir is not None:
        if rendered_pages_dir.is_dir():
            rendered_pages = sorted(
                str(path.resolve())
                for path in rendered_pages_dir.glob("*.png")
                if path.stat().st_size > 0
            )
        if not rendered_pages:
            errors["rendered_pages"] = "渲染目录中没有非空 PNG 页面"
    return {
        "ok": not errors,
        "report": str(report.resolve()),
        "part_count": sum(heading in text for heading in HEADINGS),
        "errors": errors,
        "warnings": warnings,
        "rendered_pages": rendered_pages,
    }


def main() -> int:
    try:
        args = build_parser().parse_args()
        result = validate(args.report, args.rendered_pages_dir)
        emit(result)
        return 0 if result["ok"] else 1
    except (SkillError, ElementTree.ParseError) as error:
        if isinstance(error, SkillError):
            return fail(error)
        return fail(SkillError("report_xml_invalid", "DOCX 主文档 XML 损坏。"))


if __name__ == "__main__":
    sys.exit(main())
