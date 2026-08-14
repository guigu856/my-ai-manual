from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "resolve_source.py"


class ResolveSourceTests(unittest.TestCase):
    def test_local_source_is_copied_and_hashed(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            root = Path(temp_dir)
            source = root / "输入 视频.mp4"
            source.write_bytes(b"synthetic-video")
            output = root / "run"

            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(source), "--output-dir", str(output)],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])
            media = payload["source_media"]
            self.assertEqual(media["source_kind"], "local_file")
            self.assertEqual(media["original_input"], str(source))
            self.assertEqual(len(media["sha256"]), 64)
            self.assertEqual(Path(media["local_path"]).read_bytes(), b"synthetic-video")
            self.assertTrue((output / "source.json").is_file())

    def test_missing_local_source_has_specific_error(self) -> None:
        with tempfile.TemporaryDirectory(dir="D:\\") as temp_dir:
            output = Path(temp_dir) / "run"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "D:\\missing\\not-here.mp4",
                    "--output-dir",
                    str(output),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["error"]["code"], "local_source_missing")


if __name__ == "__main__":
    unittest.main()
