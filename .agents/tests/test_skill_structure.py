from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_SCRIPT = REPOSITORY_ROOT / ".agents" / "scripts" / "validate_skills.py"


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPOSITORY_ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


skill_validator = load_module(
    "validate_skills",
    ".agents/scripts/validate_skills.py",
)


def write_minimal_skill(root: Path, name: str) -> Path:
    skill_dir = root / name
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: \"test skill\"\n---\n\n# {name}\n",
        encoding="utf-8",
    )
    (skill_dir / "agents" / "openai.yaml").write_text(
        "interface:\n"
        f'  display_name: "{name}"\n'
        '  short_description: "test"\n'
        "policy:\n"
        "  allow_implicit_invocation: true\n",
        encoding="utf-8",
    )
    return skill_dir


class SkillStructureTests(unittest.TestCase):
    def test_repository_skills_pass_all_checks(self) -> None:
        result = skill_validator.check_skills(REPOSITORY_ROOT / ".agents" / "skills")
        self.assertEqual(result["failure_count"], 0, "\n".join(result["failures"]))

    def test_missing_frontmatter_and_policy_file_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "bad-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")

            result = skill_validator.check_skills(root)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("frontmatter" in failure for failure in result["failures"]))
        self.assertTrue(any("openai.yaml missing" in failure for failure in result["failures"]))

    def test_routing_sentence_restatement_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_minimal_skill(root, "clean-skill")
            skill_file = root / "clean-skill" / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8") + "数据源路由的单一事实来源\n",
                encoding="utf-8",
            )

            result = skill_validator.check_skills(root)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(
            any("routing sentence" in failure for failure in result["failures"]),
            result["failures"],
        )

    def test_hard_content_quota_is_rejected_but_navigation_labels_pass(self) -> None:
        pattern = skill_validator.QUOTA_PATTERN

        for hard in ("Embed 2-3 charts", "3-4 bullets", "1-2 pages", "150-200 words"):
            with self.subTest(hard=hard):
                self.assertRegex(hard, pattern)

        for benign in (
            "## PAGES 8-10: VALUATION & ESTIMATES",
            "## PAGE 1: EARNINGS SUMMARY",
            "guidance to $9.8-10.0B from prior $9.5-9.7B",
            "Revenue of $2.45B exceeded ... by $60M (2.5%)",
            "Embed charts as warranted",
            "P/E or EV/EBITDA bands",
        ):
            with self.subTest(benign=benign):
                self.assertNotRegex(benign, pattern)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_minimal_skill(root, "clean-skill")
            skill_file = root / "clean-skill" / "SKILL.md"
            skill_file.write_text(
                skill_file.read_text(encoding="utf-8") + "\n**Embed 2-3 charts:**\n",
                encoding="utf-8",
            )

            result = skill_validator.check_skills(root)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(
            any("hard deliverable quota" in failure for failure in result["failures"]),
            result["failures"],
        )

    def test_cli_passes_on_repository_and_fails_on_broken_root(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["status"], "pass")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill_dir = root / "bad-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")

            broken = subprocess.run(
                [sys.executable, str(VALIDATOR_SCRIPT), str(root)],
                capture_output=True,
                text=True,
            )

        self.assertEqual(broken.returncode, 1, broken.stdout + broken.stderr)
        self.assertEqual(json.loads(broken.stdout)["status"], "fail")


if __name__ == "__main__":
    unittest.main()
