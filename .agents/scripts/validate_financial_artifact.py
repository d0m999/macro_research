#!/usr/bin/env python3
"""Validate the structure of fallback-generated XLSX, PPTX, and DOCX files."""

from __future__ import annotations

import json
import posixpath
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree


SUPPORTED = {".xlsx": "xlsx", ".pptx": "pptx", ".docx": "docx"}


def result_template(file_format: str | None) -> dict[str, Any]:
    return {
        "status": "fail",
        "format": file_format,
        "structural_checks": {},
        "formula_evaluation": {
            "status": "not_applicable",
            "formulas_found": 0,
        },
        "visual_review": {
            "status": "not_attempted",
            "method": None,
        },
        "limitations": [],
    }


def parse_xml(archive: zipfile.ZipFile, name: str) -> ElementTree.Element:
    return ElementTree.fromstring(archive.read(name))


def resolve_package_target(base: str, target: str) -> str:
    """Resolve an OOXML relationship target to an archive member name."""
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(base, target))


def safe_package_names(archive: zipfile.ZipFile) -> tuple[bool, list[str]]:
    unsafe: list[str] = []
    for name in archive.namelist():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            unsafe.append(name)
    return not unsafe, unsafe


def validate_common(archive: zipfile.ZipFile, result: dict[str, Any]) -> bool:
    checks = result["structural_checks"]
    names = archive.namelist()
    checks["zip_package"] = "pass"
    safe, unsafe = safe_package_names(archive)
    checks["safe_package_paths"] = "pass" if safe else "fail"
    if unsafe:
        checks["unsafe_paths"] = unsafe
    if len(names) != len(set(names)):
        checks["unique_package_parts"] = "fail"
        return False
    checks["unique_package_parts"] = "pass"
    required = {"[Content_Types].xml", "_rels/.rels"}
    missing = sorted(required.difference(names))
    checks["ooxml_root_parts"] = "pass" if not missing else "fail"
    if missing:
        checks["missing_root_parts"] = missing
        return False
    try:
        parse_xml(archive, "[Content_Types].xml")
        parse_xml(archive, "_rels/.rels")
        checks["root_xml"] = "pass"
    except (ElementTree.ParseError, KeyError) as exc:
        checks["root_xml"] = "fail"
        checks["root_xml_error"] = str(exc)
        return False
    return safe


def validate_xlsx(archive: zipfile.ZipFile, result: dict[str, Any]) -> bool:
    checks = result["structural_checks"]
    names = set(archive.namelist())
    required = {"xl/workbook.xml", "xl/_rels/workbook.xml.rels"}
    missing = sorted(required.difference(names))
    checks["xlsx_required_parts"] = "pass" if not missing else "fail"
    if missing:
        checks["missing_xlsx_parts"] = missing
        return False
    try:
        workbook = parse_xml(archive, "xl/workbook.xml")
        rels = parse_xml(archive, "xl/_rels/workbook.xml.rels")
    except ElementTree.ParseError as exc:
        checks["xlsx_xml"] = "fail"
        checks["xlsx_xml_error"] = str(exc)
        return False

    rel_targets = {
        rel.attrib.get("Id"): rel.attrib.get("Target", "")
        for rel in rels
    }
    ns = {
        "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    }
    missing_sheets: list[str] = []
    sheet_count = 0
    for sheet in workbook.findall("m:sheets/m:sheet", ns):
        sheet_count += 1
        rel_id = sheet.attrib.get(f"{{{ns['r']}}}id")
        target = rel_targets.get(rel_id, "")
        normalized = resolve_package_target("xl", target)
        if normalized not in names:
            missing_sheets.append(sheet.attrib.get("name", rel_id or "unknown"))
    checks["worksheet_relationships"] = "pass" if sheet_count and not missing_sheets else "fail"
    checks["worksheet_count"] = sheet_count
    if missing_sheets:
        checks["missing_worksheets"] = missing_sheets

    formula_count = 0
    formula_xml_errors: list[str] = []
    formula_text_errors: list[str] = []
    excel_error_tokens = {"#VALUE!", "#DIV/0!", "#REF!", "#NAME?", "#NULL!", "#NUM!", "#N/A"}
    for name in sorted(n for n in names if n.startswith("xl/worksheets/") and n.endswith(".xml")):
        try:
            root = parse_xml(archive, name)
            for node in root.iter():
                if node.tag.endswith("}f"):
                    formula_count += 1
                    formula_text = node.text or ""
                    if any(token in formula_text for token in excel_error_tokens):
                        formula_text_errors.append(f"{name}: {formula_text}")
                if node.tag.endswith("}c") and node.attrib.get("t") == "e":
                    cached_error = next(
                        (child.text for child in node if child.tag.endswith("}v")),
                        None,
                    )
                    if cached_error:
                        formula_text_errors.append(
                            f"{name}!{node.attrib.get('r', '?')}: cached {cached_error}"
                        )
        except ElementTree.ParseError:
            formula_xml_errors.append(name)
    checks["worksheet_xml"] = "pass" if not formula_xml_errors else "fail"
    if formula_xml_errors:
        checks["invalid_worksheet_xml"] = formula_xml_errors
    checks["formula_text"] = "pass" if not formula_text_errors else "fail"
    if formula_text_errors:
        checks["formula_text_errors"] = formula_text_errors
    result["formula_evaluation"] = {
        "status": "unverified",
        "formulas_found": formula_count,
        "marker": "FORMULA_EVALUATION_UNVERIFIED",
        "detail": "Formula text was inspected but no spreadsheet calculation engine was run.",
    }
    result["limitations"].append("FORMULA_EVALUATION_UNVERIFIED")
    return bool(sheet_count) and not missing_sheets and not formula_xml_errors and not formula_text_errors


def validate_pptx(archive: zipfile.ZipFile, result: dict[str, Any]) -> bool:
    checks = result["structural_checks"]
    names = set(archive.namelist())
    required = {"ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"}
    missing = sorted(required.difference(names))
    checks["pptx_required_parts"] = "pass" if not missing else "fail"
    if missing:
        checks["missing_pptx_parts"] = missing
        return False
    try:
        presentation = parse_xml(archive, "ppt/presentation.xml")
        rels = parse_xml(archive, "ppt/_rels/presentation.xml.rels")
    except ElementTree.ParseError as exc:
        checks["pptx_xml"] = "fail"
        checks["pptx_xml_error"] = str(exc)
        return False

    rel_targets = {
        rel.attrib.get("Id"): rel.attrib.get("Target", "")
        for rel in rels
    }
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    slide_nodes = [node for node in presentation.iter() if node.tag.endswith("}sldId")]
    missing_slides: list[str] = []
    for slide in slide_nodes:
        rel_id = slide.attrib.get(f"{{{rel_ns}}}id")
        target = rel_targets.get(rel_id, "")
        part = resolve_package_target("ppt", target)
        if part not in names:
            missing_slides.append(rel_id or "unknown")
    checks["slide_relationships"] = "pass" if slide_nodes and not missing_slides else "fail"
    checks["slide_count"] = len(slide_nodes)
    if missing_slides:
        checks["missing_slides"] = missing_slides
    return bool(slide_nodes) and not missing_slides


def validate_docx(archive: zipfile.ZipFile, result: dict[str, Any]) -> bool:
    checks = result["structural_checks"]
    names = set(archive.namelist())
    required = {"word/document.xml"}
    missing = sorted(required.difference(names))
    checks["docx_required_parts"] = "pass" if not missing else "fail"
    if missing:
        checks["missing_docx_parts"] = missing
        return False
    try:
        document = parse_xml(archive, "word/document.xml")
    except ElementTree.ParseError as exc:
        checks["docx_xml"] = "fail"
        checks["docx_xml_error"] = str(exc)
        return False
    has_body = any(node.tag.endswith("}body") for node in document.iter())
    checks["document_body"] = "pass" if has_body else "fail"
    return has_body


def try_quick_look(path: Path, result: dict[str, Any]) -> None:
    qlmanage = shutil.which("qlmanage")
    if not qlmanage:
        result["visual_review"] = {
            "status": "unverified",
            "method": None,
            "marker": "FULL_RENDER_UNVERIFIED",
            "detail": "Quick Look is unavailable; no rendered preview was generated.",
        }
        return
    with tempfile.TemporaryDirectory(prefix="financial-artifact-preview-") as directory:
        completed = subprocess.run(
            [qlmanage, "-t", "-s", "1400", "-o", directory, str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
        )
        previews = [item.name for item in Path(directory).iterdir()]
    result["visual_review"] = {
        "status": "thumbnail_generated" if completed.returncode == 0 and previews else "unverified",
        "method": "Quick Look thumbnail",
        "marker": "FULL_RENDER_UNVERIFIED",
        "detail": "A thumbnail is not a complete page-by-page render review.",
    }


def validate(path: Path) -> tuple[dict[str, Any], int]:
    file_format = SUPPORTED.get(path.suffix.lower())
    result = result_template(file_format)
    if file_format is None:
        result["limitations"].append("Unsupported extension; expected .xlsx, .pptx, or .docx")
        return result, 2
    if not path.is_file():
        result["limitations"].append(f"File not found: {path}")
        return result, 2

    try:
        with zipfile.ZipFile(path) as archive:
            ok = validate_common(archive, result)
            if ok:
                ok = {
                    "xlsx": validate_xlsx,
                    "pptx": validate_pptx,
                    "docx": validate_docx,
                }[file_format](archive, result)
    except (OSError, zipfile.BadZipFile) as exc:
        result["structural_checks"]["zip_package"] = "fail"
        result["structural_checks"]["error"] = str(exc)
        return result, 1

    if not ok:
        result["status"] = "fail"
        return result, 1

    if file_format in {"pptx", "docx"}:
        try_quick_look(path, result)
        result["limitations"].append("FULL_RENDER_UNVERIFIED")
    else:
        result["visual_review"] = {
            "status": "not_applicable",
            "method": None,
            "detail": "Workbook visual layout was not rendered by this structural validator.",
        }
    result["status"] = "pass_with_limitations" if result["limitations"] else "pass"
    return result, 0


def main() -> int:
    if len(sys.argv) != 2:
        result = result_template(None)
        result["limitations"].append(
            "Usage: python3 .agents/scripts/validate_financial_artifact.py <file>"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2
    result, exit_code = validate(Path(sys.argv[1]))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
