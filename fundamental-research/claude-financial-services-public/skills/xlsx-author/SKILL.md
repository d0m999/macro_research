---
name: xlsx-author
description: Produce a .xlsx file on disk in a headless Codex session instead of driving a live Excel workbook.
---

# xlsx-author

Use this skill in Codex when you need to deliver an Excel workbook as a local file. It writes a standalone workbook and does not require a live Office integration.

## Input boundary

Use only user-provided or locally generated inputs. This skill does not retrieve financial or market data; every number must come from a supplied source or an explicitly labeled calculation.

## Output contract

- Write to `./out/<name>.xlsx`. Create `./out/` if it does not exist.
- Return the relative path in your final message so the orchestration layer can collect it.

## How to build the workbook

Write a short Python script and run it with Bash. Use `openpyxl`:

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
ws = wb.active; ws.title = "Inputs"
ws["B2"] = "Revenue"; ws["C2"] = 1_250_000_000
ws["C2"].font = Font(color="0000FF")           # blue = hardcoded input
calc = wb.create_sheet("DCF")
calc["C5"] = "=Inputs!C2*(1+Inputs!C3)"        # black = formula
wb.save("./out/model.xlsx")
```

## Conventions (mirror `audit-xls`)

- **Blue / black / green.** Blue = hardcoded input, black = formula, green = link to another sheet/file.
- **No hardcodes in calc cells.** Every calculation cell is a formula; every input lives on an Inputs tab.
- **Named ranges** for any value referenced from a deck or memo.
- **Balance checks.** Include a Checks tab that ties (BS balances, CF ties to cash, etc.) and surfaces TRUE/FALSE.
- **One model per file.** Do not append to an existing workbook unless explicitly asked.

## Scope

This skill is limited to local file generation. If the user needs to edit a live Office workbook, request the workbook through the available host integration separately.
