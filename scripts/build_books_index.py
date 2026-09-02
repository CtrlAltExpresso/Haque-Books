#!/usr/bin/env python3
"""Build a flat list of every downloaded book (book_details + catalog).

Extracts the 5-digit BTEB code and a clean title from each book title.
Filters the catalog down to the target publisher (Haque Publication).
"""
import json
import os
import re

from paths import WORK_DIR


def extract_code(title):
    if not title:
        return None
    m = re.search(r'\[(\d{5})\]', title)
    if m:
        return m.group(1)
    m = re.search(r'\b(\d{5})\b', title)
    return m.group(1) if m else None


def extract_name(title):
    if not title:
        return title
    t = re.sub(r'\s*\[\d{5}\]\s*', '', title)
    t = re.sub(r'\s*\d{5}\s*$', '', t)
    t = re.sub(r'\(\S*\)', '', t)          # strip (Haque)/(Technical) markers
    return t.strip().strip('-').strip()


TARGET_AUTHOR = "Haque Publication"


def main():
    details = json.load(open(os.path.join(WORK_DIR, "book_details.json")))
    catalog = {str(b["post_id"]): b for b in
               json.load(open(os.path.join(WORK_DIR, "catalog_all_books.json")))}

    rows = []
    for pid, v in details.items():
        if not v:
            continue
        cat = catalog.get(pid, {})
        authors = cat.get("author_list") or []
        author = authors[0].get("author_name") if authors else ""
        title = v.get("post_title", "")
        rows.append({
            "post_id": pid,
            "code": extract_code(title),
            "title": title,
            "name_clean": extract_name(title),
            "author": author,
            "post_file_url": v.get("post_file_url"),
            "post_image": v.get("post_image"),
            "download_enable": v.get("download_enable"),
            "post_access": v.get("post_access"),
        })

    json.dump(rows, open(os.path.join(WORK_DIR, "books_extracted.json"), "w"),
              ensure_ascii=False, indent=2)
    print("total rows:", len(rows))
    print("with code:", sum(1 for r in rows if r["code"]))
    print("target author:", sum(1 for r in rows if r["author"] == TARGET_AUTHOR))


if __name__ == "__main__":
    main()
