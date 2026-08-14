from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]


class ReferenceGuidedJianyingSkillTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        required = (
            "SKILL.md",
            "DESIGN.md",
            "agents/openai.yaml",
            "evals/evals.json",
            "references/report-reading.md",
            "references/creative-planning.md",
            "references/material-preparation.md",
            "references/shot-table.md",
            "references/jianying-operation.md",
            "references/preview-check.md",
            "templates/creative-plan.md",
            "templates/shot-table.md",
        )

        for relative_path in required:
            self.assertTrue((SKILL_ROOT / relative_path).is_file(), relative_path)

    def test_main_skill_keeps_the_confirmed_boundary(self) -> None:
        content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        for phrase in (
            "报告不要求固定标题、章节数量、时间线或证据编号",
            "不要调用 `video-reference-breakdown`",
            "主动搜索候选素材",
            "computer-use:computer-use",
            "不点击最终导出",
            "创作方案确认",
            "素材与 BGM 确认",
            "逐镜剪辑表确认",
        ):
            self.assertIn(phrase, content)

        self.assertLess(len(content.splitlines()), 500)

    def test_shot_table_contains_only_execution_fields(self) -> None:
        template = (SKILL_ROOT / "templates/shot-table.md").read_text(encoding="utf-8")

        self.assertIn("| 时间 | 使用素材 | 画面处理 | 附加效果 | 文字 | 声音与节拍 | 衔接方式 |", template)
        self.assertNotIn("证据编号", template)
        self.assertNotIn("来自哪一章", template)

    def test_evals_cover_triggers_and_near_misses(self) -> None:
        payload = json.loads((SKILL_ROOT / "evals/evals.json").read_text(encoding="utf-8"))
        evals = payload["evals"]

        self.assertEqual(payload["skill_name"], "reference-guided-jianying-creation")
        self.assertEqual(len(evals), 6)
        self.assertEqual(len({item["id"] for item in evals}), 6)
        prompts = "\n".join(item["prompt"] for item in evals)
        self.assertIn("素材你来找", prompts)
        self.assertIn("还没想好拍什么", prompts)
        self.assertIn("拆解报告", prompts)
        self.assertIn("导出到桌面", prompts)

    def test_readme_registers_the_skill(self) -> None:
        readme_path = REPO_ROOT / "README.md"
        if not readme_path.is_file():
            self.skipTest("standalone Skill installation has no repository README")
        readme = readme_path.read_text(encoding="utf-8")

        self.assertIn("skills/reference-guided-jianying-creation/", readme)


if __name__ == "__main__":
    unittest.main()
