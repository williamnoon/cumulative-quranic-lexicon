# Cumulative Qur'anic Lexicon — Project State

Last updated: 2026-08-16

## Purpose

Build a 114-day Qur'anic vocabulary-learning system in which the learner studies one surah per day in this exact order:

`114 → 113 → ... → 3 → 2 → 1`

Vocabulary knowledge compounds day by day. Every current-surah vocabulary item is either already learned from a previous study day or genuinely new today.

## Current Verified State

The exhaustive full-Qur'an cumulative calculation is now implemented and reproducible on branch `williamdeval/net-61-full-corpus-calculation`.

The calculation uses pinned Quranic Arabic Corpus v0.4 data rather than the handcrafted teaching `WORDS` array.

Canonical source and generated outputs are documented in:

- `docs/CALCULATION_SPEC.md`
- `docs/CALCULATION_RESULTS.md`
- `scripts/build_cumulative_vocab.py`
- `data/generated/cumulative-vocabulary.csv`
- `data/generated/cumulative-vocabulary.json`
- `data/generated/baqarah-day-113.json`
- `data/generated/summary.json`

The generated CSV contains all 114 study days, beginning with Surah 114 and ending with Surah 1.

## Canonical Vocabulary Rule

Primary vocabulary identity is the QAC canonical `LEM:` value on a `STEM` segment.

This groups inflectional variants under one vocabulary identity while retaining genuinely different lexical/derivational forms as distinct canonical items where QAC assigns them distinct lemmas.

Roots are a separate relationship/learning dimension. Raw STEM surface spellings are retained only as a morphology diagnostic and must not be substituted for the vocabulary count.

Truth boundary: 3,307 QAC STEM rows lack `LEM:`. The product must not invent canonical lemmas for those rows. Function/grammar material outside the QAC lemma-bearing lexical layer needs an explicitly separate identity model if it is counted as learned vocabulary.

## Verified Corpus Integrity

- Qur'anic orthographic word positions: **77,429**
- QAC morphology segment rows: **128,219**
- QAC STEM rows: **77,915**
- Canonical lemma-bearing vocabulary inventory: **4,832**
- Distinct roots: **1,642**

## Verified Al-Baqarah Benchmark

Al-Baqarah is Day 113. Its known-before set contains Surahs 114→3; Al-Fatihah is not included.

- Distinct canonical vocabulary items in Al-Baqarah: **1,136**
- Already learned: **991**
- **New vocabulary: 145**
- Known vocabulary before Al-Baqarah: **4,686**
- Known vocabulary after Al-Baqarah: **4,831**
- Distinct roots in Al-Baqarah: **585**
- Already encountered roots: **563**
- **New roots: 22**
- QAC lemma-bearing lexical word tokens measured: **5,835**
- Covered entirely by previously learned vocabulary: **5,656**
- Previously learned lexical-token coverage: **96.9323%**

The separate raw-STEM diagnostic is 523 new surface forms. **523 is not the new-vocabulary count.**

On Day 114, Al-Fatihah adds exactly **1** new canonical vocabulary item and **0** new roots, bringing the full totals to 4,832 vocabulary items and 1,642 roots.

## Product Architecture — Workbook Is the Learning Product

The Workbook is not a container for drills alone. The current surah/day is the organizing axis for every capability that helps the learner acquire and use vocabulary.

Each surah Workbook must contain or contextually expose:

1. Orient — day/surah, cumulative progress, known-before/new-today state.
2. Read — full surah context, known vocabulary subdued and new vocabulary emphasized.
3. Learn — today's genuinely new vocabulary with meanings/explanations.
4. Roots & Families — root relationships relevant to current vocabulary and previously learned forms.
5. Forms / Morphology — attested forms and the morphological relationships that matter to the current vocabulary.
6. Compare — semantic neighbors, opposites, near-synonyms, lookalikes, and distinctions relevant to the current lesson.
7. Concordance / In Context — occurrences and verse context, clearly distinguishing already-studied evidence from future/reference evidence.
8. Practice — recognition, recall, root-family, morphology, semantic distinction, context, and returning-word exercises.
9. Review — cumulative/spaced retrieval of vocabulary from previous study days.
10. Complete — record/confirm the day's completion and advance to the next surah.

A learner should not need to leave the current Workbook to understand, relate, find, compare, or practice a current vocabulary item.

Roots, Forms, Concordance, Compare, Drills, and the word-detail experience are therefore Workbook capabilities, not disconnected primary learning destinations.

## Current Site Limitation

The live/static application still contains Juz 'Amma-era assumptions and handcrafted `WORDS`-driven counts. The generated corpus calculation is correct and stored, but the UI has not yet been refactored to consume it.

## Remaining Work

1. Wire `data/generated/cumulative-vocabulary.json` into the application so all displayed cumulative counts come from the verified full-corpus model.
2. Expand the surah/day experience to all 114 surahs.
3. Rebuild navigation around the per-surah Workbook architecture above.
4. Move Roots, Forms, Concordance, Compare, Drills, and contextual word-detail learning into each current-surah Workbook.
5. Keep handcrafted teaching annotations as enrichment only; never let annotation completeness drive exhaustive corpus claims.
6. Decide and implement the separately labeled grammar/function-word learning layer for QAC STEMs without canonical `LEM:` where pedagogically useful.
7. Surface source/provenance and metric definitions in a compact defensible way.
8. Add UI/regression tests that ensure displayed counts match generated data.

## Source-of-Truth Rule

Repo docs + generated data are durable product truth. Linear is the durable execution queue. Chat memory is convenience only.

## Handoff to Power

Read in this order:

1. `docs/PROJECT_STATE.md`
2. `docs/CALCULATION_SPEC.md`
3. `docs/CALCULATION_RESULTS.md`
4. Linear project `Cumulative Qur'anic Lexicon`

Do not reconstruct or estimate cumulative vocabulary counts from the UI's handcrafted `WORDS` data.
