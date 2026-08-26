---
name: pptx-author
description: Produce a .pptx file on disk in a headless Codex session instead of driving a live PowerPoint document.
---

# pptx-author

Use this skill in Codex when you need to deliver a PowerPoint deck as a file artifact. It writes a local file and does not require a live Office integration.

## Input boundary

Use only user-provided or locally generated inputs. This skill does not retrieve financial or market data; every number must come from a supplied source or an explicitly labeled calculation.

## Output contract

- Write to `./out/<name>.pptx`. Create `./out/` if it does not exist.
- Return the relative path in your final message so the orchestration layer can collect it.

## How to build the deck

Write a short Python script and run it with Bash. Use `python-pptx`:

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation("./templates/firm-template.pptx")  # if a template is provided
# or: prs = Presentation()

slide = prs.slides.add_slide(prs.slide_layouts[5])    # title-only
slide.shapes.title.text = "Valuation Summary"
# ... add tables / charts / text boxes ...

prs.save("./out/pitch-<target>.pptx")
```

## Conventions (mirror the live-Office `pitch-deck` skill)

- **One idea per slide.** Title states the takeaway; body supports it.
- **Every number traces to the model.** If a figure comes from `./out/model.xlsx`, footnote the sheet and cell.
- **Use the firm template** when one is mounted at `./templates/`; otherwise default layouts.
- **Charts**: prefer embedding a PNG rendered from the model over native pptx charts when fidelity matters.
- **No external sends.** This skill writes a file; it never emails or uploads.

## Scope

This skill is limited to local file generation. If the user needs to edit a live Office document, request the document through the available host integration separately.
