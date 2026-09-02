#!/usr/bin/env bash
# Upload each department's individual PDFs into its existing archive.org item,
# so every book gets a direct, clickable download URL:
#   https://archive.org/download/haque-books-<slug>/<Subject>.pdf
#
# Prereqs: pip install internetarchive && ia configure
#
# Usage:
#   ./upload_pdfs_to_items.sh                 # all departments
#   ./upload_pdfs_to_items.sh --only tourism  # one department (slug)
set -euo pipefail

BOOKS="${HAQUE_BOOKS:-/path/to/Haque/Books}"
ONLY=""
IDENT_PREFIX="haque-books"        # adjust to match your item naming

while [[ $# -gt 0 ]]; do
  case "$1" in
    --only) ONLY="$2"; shift 2;;
    *) echo "unknown: $1"; exit 1;;
  esac
done

if ! command -v ia >/dev/null 2>&1; then
  echo "installing internetarchive CLI..."; pip install -q internetarchive
fi

departments=()
mapfile -d '' departments < <(find "$BOOKS" -mindepth 1 -maxdepth 1 -type d -print0)

for dept_dir in "${departments[@]}"; do
  dept=$(basename "$dept_dir")
  slug=$(python3 -c "import re,sys;print(re.sub(r'[^A-Za-z0-9]+','-',sys.argv[1]).strip('-').lower())" "$dept")
  [[ -n "$ONLY" && "$slug" != "$ONLY" ]] && continue
  ident="${IDENT_PREFIX}-${slug}"
  echo "=== $dept -> $ident ==="

  mapfile -d '' pdfs < <(find "$dept_dir" -name '*.pdf' -print0 | sort -z)
  existing=$(ia list "$ident" 2>/dev/null | grep -E '\.pdf$' | sort || true)
  todo=()
  for p in "${pdfs[@]}"; do
    b="$(basename "$p")"
    grep -qxF "$b" <<<"$existing" || todo+=("$p")
  done
  echo "  already uploaded: $(( ${#pdfs[@]} - ${#todo[@]} )) / ${#pdfs[@]}"
  n=${#todo[@]}
  for ((k=0; k<n; k+=50)); do
    batch=("${todo[@]:k:50}")
    if [[ ${#batch[@]} -gt 0 ]] && ! ia upload "$ident" "${batch[@]}" --retries=5 --no-derive; then
      echo "WARN: partial failure in $dept (batch $((k/50)))"
    fi
  done
  echo "DONE: $dept (${#todo[@]} to upload this run)"
done
echo "ALL DONE."