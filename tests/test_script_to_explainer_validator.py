from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "skills" / "script-to-explainer-video" / "scripts" / "validate_project.py"


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        (self.project / "audio").mkdir()
        (self.project / "audio" / "master.wav").write_bytes(b"voice-clock")
        (self.project / "audio" / "captions.json").write_text('{"cues": []}', encoding="utf-8")
        (self.project / "STORYBOARD.md").write_text("# locked storyboard\n", encoding="utf-8")
        self.plan = self.make_plan()
        self.write_plan()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_plan(self) -> dict:
        scenes = []
        for index, (start, end) in enumerate(((0, 90), (90, 180)), start=1):
            scenes.append({
                "id": f"S{index:02d}",
                "beat_ids": [f"B{index:02d}"],
                "start_frame": start,
                "end_frame": end,
                "background_token": "background.system-lab.dark",
                "chrome": {
                    "corner_label": f"段落 {index}",
                    "page_number": f"{index:02d} / 02",
                    "headline": f"判断 {index}",
                },
                "complexity": {
                    "focal_points": 1,
                    "content_groups": 2,
                    "simultaneous_text_blocks": 3,
                    "primary_motion_relations": 1,
                },
                "persistent_elements": [],
                "states": [{
                    "id": f"S{index:02d}_ST1",
                    "meaning": "stable",
                    "start_frame": start,
                    "end_frame": end,
                    "visible_elements": ["headline"],
                }],
                "events": [{
                    "id": f"S{index:02d}_E1",
                    "action": "reveal",
                    "cue_ref": f"B{index:02d}.start",
                    "start_frame": start,
                    "duration_frames": 6,
                    "targets": ["headline"],
                }],
            })
        audio = self.project / "audio" / "master.wav"
        storyboard = self.project / "STORYBOARD.md"
        return {
            "schema_version": "2.1.0",
            "storyboard_hash": digest(storyboard),
            "audio_hash": digest(audio),
            "production_profile": "page-isolated",
            "canvas": {"width": 1400, "height": 1000},
            "fps": 30,
            "audio_file": "audio/master.wav",
            "caption_file": "audio/captions.json",
            "engine": "hyperframes",
            "style_lock": {
                "color_mode": "dark",
                "background_token": "background.system-lab.dark",
                "caption": {
                    "background": "none",
                    "background_alpha": 0,
                    "outline_px": 0,
                    "shadow": False,
                    "max_lines": 1,
                },
                "page_chrome": {
                    "corner_label": "required",
                    "page_number": "required",
                    "headline": "required",
                },
            },
            "scenes": scenes,
        }

    def write_plan(self) -> None:
        (self.project / "render-plan.json").write_text(
            json.dumps(self.plan, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--project", str(self.project)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_valid_page_isolated_project_passes(self) -> None:
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_mixed_background_without_intent_fails(self) -> None:
        self.plan["scenes"][1]["background_token"] = "background.paper.light"
        self.write_plan()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("background_token drifts", result.stdout)

    def test_missing_corner_label_fails(self) -> None:
        self.plan["scenes"][0]["chrome"]["corner_label"] = ""
        self.write_plan()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("corner_label is required", result.stdout)

    def test_intentional_background_change_requires_reason(self) -> None:
        self.plan["style_lock"]["color_mode"] = "mixed-intentional"
        self.plan["scenes"][1]["background_token"] = "background.paper.light"
        self.write_plan()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("background_change_reason", result.stdout)

    def test_caption_none_with_background_alpha_fails(self) -> None:
        self.plan["style_lock"]["caption"]["background_alpha"] = 0.5
        self.write_plan()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("background=none requires background_alpha=0", result.stdout)

    def test_page_isolated_rejects_persistent_elements(self) -> None:
        self.plan["scenes"][1]["persistent_elements"] = ["old_card"]
        self.write_plan()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("page-isolated allows 0", result.stdout)

    def test_complexity_budget_is_enforced(self) -> None:
        self.plan["scenes"][0]["complexity"]["content_groups"] = 5
        self.write_plan()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds default limit 4", result.stdout)


if __name__ == "__main__":
    unittest.main()
