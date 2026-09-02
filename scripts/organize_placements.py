#!/usr/bin/env python3
"""Copy each Haque book into every Department/Semester/Subject.pdf slot
defined by the authoritative BTEB structure (course_dept_sem.json).

Produces the 33-department Books/ tree (~982 placements).
"""
import json
import os
import re
import shutil

from paths import WORK_DIR, DEST_DIR, BOOKS_DIR


def norm(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def main():
    manifest = json.load(open(os.path.join(WORK_DIR, "haque_collection_manifest.json")))
    course = json.load(open(os.path.join(WORK_DIR, "course_dept_sem.json")))
    by_file = {r["filename"]: r for r in manifest}

    # map (dept, semester) -> normalized title -> file
    placed = 0
    skipped = 0
    for dept, sems in course.items():
        for sem, subs in sems.items():
            dept_dir = os.path.join(BOOKS_DIR, dept, f"Semester {sem}")
            os.makedirs(dept_dir, exist_ok=True)
            for s in subs:
                title = s["title"]
                # find a book whose filename embeds this subject's code
                code = s.get("code", "")
                match = None
                for r in manifest:
                    if r["code"] == code and os.path.exists(
                            os.path.join(DEST_DIR, r["filename"])):
                        match = r
                        break
                if match is None:
                    skipped += 1
                    continue
                src = os.path.join(DEST_DIR, match["filename"])
                dst = os.path.join(dept_dir, title + ".pdf")
                if os.path.exists(dst):
                    continue
                shutil.copy2(src, dst)
                placed += 1
            print("did dept", dept, "sem", sem)
    print("placed:", placed, "skipped:", skipped)


if __name__ == "__main__":
    main()