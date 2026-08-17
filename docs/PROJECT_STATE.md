# Cumulative Qur'anic Lexicon — Project State

Last updated: 2026-08-16

## Purpose

Build a 114-day Qur'anic vocabulary-learning system in which a learner studies one surah per day, starting from the back of the Qur'an and moving toward the front, so that vocabulary knowledge compounds across the entire Qur'an rather than only Juz 'Amma.

The intended study order is:

114 → 113 → ... → 3 → 2 → 1

The system should answer, for every surah, what vocabulary is genuinely new at that point in the sequence and what has already been learned from later-numbered surahs.

## Product Goal

A learner who follows the sequence for 114 days should be able to see and study the cumulative Qur'anic vocabulary required for each day's surah.

A key benchmark question is:

> On the day Surah al-Baqarah (2) is reached, after Surahs 114 through 3 have already been studied, how many vocabulary items in Surah al-Baqarah are still unseen/new?

This must be calculated from the full Qur'an dataset, not inferred from Juz 'Amma-only statistics.

## Current Problem

The current site contains all surahs in the interface, but the calculations were originally built around Juz 'Amma. Therefore the displayed cumulative/new-word calculations cannot be assumed correct for the 114-surah learning sequence.

The next implementation must calculate against every surah.

## Core Decisions

1. The unit of progression is one surah per day.
2. The sequence starts from Surah 114 and proceeds backward toward Surah 1.
3. Vocabulary is cumulative: once an item has appeared in an earlier study day, later appearances should be treated as known/review rather than new.
4. Workbook content is per-surah.
5. Drills belong inside the workbook for that surah rather than existing as a separate top-level product area.
6. Other drill-like exercises should likewise live inside the per-surah workbook.
7. The system must make its vocabulary identity rule explicit (for example lemma, root, normalized surface form, or more than one view) rather than silently mixing definitions.
8. Derived counts must be reproducible from source data and code. Numbers should not live only in chat memory.

## Required Surah Metrics

For each surah in the study sequence, compute at minimum:

- total word tokens
- distinct normalized surface forms, if retained
- distinct lemmas
- distinct roots
- lemmas already seen in previously studied surahs
- lemmas new in this surah
- roots already seen in previously studied surahs
- roots new in this surah
- cumulative distinct lemmas learned through this day
- cumulative distinct roots learned through this day

The UI must clearly label which metric is being shown. “Words” is too ambiguous on its own.

## Surah al-Baqarah Benchmark

When Surah 2 is reached, the already-studied set is Surahs 114 through 3.

Therefore:

new_lemmas_in_2 = lemmas(Surah 2) − union(lemmas(Surahs 3..114))

new_roots_in_2 = roots(Surah 2) − union(roots(Surahs 3..114))

The answer must report both the count and the actual items so it can be audited.

## Workbook Structure

Each surah should have one workbook containing the learning material and exercises for that surah. Suggested internal sections:

1. Surah overview
2. New vocabulary for this day
3. Previously learned vocabulary appearing again
4. Root families / morphology where useful
5. Recognition drills
6. Recall drills
7. Matching / multiple-choice exercises
8. Verse-context exercises
9. Review of high-frequency items
10. Answer key / explanations

This is a structural requirement, not a final pedagogical design; exercises can evolve without recreating a separate global drills product.

## Source-of-Truth Rule

Project requirements, calculation definitions, source datasets, derived outputs, and unresolved questions must be committed to the repository or represented in Linear. Chat memory is not a sufficient source of truth.

## Open Work

- Select and pin the canonical full-Qur'an morphology/lexicon dataset.
- Implement a reproducible full-Qur'an calculation pipeline.
- Produce per-surah cumulative/new lemma and root data for all 114 surahs.
- Verify the Surah 2 benchmark: unseen vocabulary after studying Surahs 114→3.
- Replace Juz 'Amma-only calculations in the site.
- Refactor workbook/drills into a per-surah workbook model.
- Expose enough provenance in the UI/data so counts can be audited.
- Add regression tests for known surah counts and cumulative behavior.

## Definition of Done for the Calculation Rewrite

The calculation work is complete only when:

- all 114 surahs are included;
- the reverse-surah study sequence is deterministic;
- lemma/root identity rules are documented;
- all derived counts can be regenerated from a pinned source dataset;
- Surah 2's new vocabulary after Surahs 3–114 is available as both counts and item lists;
- automated tests catch regressions;
- the site consumes generated full-Qur'an data rather than hand-entered/Juz 'Amma-only assumptions.

## Handoff to Power

Power should read this file first for project intent and current state. For exact computation rules and data-contract expectations, read `docs/CALCULATION_SPEC.md`.
