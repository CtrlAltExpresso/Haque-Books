#!/usr/bin/env bash
# Create + populate the small GitHub repo for the collection.
# ONLY metadata is pushed (README, manifests, download tool).
# The ~103 GB PDFs live on Internet Archive, not in this repo.
#
# Prereqs: gh authenticated
#
# Usage:
#   ./publish_github.sh [--repo OWNER/REPO] [--public]
set -euo pipefail

REPO="YOUR_USER/REPO"
VISIBILITY="private"
REPO_DIR="${HAQUE_REPO:-/path/to/Haque/publish_repo}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2;;
    --public) VISIBILITY="public"; shift;;
    *) echo "unknown: $1"; exit 1;;
  esac
done

cd "$REPO_DIR"

if [ ! -d .git ]; then git init -q; fi
git add -A

if ! gh repo view "$REPO" >/dev/null 2>&1; then
  gh repo create "$REPO" --"$VISIBILITY" \
    --description "BTEB polytechnic textbook collection (Probidhan 2022) - catalog + links to Internet Archive hosting" \
    >/dev/null
fi
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$REPO.git"

git commit -q -m "BTEB textbook collection - catalog + archive.org links" || echo "nothing to commit"
git branch -M main
git push -u origin main

echo "Pushed to https://github.com/$REPO"