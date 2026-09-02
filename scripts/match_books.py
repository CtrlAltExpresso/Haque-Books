#!/usr/bin/env python3
"""Match every missing BTEB subject to a Poly eBook book.

Two-pass:
  1. exact 5-digit code match
  2. fuzzy title match (RapidFuzz) for the rest

Outputs match_result.json with matched / unmatched.
"""
import json
import os
import re
import unicodedata

from rapidfuzz import fuzz, process

from paths import WORK_DIR, SRC_DIR


def norm(s):
    if not s:
        return ""
    s = unicodedata.normalize('NFKD', s)
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return s.strip()


def main():
    missing = json.load(open(os.path.join(SRC_DIR, "missing_subjects_by_code.json")))
    rows = json.load(open(os.path.join(WORK_DIR, "books_extracted.json")))

    # index books by code, preferring the target author
    target = "Haque Publication"
    by_code = {}
    for r in rows:
        c = r["code"]
        if not c:
            continue
        cur = by_code.get(c)
        if cur is None or (cur["author"] != target and r["author"] == target):
            by_code[c] = r

    matched = []
    unmatched = []
    for m in missing:
        code = m.get("code")
        if code and code in by_code:
            matched.append({"missing": m, "book": by_code[code]})
        else:
            unmatched.append(m)

    # --- fuzzy pass on the remainder --------------------------------
    matched_codes = {m["missing"].get("code") for m in matched}
    unmatched_left = [u for u in unmatched if u.get("code") not in matched_codes]
    pool = [r for r in rows
            if r["author"] == target and r["post_file_url"]
            and r["post_id"] not in {m["book"]["post_id"] for m in matched}]
    by_norm = {norm(r["title"]): r for r in pool}
    choices = list(by_norm.keys())

    fuzzy_hits = []
    for u in unmatched_left:
        q = norm(u.get("name", ""))
        if not q:
            continue
        res = process.extract(q, choices, scorer=fuzz.token_set_ratio, limit=1)
        for choice, score, _ in res:
            if score >= 80:
                fuzzy_hits.append({"missing": u, "book": by_norm[choice], "score": score})
    fuzzy_hits.sort(key=lambda c: -c["score"])
    json.dump(fuzzy_hits, open(os.path.join(WORK_DIR, "fuzzy_candidates.json"), "w"),
              ensure_ascii=False, indent=2)

    print("Missing subjects:", len(missing))
    print("Matched by code:", len(matched))
    print("Fuzzy candidates (score>=80):", len(fuzzy_hits))
    print("Still unmatched:", len(unmatched_left))

    json.dump({"matched": matched, "unmatched": unmatched},
              open(os.path.join(WORK_DIR, "match_result.json"), "w"),
              ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
