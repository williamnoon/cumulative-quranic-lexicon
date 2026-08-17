# Power Context — Cumulative Qur'anic Lexicon

This file is the entry point for any agent or Power session working on this repository.

## Read first

1. `docs/PROJECT_STATE.md` — current product truth, goals, architecture direction, known limitations, and remaining work.
2. `docs/CALCULATION_SPEC.md` — canonical cumulative-vocabulary calculation rules and the exact Al-Baqarah benchmark definition.
3. Linear project: **Cumulative Qur'anic Lexicon** — actionable backlog and execution status.

## Core goal

Create a 114-day Qur'anic vocabulary-learning system in study order 114 → 1. Each surah is one day. The system must calculate vocabulary cumulatively across the full Qur'an, not only Juz 'Amma.

## Non-negotiable calculation principle

For a surah studied on day `d`:

- `known_before` = union of canonical vocabulary items seen in all previously studied surahs
- `new_today` = vocabulary of the current surah minus `known_before`
- `carried_in` = vocabulary of the current surah intersect `known_before`
- `known_after` = `known_before` union vocabulary of the current surah

Do not derive full-Qur'an claims from the handcrafted teaching `WORDS` array. Exhaustive corpus data drives calculations; teaching annotations enrich the experience.

## Benchmark question

When the learner reaches Surah Al-Baqarah (Surah 2, Day 113 after studying Surahs 114→3), compute exactly:

- unseen/new distinct vocabulary items
- unseen roots, separately
- token coverage in Al-Baqarah from already learned vocabulary
- machine-readable unseen-item list

The answer must be reproducible from a named source dataset/version and generation script.

## Workbook direction

Workbook is per surah/day and is the primary learning surface:

Read → Learn → Practice → Review → Complete

Drills live inside the Workbook rather than as a separate primary destination.

## Working rule for agents

Before making a product or calculation decision, update the durable project artifacts rather than relying on chat memory. If a decision changes, update the relevant doc and Linear issue so future sessions inherit the new truth.
