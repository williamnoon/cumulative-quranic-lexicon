#!/usr/bin/env python3
"""Generate the 114-day reverse-surah cumulative Qur'anic vocabulary model.

Canonical vocabulary identity
=============================
The primary learning unit is QAC's canonical LEM value on a STEM segment.
This is the corpus' lexicon grouping: inflectional variants share a lemma,
while derivationally different vocabulary (including derived verb forms) has a
different canonical lemma. That matches the product rule: do not relearn mere
inflection, but do learn a genuinely different lexical/morphological form.

Study order is exactly 114 -> 1. For each day:
    new_today = items(current_surah) - union(items(previous study days))

Roots are calculated separately. Raw stem spellings are retained only as a
supplementary morphology diagnostic and never drive the primary vocabulary
claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/bnjasim/quranic-corpus/master/quranic-corpus-morphology-0.4.txt"
SOURCE_REPO = "bnjasim/quranic-corpus"
SOURCE_PATH = "quranic-corpus-morphology-0.4.txt"
SOURCE_BLOB_SHA = "b91cec6e95d5e0306550b4aedacc7380dc71152a"
SOURCE_VERSION = "Quranic Arabic Corpus v0.4"

LOC_RE = re.compile(r"^\((\d+):(\d+):(\d+):(\d+)\)$")
FEATURE_KV_RE = re.compile(r"(?:^|\|)(LEM|ROOT):([^|]+)")

# Official/extended Buckwalter characters used by QAC/JQuranTree.
BW_TO_AR = {
    "'":"ء", ">":"أ", "&":"ؤ", "<":"إ", "}":"ئ", "A":"ا",
    "b":"ب", "p":"ة", "t":"ت", "v":"ث", "j":"ج", "H":"ح",
    "x":"خ", "d":"د", "*":"ذ", "r":"ر", "z":"ز", "s":"س",
    "$":"ش", "S":"ص", "D":"ض", "T":"ط", "Z":"ظ", "E":"ع",
    "g":"غ", "_":"ـ", "f":"ف", "q":"ق", "k":"ك", "l":"ل",
    "m":"م", "n":"ن", "h":"ه", "w":"و", "Y":"ى", "y":"ي",
    "F":"ً", "N":"ٌ", "K":"ٍ", "a":"َ", "u":"ُ", "i":"ِ",
    "~":"ّ", "o":"ْ", "^":"ٓ", "#":"ٔ", "`":"ٰ", "{":"ٱ",
    ":":"ۜ", "@":"۟", '"':"۠", "[":"ۢ", ";":"ۣ", ",":"ۥ",
    ".":"ۦ", "!":"ۨ", "-":"۪", "+":"۫", "%":"۬", "]":"ۭ",
}


def buckwalter_to_arabic(value: str | None) -> str | None:
    if value is None:
        return None
    return "".join(BW_TO_AR.get(ch, ch) for ch in value)


def extract_feature(features: str, key: str) -> str | None:
    for k, value in FEATURE_KV_RE.findall(features):
        if k == key:
            return value
    return None


def parse_qac(path: Path):
    stems_by_surah: dict[int, list[dict]] = defaultdict(list)
    all_words_by_surah: dict[int, set[tuple[int, int, int]]] = defaultdict(set)
    segment_count = 0
    missing_lemma_stems = 0

    with path.open("r", encoding="utf-8") as fh:
        # quotechar is disabled because Buckwalter uses ASCII punctuation as data.
        reader = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            if len(row) < 4:
                continue
            location, form, tag, features = row[0], row[1], row[2], row[3]
            match = LOC_RE.match(location.strip())
            if not match:
                continue
            surah, ayah, word_index, segment_index = map(int, match.groups())
            segment_count += 1
            word_key = (surah, ayah, word_index)
            all_words_by_surah[surah].add(word_key)

            if not features.startswith("STEM|"):
                continue

            lemma = extract_feature(features, "LEM")
            root = extract_feature(features, "ROOT")
            if not lemma:
                missing_lemma_stems += 1

            stems_by_surah[surah].append({
                "surah": surah,
                "ayah": ayah,
                "word_index": word_index,
                "segment_index": segment_index,
                "word_key": word_key,
                "stem_form": form,
                "tag": tag,
                "features": features,
                "lemma": lemma,
                "root": root,
            })

    return stems_by_surah, all_words_by_surah, segment_count, missing_lemma_stems


def display_items(values: set[str]):
    return [
        {"buckwalter": value, "arabic": buckwalter_to_arabic(value)}
        for value in sorted(values)
    ]


def build(stems_by_surah, all_words_by_surah):
    known_vocab: set[str] = set()
    known_roots: set[str] = set()
    known_stems: set[str] = set()
    days = []

    for day, surah in enumerate(range(114, 0, -1), start=1):
        stems = stems_by_surah.get(surah, [])
        vocab_occurrences = [x["lemma"] for x in stems if x["lemma"]]
        vocab = set(vocab_occurrences)
        roots = {x["root"] for x in stems if x["root"]}
        raw_stems = {x["stem_form"] for x in stems}

        new_vocab = vocab - known_vocab
        carried_vocab = vocab & known_vocab
        new_roots = roots - known_roots
        carried_roots = roots & known_roots
        new_stems = raw_stems - known_stems
        carried_stems = raw_stems & known_stems

        known_lexical_occurrences = sum(1 for x in vocab_occurrences if x in known_vocab)
        new_lexical_occurrences = len(vocab_occurrences) - known_lexical_occurrences

        # Orthographic-token coverage: a word is covered only when every lexical
        # STEM lemma inside that word was known before today. This avoids double
        # counting the small number of orthographic words with >1 STEM segment.
        word_lemmas: dict[tuple[int, int, int], set[str]] = defaultdict(set)
        for x in stems:
            if x["lemma"]:
                word_lemmas[x["word_key"]].add(x["lemma"])
        lexical_word_tokens = len(word_lemmas)
        known_word_tokens = sum(
            1 for lemmas in word_lemmas.values()
            if lemmas and lemmas.issubset(known_vocab)
        )
        new_word_tokens = lexical_word_tokens - known_word_tokens
        coverage_pct = (known_word_tokens / lexical_word_tokens * 100.0) if lexical_word_tokens else 0.0

        known_before_vocab = len(known_vocab)
        known_before_roots = len(known_roots)
        known_before_stems = len(known_stems)

        known_vocab |= vocab
        known_roots |= roots
        known_stems |= raw_stems

        days.append({
            "day": day,
            "surah": surah,
            "orthographic_word_tokens": len(all_words_by_surah.get(surah, set())),
            "lexical_word_tokens": lexical_word_tokens,
            "distinct_vocabulary_items": len(vocab),
            "carried_vocabulary_items": len(carried_vocab),
            "new_vocabulary_items": len(new_vocab),
            "known_before_vocabulary_items": known_before_vocab,
            "known_after_vocabulary_items": len(known_vocab),
            "known_lexical_word_tokens": known_word_tokens,
            "new_lexical_word_tokens": new_word_tokens,
            "known_lexical_word_token_coverage_pct": round(coverage_pct, 4),
            "lexical_stem_occurrences": len(vocab_occurrences),
            "known_lexical_stem_occurrences": known_lexical_occurrences,
            "new_lexical_stem_occurrences": new_lexical_occurrences,
            "distinct_roots": len(roots),
            "carried_roots": len(carried_roots),
            "new_roots": len(new_roots),
            "known_before_roots": known_before_roots,
            "known_after_roots": len(known_roots),
            "distinct_raw_stem_forms": len(raw_stems),
            "carried_raw_stem_forms": len(carried_stems),
            "new_raw_stem_forms": len(new_stems),
            "known_before_raw_stem_forms": known_before_stems,
            "known_after_raw_stem_forms": len(known_stems),
            "new_vocabulary_item_list": display_items(new_vocab),
            "new_root_list": display_items(new_roots),
        })

    return days


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(days, path: Path):
    fields = [
        "day", "surah", "orthographic_word_tokens", "lexical_word_tokens",
        "distinct_vocabulary_items", "carried_vocabulary_items", "new_vocabulary_items",
        "known_before_vocabulary_items", "known_after_vocabulary_items",
        "known_lexical_word_tokens", "new_lexical_word_tokens", "known_lexical_word_token_coverage_pct",
        "lexical_stem_occurrences", "known_lexical_stem_occurrences", "new_lexical_stem_occurrences",
        "distinct_roots", "carried_roots", "new_roots", "known_before_roots", "known_after_roots",
        "distinct_raw_stem_forms", "carried_raw_stem_forms", "new_raw_stem_forms",
        "known_before_raw_stem_forms", "known_after_raw_stem_forms",
    ]
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for d in days:
            writer.writerow({k: d[k] for k in fields})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out-dir", default=Path("data/generated"), type=Path)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    stems_by_surah, all_words_by_surah, segment_count, missing_lemma_stems = parse_qac(args.source)
    days = build(stems_by_surah, all_words_by_surah)

    assert len(days) == 114
    assert [d["surah"] for d in days] == list(range(114, 0, -1))
    assert days[0]["carried_vocabulary_items"] == 0
    assert days[0]["new_vocabulary_items"] == days[0]["distinct_vocabulary_items"]
    assert days[112]["surah"] == 2 and days[113]["surah"] == 1

    metadata = {
        "study_order": "114->1",
        "source": {
            "name": SOURCE_VERSION,
            "repository": SOURCE_REPO,
            "path": SOURCE_PATH,
            "blob_sha": SOURCE_BLOB_SHA,
            "download_url": SOURCE_URL,
            "download_sha256": sha256_file(args.source),
            "license": "GPL; Quranic Arabic Corpus © Kais Dukes 2009-2017",
        },
        "calculation": {
            "primary_vocabulary_identity": "QAC STEM segment LEM value (exact extended-Buckwalter canonical lemma)",
            "why": "QAC lemmas group inflectional variants; derivationally distinct vocabulary, including derived verb forms, uses distinct canonical lemmas",
            "known_before": "union of canonical vocabulary items from earlier study days (higher-numbered surahs)",
            "new_today": "vocab(current surah) minus known-before; Surah 1 is not in the known set on Day 113",
            "root_metric": "exact QAC ROOT values on STEM segments, independently accumulated",
            "raw_stem_metric": "supplementary diagnostic only; not the product vocabulary count",
        },
        "parsed_segment_rows": segment_count,
        "parsed_stem_rows": sum(len(v) for v in stems_by_surah.values()),
        "stems_missing_lemma": missing_lemma_stems,
        "orthographic_word_positions": sum(len(v) for v in all_words_by_surah.values()),
    }

    # Integrity checks anchored in this pinned source version.
    assert metadata["parsed_segment_rows"] == 128219
    assert metadata["orthographic_word_positions"] == 77429
    assert days[-1]["known_after_vocabulary_items"] == 4832
    assert days[-1]["known_after_roots"] == 1642

    full = {"metadata": metadata, "days": days}
    (args.out_dir / "cumulative-vocabulary.json").write_text(
        json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_csv(days, args.out_dir / "cumulative-vocabulary.csv")

    baqarah = days[112].copy()
    baqarah["benchmark"] = "Surah 2 on Day 113 after studying Surahs 114 through 3; Surah 1 is excluded from known-before"
    (args.out_dir / "baqarah-day-113.json").write_text(
        json.dumps({"metadata": metadata, "result": baqarah}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    summary = {
        "whole_quran": {
            "orthographic_word_positions": metadata["orthographic_word_positions"],
            "lexical_stem_rows": metadata["parsed_stem_rows"],
            "stems_missing_lemma": metadata["stems_missing_lemma"],
            "canonical_vocabulary_items": days[-1]["known_after_vocabulary_items"],
            "roots": days[-1]["known_after_roots"],
        },
        "baqarah_day_113": {k: v for k, v in baqarah.items() if not k.endswith("_list")},
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
