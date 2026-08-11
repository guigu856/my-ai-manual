import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from manifest_core import ManifestError, prepare_manifest  # noqa: E402
from publish_social import (  # noqa: E402
    build_douyin_video_command,
    build_xiaohongshu_note_command,
    command_summary,
    _submission_succeeded,
)
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

    def make_douyin_video(self, root: Path, title: str = "真正拉开差距的是判断力", body: str = "这是一段抖音视频文案。") -> Path:
        manifest = self.create_package(root, title, body)
        (root / "output" / "video.mp4").write_bytes(b"\x00\x00\x00\x18ftypmp42fixture")
        (root / "output" / "cover-landscape.jpg").write_bytes(b"\xff\xd8\xfffixture")
        (root / "output" / "cover-portrait.png").write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data.update(
            {
                "platform": "douyin",
                "content_type": "video",
                "media": ["output/video.mp4"],
                "covers": {
                    "landscape": "output/cover-landscape.jpg",
                    "portrait": "output/cover-portrait.png",
                },
                "schedule": "2026-08-13 20:00",
                "browser_mode": "headed",
            }
        )
        manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return manifest

    def test_valid_xiaohongshu_note_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = prepare_manifest(self.create_package(Path(directory)))
            self.assertEqual(prepared.report["status"], "preflight-passed")
            self.assertEqual(prepared.report["media_count"], 1)
            self.assertGreater(prepared.report["title_cjk"], 0)

    def test_valid_douyin_video_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = prepare_manifest(self.make_douyin_video(Path(directory)))
            self.assertEqual(prepared.report["adapter"], "douyin/video")
            self.assertEqual(prepared.report["status"], "preflight-passed")
            self.assertEqual(prepared.report["covers"], ["landscape", "portrait"])

    def test_douyin_video_requires_one_video(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.make_douyin_video(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["media"].append("output/video.mp4")
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaisesRegex(ManifestError, "duplicate media"):
                prepare_manifest(manifest)

    def test_douyin_video_limits_title_and_body(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ManifestError, "30-character"):
                prepare_manifest(self.make_douyin_video(Path(directory), title="中" * 31))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ManifestError, "1000-character"):
                prepare_manifest(self.make_douyin_video(Path(directory), body="中" * 1001))

    def test_douyin_command_maps_text_tags_covers_schedule_and_mode(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = prepare_manifest(self.make_douyin_video(Path(directory)))
            command = build_douyin_video_command(prepared, "sau")
            self.assertEqual(command[:3], ["sau", "douyin", "upload-video"])
            for flag in ("--file", "--title", "--desc", "--tags", "--thumbnail-landscape", "--thumbnail-portrait", "--schedule", "--headed"):
                self.assertIn(flag, command)
            summary = json.dumps(command_summary(prepared, command), ensure_ascii=False)
            self.assertNotIn(prepared.title, summary)
            self.assertNotIn(prepared.body, summary)

    def test_douyin_submission_marker_is_platform_specific(self):
        success = subprocess.CompletedProcess([], 0, stdout="Douyin video upload submitted: fixture.mp4", stderr="")
        unrelated = subprocess.CompletedProcess([], 0, stdout="Kuaishou video upload submitted: fixture.mp4", stderr="")
        self.assertTrue(_submission_succeeded("douyin/video", success))
        self.assertFalse(_submission_succeeded("douyin/video", unrelated))

    def test_douyin_note_remains_reserved(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = self.create_package(Path(directory))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data.update({"platform": "douyin", "content_type": "note"})
            manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(prepare_manifest(manifest).report["status"], "adapter-reserved")

    def test_cover_signature_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.make_douyin_video(root)
            (root / "output" / "cover-portrait.png").write_bytes(b"not-a-png")
            with self.assertRaisesRegex(ManifestError, "signature"):
                prepare_manifest(manifest)

    def test_blocks_question_mark_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ManifestError, "question marks"):
                prepare_manifest(self.create_package(Path(directory), title="AI?????????AI"))

    def test_accepts_windows_utf8_bom(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = self.create_package(root)
            (root / "content" / "title.txt").write_text("中文标题", encoding="utf-8-sig")
            manifest.write_text(manifest.read_text(encoding="utf-8"), encoding="utf-8-sig")
            self.assertEqual(prepare_manifest(manifest).title, "中文标题")

    def test_blocks_xiaohongshu_title_that_upstream_would_truncate(self):
        with tempfile.TemporaryDirectory() as directory:
            title = "这是一个超过二十个字符并会被上游静默截断的小红书标题"
            with self.assertRaisesRegex(ManifestError, "20-character"):
                prepare_manifest(self.create_package(Path(directory), title=title))

    def test_xiaohongshu_command_uses_argument_list_and_redacted_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            prepared = prepare_manifest(self.create_package(Path(directory)))
            command = build_xiaohongshu_note_command(prepared, "sau")
            self.assertIn(prepared.title, command)
            self.assertIn(prepared.body, command)
            rendered = json.dumps(command_summary(prepared, command), ensure_ascii=False)
            self.assertNotIn(prepared.body, rendered)
            self.assertIn("UTF-8 text", rendered)

    def test_null_match_title_uses_prepared_title(self):
        self.assertEqual(resolve_match_title({"match_title": None}, "中文标题"), "中文标题")
        self.assertEqual(resolve_match_title({"match_title": ""}, "中文标题"), "中文标题")
        self.assertEqual(resolve_match_title({"match_title": "指定标题"}, "中文标题"), "指定标题")


if __name__ == "__main__":
    unittest.main()
