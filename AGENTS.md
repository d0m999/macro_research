# Repository Guidelines

## Project Structure & Module Organization

This repository holds **two active work streams plus one dormant research line**. Read `CLAUDE.md` first — it defines which stream a task belongs to and carries the hard constraints. Do not assume a task is Pine-related just because `PineScript/` exists.

1. **Active, primary — KOL corpus archiving and view distillation.** `Herman Jin/` (1.6 GB, @ShanghaoJin) and `Serenity/` (@aleabitoreddit — a *different* person, do not conflate) hold scraped X posts/replies and YouTube transcripts. Deliverable is reasoning chains and a verified view list, **not** persona replication. Output lives in `research/Herman-Jin 观点 rollup.md` (untracked in git — see `CLAUDE.md` for the edit protocol) and `research/_agent/`.
2. **Active, secondary — US equity / AI supply-chain fundamental research.** Hyperscaler CAPEX, CoWoS/HBM supply-demand gaps, single-name quick takes in `research/_agent/`; public-source channel validation in `GLW/`; 15 financial analysis skills under `.agents/skills/`.
3. **Dormant — TradingView/Pine Script research.** `PineScript/` contains standalone indicators grouped into `_L∞p/` core studies, `Open Interest/`, `Oscillator/`, `Price_Zones/`, and `Vol/`. `strategy-notes/` holds strategy assumptions and checklists; `strategy-notes/design/` contains self-contained HTML visualization mockups. No new commits since 2026-09.

`docs/` contains methodology and process notes.

## Build, Test, and Development Commands

There is no build system or runtime dependency manifest. Run the checks with Python 3.10+; `requirements-test.txt` lists the optional unit-test dependency. Useful checks:

```bash
git status --short --branch
rg --files PineScript strategy-notes docs
rg -n '^//@version=|request\.security|lookahead|barstate\.isconfirmed' PineScript
git diff --check
```

There are two offline unittest groups: `.agents/tests/` has 4 financial-artifact tests and 7 corpus-index checker tests; `tools/validation/tests/` has 17 OI validator tests. The OI tests use mocked HTTP responses and temporary files; they do not contact an exchange. `pytest` is not used.

```bash
python3 -m pip install -r requirements-test.txt  # openpyxl for the workbook test
python3 .agents/scripts/check_corpus_index_paths.py
python3 -m unittest discover -s .agents/tests -p 'test_*.py' -v
python3 -m unittest discover -s tools/validation/tests -p 'test_*.py' -v
python3 .agents/scripts/validate_financial_artifact.py <artifact.xlsx|.pptx|.docx>
```

The financial-artifact validator itself uses only the Python standard library. `openpyxl` is needed only by the workbook fixture test; Quick Look is optional and is not required by the unit suites. The index checker reads index JSON plus local Git tree paths, not corpus file contents. Do not run the live collectors as part of offline validation.

Known follow-up, intentionally not changed here: `run_collect()` in `tools/validation/validate_binance_coinm_oi.py` prints `ready_for_compare` after reaching the requested coverage, but still returns `EXIT_INCONCLUSIVE`. Define and test its CLI exit-code contract separately; this maintenance does not change collector behavior.

For Pine changes, paste the modified file into the TradingView Pine Editor, compile it, and inspect representative symbols and timeframes. Check data availability, closed-bar behavior, multi-timeframe requests, and alerts when relevant.

## Coding Style & Naming Conventions

**Pine:** prefer Pine Script v6 for new work; preserve v5 scripts unless migration is part of the change. Match the surrounding file’s indentation to avoid noisy diffs; use four spaces for new blocks where practical. Keep variables and inputs descriptive (`camelCase` is common), use clear helper names such as `f_*`, and keep user-facing labels/tooltips explicit. Use descriptive filenames within the existing category directories; do not rename files casually.

**Research artifacts:** name corpus deliverables `*-YYYY-MM-DD.md` (or `-YYYY-MM-DD.json`) under `research/_agent/`, and keep the date in the filename rather than relying on mtime. Every chart ships a companion `*-notes-YYYY-MM-DD.md` with the data table, caveats, and the reproduction command; put the numeric constants in a block at the top of the chart script rather than hardcoding them in the drawing logic. Back up the corpus copy before editing and record the baseline MD5.

## Testing Guidelines

**Pine (dormant line):** treat TradingView compilation plus chart-level visual review as the acceptance test. For signal changes, verify confirmed-bar and repaint/lookahead behavior and document the data source, especially for OI. Do not treat a design mockup as proof that the Pine implementation exists.

**Corpus distillation (primary line):** every claim needs a re-anchored citation (transcript line number, slide OCR, or dated social post) before it goes into a deliverable. Search **both** traditional and simplified character forms — a single-form keyword search misses roughly half the corpus. Mark the polarity of every ticker mentioned: corpus hit ≠ endorsement. See `CLAUDE.md` for the full rule set.

**Financial artifacts:** run the validator in `.agents/tests/` and report `SOURCE_UNAVAILABLE` honestly rather than filling gaps with plausible numbers.

## Commit & Pull Request Guidelines

Use concise imperative subjects with the repository’s established prefixes: `feat:`, `fix:`, `docs:`, `chore:`, or `refactor:`; an optional scope is fine. PRs should describe changed scripts, symbols/timeframes checked, compile or chart evidence, and screenshots for visual changes. Preserve unrelated work and untracked artifacts; stage named files rather than using `git add -A`.

## Security & Scope

Never commit `.env`, credentials, logs, or generated data.

**Git state (checked 2026-10-07).** The 239-change count recorded on 2026-10-05 described a local pre-sync working-tree snapshot, not the current branch. The latest `main` commit at this check was `7c8b1ba`; inspect `git status --short --branch` before every task. The repository already tracks a large `Herman Jin/` corpus; never stage that directory wholesale. Keep any local `.env` out of commits and do not print its contents. Do not reintroduce the removed Python/FreqTrade execution layer, Docker deployment, or trading database without explicit authorization. Keep TradingView price data, exchange OI feeds, and native exchange OI claims clearly distinguished in code comments and research notes.

**Corpus scope.** `research/_agent/` contains corpus updates, single-name deep dives, chart scripts with PNG/CSV, and one-off demos (`jev-ling-repro/`). Date-based corpus update packages are grouped under `research/_agent/corpus-updates/YYYY-MM-DD/`; chart assets and other files with established document or reproduction links retain their current paths. See the `_agent` README for navigation. `Serenity/` is **not** structured like `Herman Jin/`: it holds only `agent-index.json` plus six files under `data/clean/`, with no `x-archive/` or `_source/` yet. `Herman Jin/` is large — never stage it wholesale; stage named files only. Scraped social data is for private analysis only: do not republish raw transcripts or posts, and do not attribute derived views to a person beyond what the corpus actually supports. The GitHub repository is publicly visible; that visibility does not grant permission to redistribute source material. Do not put raw source content, credentials, or local settings in PR descriptions, workflow logs, or artifacts. Scraping credentials and session state stay out of the repo. Distilled output is the user's research, not a publication.
