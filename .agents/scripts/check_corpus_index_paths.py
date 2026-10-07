#!/usr/bin/env python3
"""Check repository-local paths referenced by corpus index JSON files.

This reads index metadata and Git tree names only; it never opens corpus files
or accesses the network.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

INDEX_PATHS = (
    "Herman Jin/agent-index.json",
    "Serenity/agent-index.json",
)


@dataclass(frozen=True)
class IndexReference:
    index_path: str
    label: str
    target: str | None
    is_directory: bool
    invalid_reason: str | None = None


def _reference(index_path: str, label: str, value: Any, key: str) -> IndexReference | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        return IndexReference(index_path, label, None, False, "expected a non-empty path")
    if value.startswith(("http://", "https://")):
        return None
    if "\\" in value:
        return IndexReference(index_path, label, None, False, "use repository-relative POSIX paths")

    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        return IndexReference(index_path, label, None, False, "path must stay inside the repository")

    root = PurePosixPath(index_path).parent
    target = str(root / relative)
    is_directory = key in {"source", "path"} or value.endswith("/")
    return IndexReference(index_path, label, target, is_directory)


def iter_references(index_path: str, payload: dict[str, Any]) -> Iterable[IndexReference]:
    """Yield local manifest/source references in the supported index shapes."""
    for position, package in enumerate(payload.get("packages", [])):
        if not isinstance(package, dict):
            yield IndexReference(index_path, f"packages[{position}]", None, False, "expected an object")
            continue
        package_label = str(package.get("id") or f"packages[{position}]")
        for key in ("manifest", "readable", "source"):
            ref = _reference(index_path, f"{package_label}.{key}", package.get(key), key)
            if ref is not None:
                yield ref

    data = payload.get("data", {})
    if isinstance(data, dict):
        for section_name, section in data.items():
            if not isinstance(section, dict):
                continue
            for key in ("path", "source_evidence"):
                ref = _reference(index_path, f"data.{section_name}.{key}", section.get(key), key)
                if ref is not None:
                    yield ref


def reference_exists(reference: IndexReference, tracked_paths: set[str]) -> bool:
    if reference.target is None:
        return False
    if reference.is_directory:
        prefix = reference.target.rstrip("/") + "/"
        return any(path.startswith(prefix) for path in tracked_paths)
    return reference.target in tracked_paths


def git_tree_paths(root: Path, ref: str) -> set[str]:
    completed = subprocess.run(
        ["git", "-C", str(root), "ls-tree", "-r", "--name-only", ref],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or f"git ls-tree exited {completed.returncode}"
        raise RuntimeError(detail)
    return {line for line in completed.stdout.splitlines() if line}


def check_indexes(root: Path, ref: str = "HEAD") -> tuple[int, list[str]]:
    tracked_paths = git_tree_paths(root, ref)
    errors: list[str] = []
    checked = 0
    for relative_index in INDEX_PATHS:
        if relative_index not in tracked_paths:
            errors.append(f"{relative_index}: index file is not tracked in {ref!r}")
            continue
        index_file = root / relative_index
        try:
            payload = json.loads(index_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative_index}: cannot read valid JSON ({exc})")
            continue
        if not isinstance(payload, dict):
            errors.append(f"{relative_index}: expected a JSON object")
            continue
        for reference in iter_references(relative_index, payload):
            checked += 1
            if reference.invalid_reason:
                errors.append(
                    f"{reference.index_path}: {reference.label} has invalid path "
                    f"({reference.invalid_reason})"
                )
            elif not reference_exists(reference, tracked_paths):
                kind = "directory" if reference.is_directory else "file"
                errors.append(
                    f"{reference.index_path}: {reference.label} points to missing "
                    f"{kind} {reference.target!r}"
                )
    return checked, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--ref", default="HEAD", help="local Git ref to inspect (default: HEAD)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        checked, errors = check_indexes(root, args.ref)
    except RuntimeError as exc:
        print(f"ERROR: unable to inspect local Git tree: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(
            f"Corpus index path check failed: {len(errors)} issue(s) "
            f"across {checked} references.",
            file=sys.stderr,
        )
        return 1
    print(f"Corpus index path check passed: {checked} local references across {len(INDEX_PATHS)} indexes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
