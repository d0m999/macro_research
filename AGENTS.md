# Repository Guidelines

## Project Structure & Module Organization

This repository is a TradingView/Pine Script research workspace, not a live trading engine. `PineScript/` contains standalone indicators grouped into `_L∞p/` core studies, `Open Interest/`, `Oscillator/`, `Price_Zones/`, and `Vol/`. `strategy-notes/` holds strategy assumptions and checklists; `strategy-notes/design/` contains self-contained HTML visualization mockups. `docs/` contains methodology and process notes. Read `CLAUDE.md` before changing scope or workflow assumptions.

## Build, Test, and Development Commands

There is currently no package manager, build script, or local runtime. Useful checks are:

```bash
git status --short --branch
rg --files PineScript strategy-notes docs
rg -n '^//@version=|request\.security|lookahead|barstate\.isconfirmed' PineScript
git diff --check
```

For Pine changes, paste the modified file into the TradingView Pine Editor, compile it, and inspect representative symbols and timeframes. Check data availability, closed-bar behavior, multi-timeframe requests, and alerts when relevant.

## Coding Style & Naming Conventions

Prefer Pine Script v6 for new work; preserve v5 scripts unless migration is part of the change. Match the surrounding file’s indentation to avoid noisy diffs; use four spaces for new blocks where practical. Keep variables and inputs descriptive (`camelCase` is common), use clear helper names such as `f_*`, and keep user-facing labels/tooltips explicit. Use descriptive filenames within the existing category directories; do not rename files casually.

## Testing Guidelines

No automated test framework or coverage target is configured. Treat TradingView compilation plus chart-level visual review as the acceptance test. For signal changes, verify confirmed-bar and repaint/lookahead behavior and document the data source, especially for OI. Do not treat a design mockup as proof that the Pine implementation exists.

## Commit & Pull Request Guidelines

Use concise imperative subjects with the repository’s established prefixes: `feat:`, `fix:`, `docs:`, `chore:`, or `refactor:`; an optional scope is fine. PRs should describe changed scripts, symbols/timeframes checked, compile or chart evidence, and screenshots for visual changes. Preserve unrelated work and untracked artifacts; stage named files rather than using `git add -A`.

## Security & Scope

Never commit `.env`, credentials, logs, or generated data. Do not reintroduce the removed Python/FreqTrade execution layer, Docker deployment, or trading database without explicit authorization. Keep TradingView price data, exchange OI feeds, and native exchange OI claims clearly distinguished in code comments and research notes.
