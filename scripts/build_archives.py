#!/usr/bin/env python3
"""Generate per-department .zip archives (store mode) into /archives for upload."""
import json
import os
import re
import subprocess

from paths import BOOKS_DIR, ARCH_DIR


def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()


def main():
    os.makedirs(ARCH_DIR, exist_ok=True)
    jobs = []
    for dept in sorted(os.listdir(BOOKS_DIR)):
        deptdir = os.path.join(BOOKS_DIR, dept)
        if not os.path.isdir(deptdir):
            continue
        pdfs = []
        for dirpath, _, files in os.walk(deptdir):
            for f in files:
                if f.lower().endswith(".pdf"):
                    pdfs.append(os.path.join(dirpath, f))
        if not pdfs:
            continue
        zipname = slug(dept) + ".zip"
        jobs.append({"dept": dept, "zip": zipname,
                     "zip_path": os.path.join(ARCH_DIR, zipname), "pdfs": len(pdfs)})

    json.dump(jobs, open(os.path.join(ARCH_DIR, "_archives_manifest.json"), "w"),
              indent=2, ensure_ascii=False)

    for j in jobs:
        if os.path.exists(j["zip_path"]):
            print("skip (exists):", j["zip"])
            continue
        print("building", j["zip"], f"({j['pdfs']} pdfs)...", flush=True)
        tmp = j["zip_path"] + ".part"
        subprocess.run(["zip", "-0", "-q", "-r", tmp, j["dept"]],
                       cwd=BOOKS_DIR, check=True)
        os.replace(tmp, j["zip_path"])
        print("  done", j["zip"], f"{os.path.getsize(j['zip_path']) / 1e9:.2f} GB")

    print("\n=== ALL ARCHIVES ===")
    for j in jobs:
        sz = os.path.getsize(j["zip_path"]) / 1e9 if os.path.exists(j["zip_path"]) else 0
        print(f"  {sz:6.2f} GB  {j['zip']}")


if __name__ == "__main__":
    main()