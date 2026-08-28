#!/usr/bin/env python3
"""Download Haque collection files from Internet Archive.

Examples:
  python download.py --department "Civil Technology"
  python download.py --department civil-technology
  python download.py --subject 25913        # download the Chemistry PDF(s) for code 25913
  python download.py --list                 # list departments and their item identifiers
"""
import argparse, csv, os, re, subprocess, sys

BASE = "https://archive.org/download"
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.csv")

def slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()

def load_manifest():
    if not os.path.exists(MANIFEST):
        sys.exit("manifest.csv not found next to this script")
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

def departments():
    rows = load_manifest()
    depts = []
    for r in rows:
        if r["department"] not in [d[0] for d in depts]:
            depts.append((r["department"], slug(r["department"])))
    return depts

def list_depts():
    for name, ident in departments():
        print(f"{ident:60s}  {name}")
    sys.exit(0)

def dl(url, out):
    print(f"Downloading {os.path.basename(out)} ...", flush=True)
    subprocess.run(["curl","-L","-C","-","-o",out,url], check=True)
    print("OK:", out)

def dl_department(name, outdir):
    rows = load_manifest()
    dept_rows = [r for r in rows if r["department"] == name]
    if not dept_rows:
        sys.exit(f"Unknown department: {name}")
    ident = slug(name)
    zipfile = dept_rows[0]["archive"]
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, zipfile)
    dl(f"{BASE}/{ident}/{ident}.zip", out)
    print(f"\nExtract with: unzip {out} -d {os.path.join(outdir, name)}")

def dl_subject(code, outdir):
    rows = load_manifest()
    hits = [r for r in rows if r["code"] == code]
    if not hits:
        sys.exit(f"No subject with code {code} in manifest")
    # group by archive; download whole archive for each dept that teaches it
    seen = set()
    for r in hits:
        dept = r["department"]
        if dept in seen:
            continue
        seen.add(dept)
    for r in hits:
        dl_department(r["department"], outdir)
        break
    print(f"\n{code} appears in {len(hits)} placements; downloaded the dept archive for '{hits[0]['department']}'.\n"
          "See manifest.csv for all placements, or pass --department to get a specific one.")

def main():
    ap = argparse.ArgumentParser(description="Download Haque collection from Internet Archive")
    ap.add_argument("--department", help="Department name or slug to download (whole zip)")
    ap.add_argument("--subject", help="BTEB subject code to locate/download")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--list", action="store_true", help="list departments + item identifiers")
    a = ap.parse_args()
    if a.list:
        list_depts()
    if a.department:
        dl_department(a.department, a.out)
    elif a.subject:
        dl_subject(a.subject, a.out)
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
