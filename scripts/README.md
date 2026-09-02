# Scripts — the pipeline, in run order

Generalized, dependency-light copies of the exact scripts used to build this
collection. Hardcoded host paths from the originals have been replaced with a
single config file (`paths.py`) and a couple of env vars.

> **Note:** The full end-to-end method is explained in
> [`docs/HOW-IT-WAS-DONE.md`](../docs/HOW-IT-WAS-DONE.md). These scripts are the
> concrete implementation of that write-up.

## Setup

```bash
pip install playwright  playwright-stealth  rapidfuzz
python -m playwright install chromium
# for the publishing half:
pip install internetarchive && ia configure
```

### Network/API config

- `waf_client.py` — the one place with the WAF-bypass plumbing
  (Imunify360 challenge solve + in-page `fetch`). Point `BASE` at the API base URL.
- Each API-calling script declares its own `SALT` constant — set these to the
  salt integer you recover from the app. `sign = md5("viaviweb" + salt)`.

### Filesystem config

`paths.py` centralizes the host paths (`BASE_DIR`, `WORK_DIR`, `DEST_DIR`,
`BOOKS_DIR`, `ARCH_DIR`, `REPO_DIR`, `SRC_DIR`). Override with the
`HAQUE_BASE` env var, or edit directly.

## Pipeline order

| Step | Script | Output |
|---|---|---|
| 1. Parse the authoritative BTEB structure | `../work/parse_a_txt.py` | `a_txt_parsed.json`, `course_dept_sem.json` |
| 2. Enumerate the app catalog | `enumerate_catalog.py` | `catalog_checkpoint.json` |
| 3. Full catalog crawl (resumable) | `crawl_catalog.py` | `catalog_all_books.json` |
| 4. Fetch per-book details (PDF URLs) | `fetch_details.py` | `book_details.json` |
| 5. Build book index (code/author extraction) | `build_books_index.py` | `books_extracted.json` |
| 6. Match subjects → books | `match_books.py` | `match_result.json`, `fuzzy_candidates.json` |
| 7. Download the PDFs (resumable) | `download_haque.py` | `master/` + state |
| 8. Final manifest (code/file/size/url) | `build_collection_manifest.py` | `haque_collection_manifest.json/.csv` |
| 9. Organize into dept/sem tree | `organize_placements.py` | `Books/<Dept>/<Sem N>/<Subject>.pdf` |
| 10. Build per-dept zips (for archive.org) | `build_archives.py` | `archives/*.zip` |
| 11. Upload individual PDFs to archive.org | `upload_pdfs_to_items.sh` | items `<prefix>-<slug>` |
| 12. Build browsable Books/ tree of .md links | `build_book_tree.py` | `publish_repo/Books/**/*.md` |
| 13. Create + push the GitHub repo | `publish_github.sh` | the repo |

## Per-script detail

- **`paths.py`** — single source of truth for paths.
- **`waf_client.py`** — `solve_challenge()` clears the Imunify360 JS challenge
  (leaves a `wssplashchk` cookie); `api_post()` runs a request from inside the page
  and re-solves on 429/403/block-page.
- **`enumerate_catalog.py`** — walks every category + subcategory, paged, into a
  checkpoint file.
- **`crawl_catalog.py`** — handles WAF re-solve mid-crawl and is resumable; stops at
  a `MAX_BOOKS` cap.
- **`fetch_details.py`** — hits `books_details` per id to get the real
  `post_file_url`; resumable.
- **`build_books_index.py`** — extracts the 5-digit BTEB code and a clean title from
  each title; keeps books by the target author.
- **`match_books.py`** — exact code match first, then RapidFuzz token-set title match.
- **`download_haque.py`** — solves the challenge once, then
  `goto → expect_download → save_as` per URL; checks the `%PDF` magic byte; writes a
  resumable state file.
- **`build_collection_manifest.py`** — final manifest with sizes + a CSV; allows
  hand-added filler rows.
- **`organize_placements.py`** — copies each book into every dept/semester slot where
  its subject code appears in the course structure.
- **`build_archives.py`** — store-mode (`zip -0`) per-department archives for the
  initial archive.org upload.
- **`upload_pdfs_to_items.sh`** — uploads each department's PDFs flat (basename) into
  its archive.org item, batched/resumable, `--no-derive`.
- **`build_book_tree.py`** — regenerates the `.md` subject pages with direct
  archive.org download links.
- **`publish_github.sh`** — creates the repo and pushes only metadata (never the PDFs).