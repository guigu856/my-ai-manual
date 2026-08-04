from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_sample_plan import build_plan  # noqa: E402
from validate_review_report import validate  # noqa: E402


class ReviewContractTests(unittest.TestCase):
    def test_standard_sampling_is_deterministic_and_includes_boundary_offsets(self) -> None:
        first = build_plan(5.0, "standard", [2.0])
        second = build_plan(5.0, "standard", [2.0])
        self.assertEqual(first, second)
        self.assertIn(1.75, first["timestamps_s"])
        self.assertIn(2.0, first["timestamps_s"])
        self.assertIn(2.25, first["timestamps_s"])

    def test_valid_report_passes(self) -> None:
        payload = json.loads((ROOT / "examples" / "review-report.valid.json").read_text(encoding="utf-8"))
        result = validate(payload)
        self.assertTrue(result["ok"], result)

    def test_failed_finding_requires_evidence(self) -> None:
        payload = json.loads((ROOT / "examples" / "review-report.valid.json").read_text(encoding="utf-8"))
        payload["findings"][0]["status"] = "fail"
        payload["findings"][0]["evidence"] = []
        result = validate(payload)
        self.assertFalse(result["ok"])
        self.assertTrue(any("needs evidence" in error for error in result["errors"]))

    def test_timestamp_must_stay_inside_media(self) -> None:
        payload = json.loads((ROOT / "examples" / "review-report.valid.json").read_text(encoding="utf-8"))
        payload["findings"][0]["end_s"] = 20.0
        result = validate(payload)
        self.assertFalse(result["ok"])
        self.assertTrue(any("timestamps fall outside" in error for error in result["errors"]))

    def test_malformed_shape_returns_errors_without_crashing(self) -> None:
        payload = json.loads((ROOT / "examples" / "review-report.valid.json").read_text(encoding="utf-8"))
        payload["overall"] = []
        payload["findings"][0]["id"] = []
        result = validate(payload)
        self.assertFalse(result["ok"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
