from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
ANALYZE = SKILL / "scripts" / "analyze_media.py"
REFINE = SKILL / "scripts" / "refine_intervals.py"


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "requires FFmpeg")
class AnalyzeMediaTests(unittest.TestCase):
    def make_video(self, path: Path) -> None:
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=size=320x180:rate=10:duration=2",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:sample_rate=16000:duration=2",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                str(path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_analysis_creates_probe_frames_contact_sheet_and_audio_evidence(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            root = Path(temp_dir)
            media = root / "sample.mp4"
            self.make_video(media)
            output = root / "analysis"

            result = subprocess.run(
                [
                    sys.executable,
                    str(ANALYZE),
                    str(media),
                    "--output-dir",
                    str(output),
                    "--overview-interval",
                    "0.5",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            manifest = Path(payload["analysis_manifest"])
            self.assertTrue(manifest.is_file())
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertGreaterEqual(data["probe"]["duration_seconds"], 1.9)
            self.assertGreaterEqual(len(data["overview_frames"]), 3)
            self.assertTrue(all(Path(item["path"]).is_file() for item in data["overview_frames"]))
            self.assertTrue(data["contact_sheets"])
            self.assertTrue(all(Path(item["path"]).is_file() for item in data["contact_sheets"]))
            self.assertTrue(Path(data["audio"]["waveform_path"]).is_file())
            self.assertIn("tempo_candidate", data["audio"])

    def test_refinement_rejects_step_above_point_one_seconds(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            root = Path(temp_dir)
            media = root / "sample.mp4"
            self.make_video(media)
            result = subprocess.run(
                [
                    sys.executable,
                    str(REFINE),
                    str(media),
                    "--output-dir",
                    str(root / "refined"),
                    "--interval",
                    "0.2:0.8",
                    "--step",
                    "0.2",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["error"]["code"], "step_too_large")


if __name__ == "__main__":
    unittest.main()
