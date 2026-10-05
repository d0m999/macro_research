from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, REPOSITORY_ROOT / relative_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


artifact_validator = load_module(
    "validate_financial_artifact",
    ".agents/scripts/validate_financial_artifact.py",
)


try:
    import openpyxl
except ImportError:
    openpyxl = None


class FormulaLiteralTests(unittest.TestCase):
    def test_error_markers_inside_string_literals_are_ignored(self) -> None:
        formulas = (
            '=COUNTIF(A1:A3,"#REF!")',
            '=IFERROR(A1,"#N/A")',
            '="escaped ""#VALUE!"" text"',
        )
        for formula in formulas:
            with self.subTest(formula=formula):
                self.assertFalse(artifact_validator.formula_has_unquoted_excel_error(formula))

    def test_error_markers_outside_string_literals_are_rejected(self) -> None:
        formulas = (
            "=#REF!",
            '=IFERROR(#N/A,"fallback")',
            '=IF(A1="#REF!",#VALUE!,0)',
            '=IF(A1,"unterminated #REF!)',
        )
        for formula in formulas:
            with self.subTest(formula=formula):
                self.assertTrue(artifact_validator.formula_has_unquoted_excel_error(formula))


@unittest.skipUnless(openpyxl, "openpyxl is required for workbook validation tests")
class WorkbookValidationTests(unittest.TestCase):
    def test_artifact_validator_accepts_quoted_error_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "quoted-errors.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet["A1"] = '=COUNTIF(B1:B3,"#REF!")'
            sheet["A2"] = '=IFERROR(B2,"#N/A")'
            workbook.save(path)

            result, exit_code = artifact_validator.validate(path)

        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "pass_with_limitations")
        self.assertEqual(result["structural_checks"]["formula_text"], "pass")

class QuickLookValidationTests(unittest.TestCase):
    def test_timeout_returns_pass_with_full_render_limitation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "document.docx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "[Content_Types].xml",
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>',
                )
                archive.writestr(
                    "_rels/.rels",
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>',
                )
                archive.writestr(
                    "word/document.xml",
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    "<w:body><w:p/></w:body></w:document>",
                )

            with mock.patch.object(
                artifact_validator.shutil,
                "which",
                return_value="/usr/bin/qlmanage",
            ), mock.patch.object(
                artifact_validator.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired("qlmanage", 30),
            ):
                result, exit_code = artifact_validator.validate(path)

        self.assertEqual(exit_code, 0)
        self.assertEqual(result["status"], "pass_with_limitations")
        self.assertEqual(result["visual_review"]["status"], "unverified")
        self.assertEqual(result["visual_review"]["marker"], "FULL_RENDER_UNVERIFIED")
        self.assertIn("FULL_RENDER_UNVERIFIED", result["limitations"])


if __name__ == "__main__":
    unittest.main()
