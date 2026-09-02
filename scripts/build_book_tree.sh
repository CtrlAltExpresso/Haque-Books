#!/usr/bin/env bash
# Build the lightweight, GitHub-browsable Books/ tree in publish_repo.
# Each subject becomes a small .md page with a direct archive.org download link.
set -euo pipefail
python3 "${HAQUE_SCRIPTS:-/path/to/scripts}/build_book_tree.py"