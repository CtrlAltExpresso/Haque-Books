#!/usr/bin/env python3
"""Build the final Haque collection manifest (code, file, size, author, url).

Also emits a CSV. Adds any hand-added extra books (fillers) to the list.
"""
import json
import os
import re
import csv

from paths import WORK_DIR, DEST_DIR


def sanitize(name):
    return re.sub(r'[^\w\-\.]+', '_', name).strip('_')


def main():
    match = json.load(open(os.path.join(WORK_DIR, "match_result.json")))["matched"]
    extra = [   # hand-added fillers not present in the app catalog
        {"code": "26466", "name": "Innovation and Entrepreneurship",
         "author": "Haque Publication"},
        {"code": "29671", "name": "Multimedia and Animation",
         "author": "Haque Publication"},
    ]

    rows = []
    for m in match:
        mm, b = m["missing"], m["book"]
        code = mm.get("code")
        name = mm.get("name") or (b.get("name_clean") or "book")
        fname = (sanitize(f"{code}_{name}") if code and code != "No Code"
                 else sanitize(name)).rstrip('_') + ".pdf"
        rows.append({"code": code, "subject": name,
                     "entries": mm.get("entries"), "dept_count": mm.get("dept_count"),
                     "filename": fname, "author": b["author"], "url": b["post_file_url"]})
    for e in extra:
        rows.append({"code": e["code"], "subject": e["name"],
                     "entries": None, "dept_count": None,
                     "filename": sanitize(f"{e['code']}_{e['name']}") + ".pdf",
                     "author": e["author"], "url": None})

    for r in rows:
        p = os.path.join(DEST_DIR, r["filename"])
        r["size_bytes"] = os.path.getsize(p) if os.path.exists(p) else 0

    rows.sort(key=lambda r: -(r["dept_count"] or 0))

    with open(os.path.join(WORK_DIR, "haque_collection_manifest.json"), "w") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    with open(os.path.join(WORK_DIR, "haque_collection_manifest.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["code", "subject", "entries", "dept_count",
                    "author", "filename", "size_bytes", "source_url"])
        for r in rows:
            w.writerow([r["code"], r["subject"], r["entries"], r["dept_count"],
                        r["author"], r["filename"], r["size_bytes"], r["url"]])

    total = sum(r["size_bytes"] for r in rows)
    print("BOOKS:", len(rows))
    print("TOTAL GB: %.2f" % (total / 1e9))
    print("target author:", sum(1 for r in rows if r["author"] == "Haque Publication"))


if __name__ == "__main__":
    main()
