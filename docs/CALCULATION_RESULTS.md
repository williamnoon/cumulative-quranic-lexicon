# Verified Full-Qur'an Cumulative Vocabulary Results

Last verified: 2026-08-16

## Status

The full reverse-surah calculation has been generated for every study day in the exact order:

`114 → 113 → ... → 3 → 2 → 1`

The results are machine-generated from the pinned corpus and are stored in `data/generated/`.

## Canonical Source

- Dataset: Quranic Arabic Corpus v0.4
- Pinned mirror: `bnjasim/quranic-corpus`
- File: `quranic-corpus-morphology-0.4.txt`
- Git blob SHA: `b91cec6e95d5e0306550b4aedacc7380dc71152a`
- Download SHA-256: `a1d12923815341face765083805d2148ed2d9f5cc3f7d6665219d887675d8c46`
- Parsed morphology segments: 128,219
- Qur'anic orthographic word positions: 77,429
- STEM rows: 77,915

## Canonical Vocabulary Identity

The product's primary cumulative vocabulary identity is the QAC `LEM:` value attached to a `STEM` segment.

This is intentional. QAC canonical lemmas group inflectional variants under one lexical item while derivationally distinct vocabulary can have a distinct canonical lemma. Therefore ordinary conjugational/case variation is not counted as a completely new vocabulary item, while a genuinely different lexical/derivational form can be.

Roots are accumulated independently and never substituted for vocabulary-item counts.

Raw STEM spellings are retained only as a morphology diagnostic. They are not the product's primary "new vocabulary" number.

## Whole-Qur'an Integrity Results

- Canonical QAC vocabulary items encountered across the complete 114-day sequence: **4,832**
- Distinct QAC roots: **1,642**
- Orthographic word positions: **77,429**

QAC has **3,307 STEM rows without a `LEM:` assignment**. Those rows are not silently promoted into invented lemmas. The 4,832 vocabulary metric is therefore specifically the canonical QAC lemma-bearing lexical vocabulary layer. Grammatical/function-word learning that lacks a QAC lemma must be handled and labeled separately in the product.

## Day 1 — Surah 114, An-Nas

With no previous study days:

- Distinct canonical vocabulary items: **15**
- Carried in: **0**
- New today: **15**
- Distinct roots: **11**
- New roots: **11**

This confirms the cumulative sequence begins from an empty known set.

## Day 113 — Surah 2, Al-Baqarah

Known-before set: Surahs **114 through 3 only**. Surah al-Fatihah (1) is not included because it is Day 114.

Canonical vocabulary:

- Distinct vocabulary items in Al-Baqarah: **1,136**
- Already learned from Surahs 114→3: **991**
- **New vocabulary items: 145**
- Known canonical vocabulary before Al-Baqarah: **4,686**
- Known canonical vocabulary after Al-Baqarah: **4,831**

Roots:

- Distinct roots in Al-Baqarah: **585**
- Already encountered roots: **563**
- **New roots: 22**
- Known roots before Al-Baqarah: **1,620**
- Known roots after Al-Baqarah: **1,642**

Lexical word-token coverage among orthographic words carrying QAC lemma-bearing lexical STEMs:

- Lexical word tokens measured: **5,835**
- Covered entirely by previously learned canonical vocabulary: **5,656**
- Containing new canonical vocabulary: **179**
- **Previously learned lexical-token coverage: 96.9323%**

Raw STEM-form diagnostic, not the vocabulary metric:

- Distinct raw STEM spellings in Al-Baqarah: 2,065
- Previously encountered raw STEM spellings: 1,542
- New raw STEM spellings: 523

The **523** figure must never be presented as the number of new vocabulary items. The canonical vocabulary result is **145**.

## Day 114 — Surah 1, Al-Fatihah

After Surahs 114→2 have been studied:

- Distinct canonical vocabulary items: **23**
- Already learned: **22**
- **New vocabulary items: 1**
- Distinct roots: **18**
- Already learned roots: **18**
- **New roots: 0**

This brings the full canonical vocabulary inventory from 4,831 after Al-Baqarah to 4,832 after Al-Fatihah.

## Generated Artifacts

- `scripts/build_cumulative_vocab.py` — reproducible calculation
- `data/generated/cumulative-vocabulary.csv` — one row for every study day/surah
- `data/generated/cumulative-vocabulary.json` — full metrics plus per-day new-item lists
- `data/generated/baqarah-day-113.json` — exact Day-113 benchmark and item lists
- `data/generated/summary.json` — compact integrity and benchmark summary
- `.github/workflows/build-cumulative-vocabulary.yml` — reproducible CI generation/validation

## Validation

CI validates:

- exactly 114 study days;
- exact surah order 114→1;
- Surah 114 begins with zero carried vocabulary;
- Surah 2 is Day 113 and Surah 1 is Day 114;
- 128,219 morphology segment rows;
- 77,429 orthographic word positions;
- final canonical vocabulary inventory = 4,832;
- final root inventory = 1,642.

The successful calculation run is GitHub Actions run `31985336341`.

## Product Rule

The application must consume these generated artifacts for cumulative counts. The handcrafted `WORDS` teaching annotations may enrich lessons, explanations, comparisons, and exercises, but must never drive exhaustive full-Qur'an known/new calculations.
