# Cumulative Vocabulary Calculation Specification

Last updated: 2026-08-16

## Objective

Generate reproducible vocabulary statistics for the full Qur'an across the study order 114 → 1.

The implementation must never rely on Juz 'Amma-only accumulation when displaying whole-Qur'an progress.

## Canonical Study Order

```text
114, 113, 112, ..., 3, 2, 1
```

For a surah S, the previously learned corpus is every surah with a number greater than S.

Example for Surah 2:

```text
previously_studied = {3, 4, ..., 114}
```

Surah 1 is not part of Al-Baqarah's known-before set because Al-Fatihah is studied on Day 114, after Al-Baqarah on Day 113.

## Pinned Source

The calculation source is Quranic Arabic Corpus v0.4, pinned through the exact corpus blob:

- repository: `bnjasim/quranic-corpus`
- file: `quranic-corpus-morphology-0.4.txt`
- blob SHA: `b91cec6e95d5e0306550b4aedacc7380dc71152a`
- download SHA-256: `a1d12923815341face765083805d2148ed2d9f5cc3f7d6665219d887675d8c46`

The generator must fail validation if the pinned corpus no longer reproduces the expected integrity counts.

## Canonical Vocabulary Identity

The primary vocabulary-learning identity is the exact QAC `LEM:` value on a `STEM` segment.

Why this identity is used:

- QAC canonical lemmas group forms that vary by inflection rather than treating every conjugated/case-marked spelling as a new vocabulary item.
- Derivationally distinct lexical forms can have distinct canonical lemmas, preserving the morphology that matters for learning.
- Roots remain available as a separate relationship dimension rather than being confused with lexical vocabulary.

Therefore the product's primary cumulative labels should be:

- Vocabulary items
- New vocabulary
- Previously learned vocabulary
- Cumulative vocabulary

with provenance explaining that these are QAC canonical lemma identities.

### Root

The exact QAC `ROOT:` value on a `STEM` segment. Root counts and novelty are always reported separately from vocabulary items.

### Raw STEM form

The QAC surface form of a `STEM` segment. This is retained as a supplementary morphology diagnostic only. It is not the primary cumulative vocabulary identity because inflectional variants would otherwise inflate the number of things a learner is said to need to learn.

### Orthographic word token

A Qur'anic word position identified by `(surah, ayah, word_index)`. QAC may split an orthographic word into multiple morphological segments.

### Lexical word token

An orthographic word position containing at least one `STEM` segment with a QAC `LEM:` assignment. Coverage percentages must explicitly state that they refer to this lemma-bearing lexical layer.

## Missing-Lemma Truth Boundary

The pinned QAC v0.4 source contains 77,915 `STEM` rows, of which 3,307 do not carry a `LEM:` assignment.

The pipeline must not invent lemmas for those rows and must report the count. The canonical 4,832-item vocabulary inventory is specifically the QAC lemma-bearing lexical layer. If the product teaches function words, pronouns, or other grammatical material outside that layer, those items need a separately defined and labeled identity system.

## Per-Surah Set Definitions

Let:

- `V(S)` = set of distinct QAC canonical `LEM:` values on `STEM` segments in Surah S
- `R(S)` = set of distinct QAC `ROOT:` values on `STEM` segments in Surah S
- `W(S)` = orthographic word positions in Surah S

Previously seen sets:

```text
seen_vocab_before(S) = union(V(k) for k in S+1..114)
seen_roots_before(S) = union(R(k) for k in S+1..114)
```

New items:

```text
new_vocab(S) = V(S) - seen_vocab_before(S)
new_roots(S) = R(S) - seen_roots_before(S)
```

Carried/known items:

```text
carried_vocab(S) = V(S) intersect seen_vocab_before(S)
carried_roots(S) = R(S) intersect seen_roots_before(S)
```

Cumulative sets after studying S:

```text
cumulative_vocab_through(S) = union(V(k) for k in S..114)
cumulative_roots_through(S) = union(R(k) for k in S..114)
```

## Surah 2 Required Benchmark

Compute exactly:

```text
V2_new = V(2) - union(V(k) for k in 3..114)
R2_new = R(2) - union(R(k) for k in 3..114)
```

Verified result from the pinned corpus:

- distinct vocabulary items in Surah 2: 1,136
- carried vocabulary items: 991
- **new vocabulary items: 145**
- distinct roots: 585
- carried roots: 563
- **new roots: 22**
- previously learned lexical-word-token coverage: **96.9323%** (5,656 of 5,835 measured lexical word tokens)

The old/raw STEM diagnostic of 523 new surface forms is not the vocabulary result and must not be displayed as such.

Required stored outputs:

- count and auditable list of every new vocabulary item
- count and auditable list of every new root
- token-coverage metrics with their denominator clearly labeled
- source dataset/version/blob
- calculation code version

The result must not be copied from chat or manually entered into the UI.

## Generated Data Contract

Canonical generated artifacts:

```text
data/generated/cumulative-vocabulary.json
data/generated/cumulative-vocabulary.csv
data/generated/baqarah-day-113.json
data/generated/summary.json
```

`cumulative-vocabulary.csv` contains exactly one row per study day, 114 rows after the header, in the exact sequence 114→1.

`cumulative-vocabulary.json` contains the same metrics plus machine-readable per-day lists of new vocabulary items and roots.

## Source Data Requirements

The canonical morphology source must:

- cover all 114 surahs;
- identify verse/word locations;
- provide canonical lemma values for lexical vocabulary calculations;
- provide root data for root metrics;
- be pinned by an exact content identity;
- preserve licensing/provenance information;
- expose missing lemma/root assignments instead of silently dropping them from provenance.

## Validation

CI must validate at minimum:

1. exactly 114 study days;
2. study order is 114→1;
3. Surah 114 begins with zero carried vocabulary;
4. new and carried vocabulary are disjoint and together equal the current-surah vocabulary set;
5. analogous root invariants;
6. cumulative vocabulary/root counts never decrease as study progresses;
7. Surah 2 is Day 113 and uses Surahs 3–114 as its known-before set;
8. Surah 1 is Day 114;
9. generated counts equal generated item-list lengths;
10. source/version/blob metadata is present;
11. parsed morphology rows = 128,219;
12. orthographic word positions = 77,429;
13. final canonical vocabulary inventory = 4,832;
14. final root inventory = 1,642.

## UI Rule

Do not display an ambiguous naked label such as “new words.” Use labels whose meaning is defined by the data contract, such as:

- New vocabulary
- Previously learned vocabulary
- New roots
- Previously learned roots
- Lexical word-token coverage
- Raw STEM forms (only where morphology diagnostics are intentionally shown)

## Reproducibility Rule

If a number cannot be regenerated from the pinned source data and `scripts/build_cumulative_vocab.py`, it is not a project fact.

Verified results and caveats are recorded in `docs/CALCULATION_RESULTS.md`.
