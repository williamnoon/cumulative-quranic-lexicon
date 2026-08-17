#!/usr/bin/env python3
"""Build reverse-surah cumulative Qur'anic vocabulary metrics from QAC v0.4.

Study order: 114 -> 1.

Primary learning-unit identity
------------------------------
The primary vocabulary unit is the normalized QAC STEM surface form. QAC splits
an orthographic word into prefixes, a stem, and suffixes; using the STEM form
keeps derivational/conjugational shapes distinct while not counting attached
conjunctions, articles, prepositions, pronominal suffixes, or case/harakah
variation as a brand-new lexical item. Arabic diacritics and Quranic annotation
marks are removed for identity comparison, but the vocalized attested form is
retained in the source corpus for audit.

Separate metrics are emitted for QAC-annotated lemmas and roots. QAC v0.4 does
not provide a universal lemma for every stem category, so lemma counts are
explicitly supplementary and are NOT the primary cumulative vocabulary claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

SOURCE_URL = "https://raw.githubusercontent.com/bnjasim/quranic-corpus/master/quranic-corpus-morphology-0.4.txt"
SOURCE_REPO = "bnjasim/quranic-corpus"
SOURCE_PATH = "quranic-corpus-morphology-0.4.txt"
SOURCE_BLOB_SHA = "b91cec6e95d5e0306550b4aedacc7380dc71152a"
SOURCE_VERSION = "Quranic Arabic Corpus v0.4"

LOC_RE = re.compile(r"^\((\d+):(\d+):(\d+):(\d+)\)$")
FEATURE_KV_RE = re.compile(r"(?:^|\|)(LEM|ROOT):([^|]+)")


def normalize_arabic(text: str) -> str:
    """Normalize for vocabulary identity without collapsing Arabic letters."""
    text = unicodedata.normalize("NFKD", text)
    out = []
    for ch in text:
        cp = ord(ch)
        if unicodedata.combining(ch):
            continue
        if 0x0610 <= cp <= 0x061A or 0x064B <= cp <= 0x065F or 0x06D6 <= cp <= 0x06ED:
            continue
        if ch in {"ـ", "۞", "۩"}:
            continue
        out.append(ch)
    return "".join(out).strip()


def extract_feature(features: str, key: str) -> str | None:
    for k, value in FEATURE_KV_RE.findall(features):
        if k == key:
            return value
    return None


def parse_qac(path: Path):
    stems_by_surah: dict[int, list[dict]] = defaultdict(list)
    word_positions_by_surah: dict[int, set[tuple[int, int, int]]] = defaultdict(set)
    segment_count = 0

    with path.open("r", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        for row in reader:
            if len(row) < 4:
                continue
            location, form, tag, features = row[0], row[1], row[2], row[3]
            match = LOC_RE.match(location.strip())
            if not match:
                continue
            surah, ayah, word_index, segment_index = map(int, match.groups())
            segment_count += 1
            word_positions_by_surah[surah].add((surah, ayah, word_index))

            if not features.startswith("STEM|"):
                continue

            unit = normalize_arabic(form)
            if not unit:
                continue
            lemma = extract_feature(features, "LEM")
            root = extract_feature(features, "ROOT")
            stems_by_surah[surah].append({
                "surah": surah,
                "ayah": ayah,
                "word_index": word_index,
                "segment_index": segment_index,
                "form": form,
                "unit": unit,
                "tag": tag,
                "features": features,
                "lemma": normalize_arabic(lemma) if lemma else None,
                "lemma_attested": lemma,
                "root": normalize_arabic(root) if root else None,
                "root_attested": root,
            })

    return stems_by_surah, word_positions_by_surah, segment_count


def sorted_items(values):
    return sorted(v for v in values if v)


def build(stems_by_surah, word_positions_by_surah):
    known_units: set[str] = set()
    known_lemmas: set[str] = set()
    known_roots: set[str] = set()
    days = []

    for day, surah in enumerate(range(114, 0, -1), start=1):
        stems = stems_by_surah.get(surah, [])
        unit_occurrences = [x["unit"] for x in stems]
        units = set(unit_occurrences)
        lemmas = {x["lemma"] for x in stems if x["lemma"]}
        roots = {x["root"] for x in stems if x["root"]}

        new_units = units - known_units
        carried_units = units & known_units
        new_lemmas = lemmas - known_lemmas
        carried_lemmas = lemmas & known_lemmas
        new_roots = roots - known_roots
        carried_roots = roots & known_roots

        known_occurrences = sum(1 for u in unit_occurrences if u in known_units)
        new_occurrences = len(unit_occurrences) - known_occurrences
        stem_token_coverage = (known_occurrences / len(unit_occurrences) * 100.0) if unit_occurrences else 0.0

        known_before_unit_count = len(known_units)
        known_before_lemma_count = len(known_lemmas)
        known_before_root_count = len(known_roots)

        known_units |= units
        known_lemmas |= lemmas
        known_roots |= roots

        days.append({
            "day": day,
            "surah": surah,
            "orthographic_word_tokens": len(word_positions_by_surah.get(surah, set())),
            "stem_occurrences": len(unit_occurrences),
            "distinct_learning_units": len(units),
            "carried_learning_units": len(carried_units),
            "new_learning_units": len(new_units),
            "known_before_learning_units": known_before_unit_count,
            "known_after_learning_units": len(known_units),
            "known_stem_occurrences": known_occurrences,
            "new_stem_occurrences": new_occurrences,
            "known_stem_token_coverage_pct": round(stem_token_coverage, 4),
            "distinct_qac_annotated_lemmas": len(lemmas),
            "carried_qac_annotated_lemmas": len(carried_lemmas),
            "new_qac_annotated_lemmas": len(new_lemmas),
            "known_before_qac_annotated_lemmas": known_before_lemma_count,
            "known_after_qac_annotated_lemmas": len(known_lemmas),
            "distinct_roots": len(roots),
            "carried_roots": len(carried_roots),
            "new_roots": len(new_roots),
            "known_before_roots": known_before_root_count,
            "known_after_roots": len(known_roots),
            "new_learning_unit_items": sorted_items(new_units),
            "new_qac_annotated_lemma_items": sorted_items(new_lemmas),
            "new_root_items": sorted_items(new_roots),
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
        "day", "surah", "orthographic_word_tokens", "stem_occurrences",
        "distinct_learning_units", "carried_learning_units", "new_learning_units",
        "known_before_learning_units", "known_after_learning_units",
        "known_stem_occurrences", "new_stem_occurrences", "known_stem_token_coverage_pct",
        "distinct_qac_annotated_lemmas", "carried_qac_annotated_lemmas", "new_qac_annotated_lemmas",
        "known_before_qac_annotated_lemmas", "known_after_qac_annotated_lemmas",
        "distinct_roots", "carried_roots", "new_roots", "known_before_roots", "known_after_roots",
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
    stems_by_surah, word_positions_by_surah, segment_count = parse_qac(args.source)
    days = build(stems_by_surah, word_positions_by_surah)

    assert len(days) == 114
    assert days[0]["surah"] == 114 and days[-1]["surah"] == 1
    assert days[0]["carried_learning_units"] == 0
    assert days[0]["new_learning_units"] == days[0]["distinct_learning_units"]
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
            "primary_learning_unit": "normalized QAC STEM surface form",
            "normalization": "Unicode NFKD; remove Arabic combining/harakah/Quranic annotation marks and tatweel; preserve Arabic letters",
            "known_before": "union of the same metric from earlier study days (higher-numbered surahs)",
            "new_today": "current-surah set minus known-before set",
            "lemma_warning": "QAC v0.4 lemma annotation is not universal across every stem category; lemma results are supplementary and not the primary vocabulary claim",
        },
        "parsed_segment_rows": segment_count,
        "parsed_stem_rows": sum(len(v) for v in stems_by_surah.values()),
        "orthographic_word_positions": sum(len(v) for v in word_positions_by_surah.values()),
    }

    full = {"metadata": metadata, "days": days}
    (args.out_dir / "cumulative-vocabulary.json").write_text(json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(days, args.out_dir / "cumulative-vocabulary.csv")

    baqarah = days[112].copy()
    baqarah["benchmark"] = "Surah 2 on Day 113 after studying Surahs 114 through 3; Surah 1 is not included in known-before"
    (args.out_dir / "baqarah-day-113.json").write_text(json.dumps({"metadata": metadata, "result": baqarah}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "whole_quran": {
            "orthographic_word_positions": metadata["orthographic_word_positions"],
            "stem_rows": metadata["parsed_stem_rows"],
            "cumulative_learning_units": days[-1]["known_after_learning_units"],
            "cumulative_qac_annotated_lemmas": days[-1]["known_after_qac_annotated_lemmas"],
            "cumulative_roots": days[-1]["known_after_roots"],
        },
        "baqarah_day_113": {k: v for k, v in baqarah.items() if not k.endswith("_items")},
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
