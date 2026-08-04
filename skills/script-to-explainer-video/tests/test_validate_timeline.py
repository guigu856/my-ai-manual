import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_timeline.py"
SPEC = importlib.util.spec_from_file_location("validate_timeline", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ValidateTimelineTests(unittest.TestCase):
    def write_project(self, timeline, segments):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        (root / "timeline.json").write_text(json.dumps(timeline), encoding="utf-8")
        (root / "segments.json").write_text(json.dumps(segments), encoding="utf-8")
        self.addCleanup(directory.cleanup)
        return root

    def test_valid_project_passes(self):
        root = self.write_project(
            {
                "version": 1,
                "fps": 30,
                "duration_frames": 120,
                "segments": [
                    {
                        "id": "seg-01",
                        "start_frame": 0,
                        "end_frame": 120,
                        "cues": [{"id": "cue-01", "start_frame": 0, "end_frame": 90, "text": "原文"}],
                    }
                ],
            },
            {"version": 1, "segments": [{"id": "seg-01", "title": "标题", "text": "原文"}]},
        )
        result = MODULE.validate(root, "timeline.json", "segments.json")
        self.assertTrue(result["ok"], result)

    def test_overlapping_cues_fail(self):
        root = self.write_project(
            {
                "version": 1,
                "fps": 30,
                "duration_frames": 120,
                "segments": [
                    {
                        "id": "seg-01",
                        "start_frame": 0,
                        "end_frame": 120,
                        "cues": [
                            {"id": "cue-01", "start_frame": 0, "end_frame": 90, "text": "一"},
                            {"id": "cue-02", "start_frame": 80, "end_frame": 100, "text": "二"},
                        ],
                    }
                ],
            },
            {"version": 1, "segments": [{"id": "seg-01", "title": "标题", "text": "原文"}]},
        )
        result = MODULE.validate(root, "timeline.json", "segments.json")
        self.assertFalse(result["ok"])
        self.assertTrue(any("overlaps" in failure for failure in result["failures"]))


if __name__ == "__main__":
    unittest.main()