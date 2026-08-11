import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from manifest_core import ManifestError, prepare_manifest  # noqa: E402
from publish_social import build_xiaohongshu_note_command, command_summary  # noqa: E402
from verify_xiaohongshu_note import resolve_match_title  # noqa: E402


class ManifestCoreTests(unittest.TestCase):
    def create_package(self, root: Path, title: str = "中文标题", body: str = "这是一段中文正文。") -> Path:
        (root / "content").mkdir()
        (root / "output").mkdir()
        (root / "content" / "title.txt").write_text(title, encoding="utf-8")
        (root / "content" / "body.md").write_text(body, encoding="utf-8")
        (root / "output" / "xhs-01.png").write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        manifest = {
            "schema_version": "1.0",
            "platform": "xiaohongshu",
            "content_type": "note",
            "account": "main",
            "expected_language": "zh-CN",
            "title_file": "content/title.txt",
            "body_file": "content/body.md",
            "media": ["output/xhs-01.png"],
            "tags": ["AI", "人工智能"],
            "browser_mode": "headless",
        }
        path = root / "publish-manifest.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        return path

    def test_valid_xiaohongshu_note_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = prepare_manifest(self.create_package(Path(directory)))
            self.assertEqual(prepared.report["status"], "preflight-passed")
            self.assertEqual(prepared.report["media_count"], 1)
            self.assertGreater(prepared.report["title_cjk"], 0)

    def test_blocks_question_mark_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.create_package(Path(directory), title="?AI?????????AI?????")
            with self.assertRaisesRegex(ManifestError, "question marks"):
                prepare_manifest(manifest)

    def test_accepts_windows_utf8_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.create_package(root)
            (root / "content" / "title.txt").write_text("中文标题", encoding="utf-8-sig")
            raw = manifest.read_text(encoding="utf-8")
            manifest.write_text(raw, encoding="utf-8-sig")
            prepared = prepare_manifest(manifest)
            self.assertEqual(prepared.title, "中文标题")

    def test_blocks_title_that_upstream_would_truncate(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.create_package(Path(directory), title="这是一个超过二十个字符并会被上游静默截断的小红书标题")
            with self.assertRaisesRegex(ManifestError, "20-character"):
                prepare_manifest(manifest)

    def test_reserved_adapter_is_not_reported_as_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.create_package(Path(directory))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["platform"] = "douyin"
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            prepared = prepare_manifest(manifest)
            self.assertEqual(prepared.report["status"], "adapter-reserved")

    def test_command_uses_argument_list_and_summary_redacts_text(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = prepare_manifest(self.create_package(Path(directory)))
            command = build_xiaohongshu_note_command(prepared, "sau")
            self.assertIn(prepared.title, command)
            self.assertIn(prepared.body, command)
            summary = command_summary(prepared, command)
            rendered = json.dumps(summary, ensure_ascii=False)
            self.assertNotIn(prepared.body, rendered)
            self.assertIn("UTF-8 text", rendered)

    def test_null_match_title_uses_prepared_title(self):
        self.assertEqual(resolve_match_title({"match_title": None}, "中文标题"), "中文标题")
        self.assertEqual(resolve_match_title({"match_title": ""}, "中文标题"), "中文标题")
        self.assertEqual(resolve_match_title({"match_title": "指定标题"}, "中文标题"), "指定标题")


if __name__ == "__main__":
    unittest.main()
