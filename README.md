# The Cumulative Quranic Lexicon

An interactive, cumulative reading of Qur'anic vocabulary: one surah a day for 114 days, from An-Nas back to Al-Fatihah. Every count comes from the Quranic Arabic Corpus v0.4.

## Run locally

This is a static site. Open `index.html` directly, or serve the folder with any static HTTP server.

```bash
npx serve .
```

## Deploy

Import the GitHub repository into Vercel with the framework preset set to **Other**. No build command or environment variables are required.

## Where the numbers come from

1. `scripts/build_cumulative_vocab.py` calculates all 114 study days from the pinned corpus into `data/generated/` (see `docs/CALCULATION_SPEC.md`).
2. `scripts/embed_corpus.py` writes that data into the `CORPUS:BEGIN/END` block of `index.html`, so the site stays one self-contained file. Never edit that block by hand.
3. `scripts/check_app.py` fails if the embedded block is stale, if any day disagrees with the locked benchmarks, or if old research figures reappear. It runs in CI on every push and pull request.

If the generated data changes, run `python scripts/embed_corpus.py` and commit `index.html`.

Handcrafted teaching notes (`WORDS`, Compare, Forms, Workbook) cover Juz 'Amma and are enrichment only. They never drive counts.
