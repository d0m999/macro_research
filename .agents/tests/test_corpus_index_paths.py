from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPOSITORY_ROOT / ".agents/scripts/check_corpus_index_paths.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
import check_corpus_index_paths as checker


class CorpusIndexPathTests(unittest.TestCase):
    @staticmethod
    def git(root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def test_git_tree_paths_preserve_quoted_characters_and_unicode(self) -> None:
        paths = {
            "source/audio/音频.mp3",
            "source/deck/§3_单股波动率.png",
            'source/a "quoted" name.txt',
            "source/back\\slash.txt",
            "source/tab\tname.txt",
            "source/line\nbreak.txt",
            "source/carriage\rreturn.txt",
        }
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, "init", "--quiet")
            for relative_path in paths:
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("fixture", encoding="utf-8")
            self.git(root, "add", "--", *sorted(paths))
            tree = self.git(root, "write-tree")
            for quote_path in ("true", "false"):
                with self.subTest(core_quote_path=quote_path):
                    self.git(root, "config", "core.quotePath", quote_path)
                    self.assertEqual(checker.git_tree_paths(root, tree), paths)

    def test_sparse_worktree_checks_unicode_only_source_directory(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.git(root, "init", "--quiet")
            self.git(root, "config", "core.quotePath", "true")
            for index_path in checker.INDEX_PATHS:
                path = root / index_path
                path.parent.mkdir(parents=True, exist_ok=True)
                payload = {"packages": []}
                if index_path == "Herman Jin/agent-index.json":
                    payload["packages"].append({"id": "sample", "source": "_source/sample/"})
                path.write_text(json.dumps(payload), encoding="utf-8")
            source = root / "Herman Jin/_source/sample/转录稿.txt"
            source.parent.mkdir(parents=True)
            source.write_text("fixture", encoding="utf-8")
            self.git(root, "add", "--", *checker.INDEX_PATHS, str(source.relative_to(root)))
            tree = self.git(root, "write-tree")

            # A sparse checkout need not materialize any source content.
            source.unlink()
            source.parent.rmdir()
            self.assertEqual(checker.check_indexes(root, tree), (1, []))

            self.git(root, "rm", "--cached", "--", str(source.relative_to(root)))
            missing_source_tree = self.git(root, "write-tree")
            checked, errors = checker.check_indexes(root, missing_source_tree)
            self.assertEqual(checked, 1)
            self.assertEqual(len(errors), 1)
            self.assertIn("missing directory 'Herman Jin/_source/sample'", errors[0])

    def test_hierarchical_index_references_are_relative_to_index(self) -> None:
        payload = {
            "packages": [
                {
                    "id": "sample",
                    "manifest": "x-archive/x-2026-10-02/manifest.json",
                    "readable": None,
                    "source": "x-archive/x-2026-10-02/raw/",
                }
            ]
        }
        references = list(checker.iter_references("Herman Jin/agent-index.json", payload))
        self.assertEqual(
            [(ref.label, ref.target, ref.is_directory) for ref in references],
            [
                ("sample.manifest", "Herman Jin/x-archive/x-2026-10-02/manifest.json", False),
                ("sample.source", "Herman Jin/x-archive/x-2026-10-02/raw", True),
            ],
        )

    def test_flat_index_references_include_directory_and_evidence_file(self) -> None:
        payload = {
            "data": {
                "clean": {
                    "path": "data/clean/",
                    "source_evidence": "data/clean/source-evidence.jsonl",
                }
            }
        }
        references = list(checker.iter_references("Serenity/agent-index.json", payload))
        self.assertEqual(
            [ref.target for ref in references],
            ["Serenity/data/clean", "Serenity/data/clean/source-evidence.jsonl"],
        )
        self.assertTrue(references[0].is_directory)
        self.assertFalse(references[1].is_directory)

    def test_directory_must_match_a_path_prefix(self) -> None:
        directory = checker.IndexReference("index.json", "source", "corpus/raw", True)
        self.assertTrue(checker.reference_exists(directory, {"corpus/raw/item.bin"}))
        self.assertFalse(checker.reference_exists(directory, {"corpus/raw-archive/item.bin"}))

    def test_parent_traversal_is_rejected(self) -> None:
        reference = checker._reference("Herman Jin/agent-index.json", "sample.source", "../outside/", "source")
        self.assertIsNotNone(reference)
        self.assertIsNone(reference.target)
        self.assertIn("inside the repository", reference.invalid_reason or "")

    def test_untracked_index_file_is_reported(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for index_path in checker.INDEX_PATHS:
                path = root / index_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('{"packages": []}', encoding="utf-8")

            with mock.patch.object(
                checker,
                "git_tree_paths",
                return_value={"Serenity/agent-index.json"},
            ):
                checked, errors = checker.check_indexes(root)

        self.assertEqual(checked, 0)
        self.assertEqual(
            errors,
            ["Herman Jin/agent-index.json: index file is not tracked in 'HEAD'"],
        )


if __name__ == "__main__":
    unittest.main()
