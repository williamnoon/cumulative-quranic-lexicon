#!/usr/bin/env python3
"""Embed the verified corpus calculation into index.html.

The app is one self-contained file, so the per-day numbers it shows live in a
generated block between the CORPUS:BEGIN / CORPUS:END markers. This script is
the only thing that writes that block; never edit it by hand.

  python scripts/embed_corpus.py           # rewrite the block
  python scripts/embed_corpus.py --check   # fail if the block is stale
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "data/generated/cumulative-vocabulary.json"
NAMES = ROOT / "data/surahs.json"
HTML = ROOT / "index.html"
BEGIN, END = "/*CORPUS:BEGIN*/", "/*CORPUS:END*/"

# Order of fields in each compact day row. The app reads this list, so the
# names stay readable in the browser without shipping a 2 MB JSON file.
FIELDS = ["n", "day", "ar", "en", "v", "tw", "lex", "d", "ca", "nw", "cum",
          "pk", "rd", "nr", "rcum", "items"]


def build() -> str:
    data = json.loads(GEN.read_text(encoding="utf-8"))
    names = {r[0]: r for r in json.loads(NAMES.read_text(encoding="utf-8"))}
    rows = []
    for x in data["days"]:
        n = x["surah"]
        items = []
        for it in x["new_vocabulary_root_novelty_map"]:
            roots = it["roots"]
            items.append([it["lemma_arabic"],
                          "".join(r["arabic"] for r in roots[:1]),
                          1 if roots and roots[0]["root_is_new"] else 0])
        rows.append([n, x["day"], names[n][1], names[n][2], names[n][3],
                     x["orthographic_word_tokens"], x["lexical_word_tokens"],
                     x["distinct_vocabulary_items"], x["carried_vocabulary_items"],
                     x["new_vocabulary_items"], x["known_after_vocabulary_items"],
                     x["known_lexical_word_token_coverage_pct"],
                     x["distinct_roots"], x["new_roots"], x["known_after_roots"],
                     items])
    last = data["days"][-1]
    meta = {
        "source": data["metadata"]["source"]["name"],
        "words": data["metadata"]["orthographic_word_positions"],
        "vocab": last["known_after_vocabulary_items"],
        "roots": last["known_after_roots"],
        "verses": sum(r[3] for r in names.values()),
        "noLemma": data["metadata"]["stems_missing_lemma"],
    }
    body = json.dumps({"meta": meta, "fields": FIELDS, "days": rows},
                      ensure_ascii=False, separators=(",", ":"))
    return f"{BEGIN}\nconst CORPUS={body};\n{END}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    html = HTML.read_text(encoding="utf-8")
    i, j = html.find(BEGIN), html.find(END)
    if i < 0 or j < 0:
        print("index.html is missing the CORPUS markers", file=sys.stderr)
        return 1
    block = build()
    current = html[i:j + len(END)]
    if a.check:
        if current != block:
            print("Embedded corpus block is stale. Run: python scripts/embed_corpus.py",
                  file=sys.stderr)
            return 1
        print("Embedded corpus block matches data/generated.")
        return 0
    HTML.write_text(html[:i] + block + html[j + len(END):], encoding="utf-8")
    print(f"Embedded {len(block):,} bytes into index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
