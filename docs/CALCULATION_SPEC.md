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

## Vocabulary Identities

The pipeline should preserve distinct dimensions rather than collapse them into one ambiguous “word” count.

### Token
An occurrence of a word in Qur'anic text.

### Normalized surface form
A normalized orthographic form. Normalization rules must be versioned if this metric is used.

### Lemma
The lexical headword assigned by the pinned morphology dataset.

### Root
The morphological root assigned by the pinned dataset.

The product's primary “vocabulary learned” view should use a declared identity. Until a different decision is documented, generate both lemma and root metrics so the distinction remains visible.

## Per-Surah Set Definitions

Let:

- `L(S)` = set of distinct lemmas occurring in Surah S
- `R(S)` = set of distinct roots occurring in Surah S
- `T(S)` = total tokens in Surah S

Previously seen sets:

```text
seen_lemmas_before(S) = union(L(k) for k in S+1..114)
seen_roots_before(S)  = union(R(k) for k in S+1..114)
```

New items:

```text
new_lemmas(S) = L(S) - seen_lemmas_before(S)
new_roots(S)  = R(S) - seen_roots_before(S)
```

Review/known items:

```text
known_lemmas(S) = L(S) intersect seen_lemmas_before(S)
known_roots(S)  = R(S) intersect seen_roots_before(S)
```

Cumulative learned sets after studying S:

```text
cumulative_lemmas_through(S) = union(L(k) for k in S..114)
cumulative_roots_through(S)  = union(R(k) for k in S..114)
```

## Surah 2 Required Benchmark

Compute exactly:

```text
L2_new = L(2) - union(L(k) for k in 3..114)
R2_new = R(2) - union(R(k) for k in 3..114)
```

Required output:

- `count(L2_new)`
- sorted/auditable list of every lemma in `L2_new`
- `count(R2_new)`
- sorted/auditable list of every root in `R2_new`
- source dataset/version/commit
- calculation code version/commit

The result must not be copied from chat or manually entered into the UI.

## Generated Data Contract

Prefer a generated artifact such as:

```text
data/generated/surah-vocabulary.json
```

Suggested structure:

```json
{
  "source": {
    "name": "...",
    "version": "...",
    "commit": "..."
  },
  "studyOrder": "114-to-1",
  "surahs": {
    "2": {
      "tokenCount": 0,
      "distinctLemmaCount": 0,
      "distinctRootCount": 0,
      "newLemmaCount": 0,
      "newLemmas": [],
      "knownLemmaCount": 0,
      "newRootCount": 0,
      "newRoots": [],
      "knownRootCount": 0,
      "cumulativeLemmaCount": 0,
      "cumulativeRootCount": 0
    }
  }
}
```

Exact schema may change, but generated counts and item lists must remain machine-readable.

## Source Data Requirements

The canonical morphology source must:

- cover all 114 surahs;
- identify verse/word locations;
- provide lemma data for lexical vocabulary calculations;
- provide root data if root metrics are shown;
- be pinned by a stable version or commit;
- preserve licensing/provenance information.

If the source has missing lemma/root assignments, the pipeline must report them instead of silently dropping them.

## Validation

At minimum add automated checks for:

1. exactly 114 surahs represented;
2. study order is 114→1;
3. for each S, `new_lemmas(S)` and `known_lemmas(S)` are disjoint;
4. their union equals `L(S)`;
5. analogous root invariants;
6. cumulative vocabulary counts are monotonic non-decreasing as study progresses 114→1;
7. Surah 2 uses Surahs 3–114 as its seen set;
8. generated counts equal the lengths of generated item arrays;
9. source/version metadata is present.

## UI Rule

Never display a naked label such as “new words” when the underlying calculation is lemma-based or root-based. Use explicit labels such as:

- New lemmas
- New roots
- Previously seen lemmas
- Total word occurrences

## Reproducibility Rule

If a number cannot be regenerated from the pinned source data and code, it is not a project fact yet.
