from __future__ import annotations

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
