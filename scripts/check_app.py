#!/usr/bin/env python3
"""Regression check: the numbers the app shows must match the corpus calculation.

Runs without a browser, so it works in CI:
  1. The embedded CORPUS block in index.html is exactly what embed_corpus.py
     would write from data/generated (no hand edits, no stale data).
  2. The embedded data covers all 114 days in study order 114 -> 1 and agrees
     with the locked benchmarks in data/generated/summary.json.
  3. Old research figures that were wrong are gone from the page.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "index.html").read_text(encoding="utf-8")
summary = json.loads((ROOT / "data/generated/summary.json").read_text(encoding="utf-8"))
fails: list[str] = []

r = subprocess.run([sys.executable, str(ROOT / "scripts/embed_corpus.py"), "--check"],
                   capture_output=True, text=True)
if r.returncode:
    fails.append(r.stderr.strip() or "embedded corpus block is stale")

m = re.search(r"const CORPUS=(\{.*?\});\n/\*CORPUS:END\*/", html, re.S)
if not m:
    fails.append("CORPUS block not found in index.html")
else:
    c = json.loads(m.group(1))
    f = {k: i for i, k in enumerate(c["fields"])}
    days = c["days"]
    if [d[f["n"]] for d in days] != list(range(114, 0, -1)):
        fails.append("study order is not 114 -> 1")
    if [d[f["day"]] for d in days] != list(range(1, 115)):
        fails.append("day numbers are not 1..114")
    w = summary["whole_quran"]
    for key, want in [("words", w["orthographic_word_positions"]),
                      ("vocab", w["canonical_vocabulary_items"]),
                      ("roots", w["roots"]), ("verses", 6236)]:
        if c["meta"][key] != want:
            fails.append(f"meta.{key} = {c['meta'][key]}, expected {want}")
    if sum(d[f["tw"]] for d in days) != w["orthographic_word_positions"]:
        fails.append("per-day word totals do not add up to the whole Qur'an")
    if sum(d[f["nw"]] for d in days) != w["canonical_vocabulary_items"]:
        fails.append("new items per day do not add up to the vocabulary total")
    run = 0
    for d in days:
        run += d[f["nw"]]
        if d[f["cum"]] != run or d[f["nw"]] != len(d[f["items"]]) or d[f["d"]] != d[f["ca"]] + d[f["nw"]]:
            fails.append(f"day {d[f['day']]} (surah {d[f['n']]}) is internally inconsistent")
            break
    b = summary["baqarah_day_113"]
    baq = days[112]
    for key, want in [("n", 2), ("d", b["distinct_vocabulary_items"]),
                      ("nw", b["new_vocabulary_items"]), ("ca", b["carried_vocabulary_items"]),
                      ("cum", b["known_after_vocabulary_items"]), ("nr", b["new_roots"]),
                      ("pk", b["known_lexical_word_token_coverage_pct"])]:
        if baq[f[key]] != want:
            fails.append(f"Al-Baqarah {key} = {baq[f[key]]}, expected {want}")

for stale in ["77,430", "3,680", "1,685", "pending full verification", "working estimate"]:
    if stale in html:
        fails.append(f"stale figure or wording still on the page: {stale!r}")

if fails:
    print("FAIL\n- " + "\n- ".join(fails))
    sys.exit(1)
print("OK — app counts match the corpus calculation for all 114 days.")
