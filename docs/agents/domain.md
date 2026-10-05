# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CLAUDE.md`** at the repo root — **read this first.** It defines which of the three work streams a task belongs to and carries the hard constraints. Without it you will read this repo as a Pine-only workspace, which is wrong.
- **`CONTEXT.md`** at the repo root — the OI term glossary. **Scoped to the Pine/OI line only.** It does not define vocabulary for the corpus or fundamental-research lines.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. **Not created yet.**

If a location doesn't exist, **proceed silently**. Don't flag its absence or suggest creating it upfront. The `/domain-modeling` skill creates domain documentation lazily when terms or decisions actually get resolved.

## Configured layout

This repository uses a single-context layout across three work streams:

/
├── CONTEXT.md                  # OI glossary (Pine/OI line only)
├── docs/
│   └── adr/
├── Herman Jin/                 # primary — @ShanghaoJin corpus, 1.6 GB
├── Serenity/                   # primary — @aleabitoreddit corpus (different person)
├── research/                   # primary output + fundamental research
│   ├── Herman-Jin 观点 rollup.md
│   └── _agent/
├── GLW/                        # secondary — public-source channel validation
├── .agents/                    # skills, validators, data-source routing SoT
│   ├── skills/
│   ├── scripts/
│   ├── tests/
│   ├── data-sources.jsonl
│   └── PUBLIC-SOURCE-POLICY.md
├── fundamental-research/
├── PineScript/                 # dormant
└── strategy-notes/             # dormant

## Use the glossary's vocabulary

Vocabulary is per stream, not global:

- **Pine/OI line:** use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids (e.g. "实时 OI 柱" not "已确认 OI").
- **Corpus line:** use the terms as defined in `CLAUDE.md` and in the corpus package manifests — 包 / manifest / posts.jsonl / replies.jsonl / 回锚 / 极性 / rollup. "语料命中" and "本人推荐" are distinct concepts and must not be collapsed into one word.
- **Fundamental research line:** use the status vocabulary from `GLW/` and `.agents/PUBLIC-SOURCE-POLICY.md` — `PASS` / `PARTIAL` / `AVAILABLE` / `SOURCE_UNAVAILABLE` / `USER_UPLOAD_REQUIRED`. Don't soften `SOURCE_UNAVAILABLE` into a hedge.

If the concept you need isn't in any of these yet, that's a signal: either you're inventing language the project doesn't use and should reconsider, or there's a real gap to note for `/domain-modeling`.

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007, but worth reopening because…_
