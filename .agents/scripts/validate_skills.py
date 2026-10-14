#!/usr/bin/env python3
"""Validate the structure and convergence invariants of .agents/skills/.

Locks in the checks that SOURCE-AUDIT.md lists as structural validation:
frontmatter, per-skill invocation policy, resolvable relative links,
single-source ownership of the routing sentence, banned remote-connector
patterns, and trailing whitespace.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


SKILLS_ROOT = Path(__file__).resolve().parents[1] / "skills"

# 调用分层（fundamental-research/claude-financial-services-public/SOURCE-AUDIT.md
# 合并对账 2026-10-09）：只允许显式调用的 skill 为 False，其余 True。
EXPECTED_IMPLICIT_INVOCATION = {
    "audit-xls": False,
    "catalyst-calendar": True,
    "datapack-builder": False,
    "earnings-analysis": True,
    "financial-model": True,
    "idea-generation": True,
    "initiating-coverage": True,
    "sector-overview": True,
    "thesis-tracker": True,
}

# 单一事实来源句归 .agents/PUBLIC-SOURCE-POLICY.md 与 data-sources.jsonl
# 所有；skill 文本只保留指针，不得复述该句。
ROUTING_SENTENCE = "数据源路由的单一事实来源"

# 交付物总量配额：禁止 skill 规定固定页/图/条/词数（会诱发为凑数注水）。
# 锚定「数字范围 + 紧随的量词名词」，不匹配裸数字，故不误伤导航标签
# （PAGES 8-10，量词在前）和示例数据（$9.8-10.0B，单位是 B 不在白名单）。
QUOTA_PATTERN = re.compile(
    r"\b\d+(?:\.\d+)?\s*[-\u2013]\s*\d+(?:\.\d+)?\s+"
    r"(?:pages?|slides?|charts?|bullets?|words?|figures?|tables?|graphs?)\b",
    re.IGNORECASE,
)

BANNED_PATTERNS = ("mcp__", ".mcp.json")

MARKDOWN_LINK = re.compile(r"\]\(([^)\s]+)")

SKILL_MARKDOWN_FILES = ("SKILL.md",)


def discover_skills(skills_root: Path) -> list[Path]:
    return sorted(
        path for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def parse_frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"')
    return fields


def parse_openai_policy(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s+(display_name|short_description|allow_implicit_invocation):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"')
    return fields


def markdown_link_targets(text: str) -> list[str]:
    targets = []
    for match in MARKDOWN_LINK.finditer(text):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        targets.append(target)
    return targets


def check_skills(skills_root: Path = SKILLS_ROOT) -> dict[str, Any]:
    failures: list[str] = []
    skill_dirs = discover_skills(skills_root)
    skill_names = [path.name for path in skill_dirs]

    if not skill_dirs:
        failures.append(f"no skills found under {skills_root}")

    unexpected = sorted(set(skill_names) - set(EXPECTED_IMPLICIT_INVOCATION))
    missing = sorted(set(EXPECTED_IMPLICIT_INVOCATION) - set(skill_names))
    for name in unexpected:
        failures.append(f"skill '{name}' missing from EXPECTED_IMPLICIT_INVOCATION; update the policy map")
    for name in missing:
        failures.append(f"skill '{name}' in EXPECTED_IMPLICIT_INVOCATION has no directory on disk")

    checked_files = 0
    for skill_dir in skill_dirs:
        name = skill_dir.name
        skill_file = skill_dir / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")

        frontmatter = parse_frontmatter(text)
        if not frontmatter:
            failures.append(f"{name}: SKILL.md missing frontmatter block")
        else:
            if frontmatter.get("name") != name:
                failures.append(f"{name}: frontmatter name '{frontmatter.get('name')}' != directory name")
            if not frontmatter.get("description"):
                failures.append(f"{name}: frontmatter description is empty")

        policy_file = skill_dir / "agents" / "openai.yaml"
        if not policy_file.is_file():
            failures.append(f"{name}: agents/openai.yaml missing")
        else:
            policy = parse_openai_policy(policy_file.read_text(encoding="utf-8"))
            if not policy.get("display_name") or not policy.get("short_description"):
                failures.append(f"{name}: openai.yaml missing display_name/short_description")
            expected = EXPECTED_IMPLICIT_INVOCATION.get(name)
            actual = policy.get("allow_implicit_invocation")
            if actual not in ("true", "false"):
                failures.append(f"{name}: openai.yaml allow_implicit_invocation unparsable: {actual!r}")
            elif expected is not None and (actual == "true") != expected:
                failures.append(
                    f"{name}: allow_implicit_invocation={actual}, expected {str(expected).lower()}"
                )

        if "CODEX-EXECUTION-POLICY.md" not in text:
            failures.append(f"{name}: SKILL.md does not reference CODEX-EXECUTION-POLICY.md")
        if name != "audit-xls" and "PUBLIC-SOURCE-POLICY.md" not in text:
            failures.append(f"{name}: SKILL.md does not reference PUBLIC-SOURCE-POLICY.md")

        md_files = [skill_file, *sorted((skill_dir / "references").glob("*.md"))]
        for md_file in md_files:
            md_text = md_file.read_text(encoding="utf-8")
            checked_files += 1
            rel = md_file.relative_to(skills_root)
            for pattern in BANNED_PATTERNS:
                if pattern in md_text:
                    failures.append(f"{rel}: banned pattern {pattern!r}")
            if ROUTING_SENTENCE in md_text:
                failures.append(f"{rel}: restates the routing sentence owned by PUBLIC-SOURCE-POLICY.md")
            quota_match = QUOTA_PATTERN.search(md_text)
            if quota_match:
                failures.append(
                    f"{rel}: hard deliverable quota {quota_match.group(0)!r}; use soft wording (e.g. 'as warranted')"
                )
            for line_number, line in enumerate(md_text.splitlines(), start=1):
                if line != line.rstrip():
                    failures.append(f"{rel}:{line_number}: trailing whitespace")
            for target in markdown_link_targets(md_text):
                if not (md_file.parent / target).resolve().is_file():
                    failures.append(f"{rel}: broken relative link {target!r}")

    return {
        "status": "pass" if not failures else "fail",
        "skills_root": str(skills_root),
        "skills": skill_names,
        "checked_files": checked_files,
        "failure_count": len(failures),
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    skills_root = Path(args[0]) if args else SKILLS_ROOT
    result = check_skills(skills_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
