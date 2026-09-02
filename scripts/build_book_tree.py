#!/usr/bin/env python3
"""Build a lightweight, GitHub-browsable Books/ tree in publish_repo.

Mirrors the real layout (<Department>/<Semester N>/<Subject>.pdf) but, because
the PDFs are ~103 GB (too large for GitHub), each subject becomes a small .md
placeholder with metadata + a direct download link from the matching
archive.org item.
"""
import csv
import os
import re
import urllib.parse

from paths import REPO_DIR

MANIFEST = os.path.join(REPO_DIR, "manifest.csv")
BOOKS = os.path.join(REPO_DIR, "Books")
BASE = "https://archive.org/download"


def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def main():
    rows = list(csv.DictReader(open(MANIFEST, encoding="utf-8")))
    by_dept = {}
    for r in rows:
        by_dept.setdefault(r["department"], []).append(r)

    total = 0
    for dept in sorted(by_dept, key=lambda d: d.upper()):
        dept_dir = os.path.join(BOOKS, dept)
        os.makedirs(dept_dir, exist_ok=True)

        sems = {}
        for r in by_dept[dept]:
            sems.setdefault(int(r["semester"]), []).append(r)

        for sem in sorted(sems):
            sem_dir = os.path.join(dept_dir, f"Semester {sem}")
            os.makedirs(sem_dir, exist_ok=True)
            for r in sorted(sems[sem], key=lambda x: (x["code"], x["subject"])):
                node = os.path.join(sem_dir, r["subject"] + ".md")
                pdf_url = (f"{BASE}/haque-books-{slug(r['department'])}/"
                           f"{urllib.parse.quote(r['filename'])}")
                content = (
                    f"# {r['subject']}\n\n"
                    f"[Download this book (PDF, {r['size_mb']} MB)]({pdf_url})\n\n"
                    f"| | |\n|---|---|\n"
                    f"| **Subject code** | `{r['code']}` |\n"
                    f"| **Department** | {r['department']} |\n"
                    f"| **Semester** | {r['semester']} |\n"
                    f"| **File** | `{r['filename']}` |\n"
                    f"| **Size** | {r['size_mb']} MB |\n\n"
                    f"Click downloads this book's PDF ({r['filename']}) directly.\n"
                )
                with open(node, "w", encoding="utf-8") as fh:
                    fh.write(content)
                total += 1

    print(f"Wrote {total} subject placeholders under {BOOKS}")


if __name__ == "__main__":
    main()