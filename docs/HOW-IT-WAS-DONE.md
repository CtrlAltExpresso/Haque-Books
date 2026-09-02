# How this collection was built

A behind-the-scenes write-up of how the complete Haque Publications BTEB polytechnic
textbook collection (Probidhan 2022) was recovered and published.

This is the **methodology** — not the books themselves (those live on Internet Archive,
see the repo `README.md`). The same pipeline is reusable for similar closed Android-app /
WAF-protected ebook catalogs.

---

## tl;dr

1. The target: the official **Poly eBook** Android app (`com.polybook.diploma`), which
   hosts the Haque Publications textbooks.
2. The app's backend API and its PDF host are behind **Imunify360 bot-protection**
   (a JavaScript challenge + headless-browser detection) — plain `curl`/`requests` fail.
3. We **decompiled the APK**, recovered the Retrofit API endpoints and the auth scheme,
   then drove the API from inside a real headless browser to **pass the WAF**.
4. We enumerated the entire catalog, matched every book to its BTEB subject code /
   department / semester, downloaded all the PDFs, and published them.
5. Because the collection is ~103 GB (too large for GitHub), we hosted the PDFs on
   **Internet Archive** and keep only catalog metadata + direct links in this repo.

---

## 1. Reconnaissance

### 1.1 The goal

- BTEB (Bangladesh Technical Education Board) diploma textbooks exist under several
  publishers. The official physical prints are published by **Haque Publications**.
- The **Poly eBook** Android app claims to carry the full set. We wanted the Haque
  editions specifically (**Probidhan 2022** — note the 5-digit subject codes, e.g.
  `26843`; older editions used 4-digit codes like `6843`).
- We already had the authoritative department → semester → subject structure in the file
  `a.txt` (the BTEB 2022 course structure, 33 departments, ~1,700 subject entries).
  This was the ground truth used later for placement.

### 1.2 Obtain the APK

The current APK (`.xapk`) was fetched from the official site/app store. A `.xapk` is just
a zip containing the base APK plus split packs.

## 2. Reverse-engineering the APK

We used [`jadx`](https://github.com/skylot/jadx) to decompile the APK to Java source:

```bash
jadx -d out/ com.polybook...apk
```

From the decompiled sources we looked at the networking layer and found:

- The app is built with **Retrofit** (`ApiClient.java` / `ApiInterface.java`).
- Base URL: `https://polyebook3.polyebook.com/api/v1/`.
- PDF host: `https://ebook.projectbd.com/`.

### 2.1 API auth scheme

Every endpoint is an HTTP `POST` with a single form field `data` whose value is:

```
data = base64( JSON )
```

where the JSON looks like:

```json
{
  "package_name": "com.polybook.diploma",
  "salt": "<an integer salt>",
  "sign": "<md5 hex>",
  ...endpoint-specific fields...
}
```

The `sign` is simply:

```
sign = md5hex( "viaviweb" + String(salt) )
```

Any endpoint that needs paging takes a `?page=N` query param. The whole API is trivial —
the only real obstacle is the WAF in front of it.

## 3. Beating the WAF (Imunify360)

The API and the PDF host are protected by **Imunify360** bot protection:

- It serves a JavaScript challenge and detects headless browsers.
- A naive `urllib`/`requests` client gets a "please wait / one moment" block page.
- The magic unlock is a **`wssplashchk` cookie** issued after the challenge runs.
  Once present, it stays valid across URLs on that host — so we only need to solve it
  once per session and reuse the cookie for the whole batch.

We solved it with **Playwright** (headless Chrome) + **playwright-stealth**:

- Use the **full Chromium**, not the minimal headless-shell build.
- Create a normal-looking browser context (realistic UA, locale, viewport).
- Apply `playwright-stealth` to reduce automation fingerprints.
- `page.goto(...)` the base URL once and wait ~6–8 seconds for the challenge; the
  `wssplashchk` cookie is then present in the context.
- Run the actual API calls **from inside the page** via the page's `fetch()` — this makes
  the requests originate from the same authenticated browser session.

Key snippet:

```python
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True,
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"])
    ctx = await browser.new_context(
        user_agent="Mozilla/5.0 ... Chrome/124 ...",
        viewport={"width":1366, "height":768}, accept_downloads=True)
    await Stealth().apply_stealth_async(ctx)
    page = await ctx.new_page()
    await page.goto(BASE + "category", wait_until="domcontentloaded")
    await page.wait_for_timeout(7000)
    # cookie wssplashchk is now set; subsequent fetch() calls from this page work
```

For **downloading** PDFs, `page.goto(pdf_url)` triggers the challenge → wait ~8 s →
`page.goto(pdf_url)` again inside `page.expect_download(...)` → `download.save_as(...)`.

## 4. Enumerating the catalog

The endpoints we used:

| Endpoint | Purpose |
|---|---|
| `category` | top-level categories |
| `subcategory` (`cat_id=`) | subcategories within a category |
| `books_by_cat` (`cat_id=`) | books at category level (paged) |
| `books_by_sub_cat` (`sub_cat_id=`) | books within a subcategory (paged) |
| `books_details` (`book_id=`) | full detail incl. the PDF URL `post_file_url` |
| `search_book` (`search_text=`) | text search against titles/descriptions |

The full crawl (all 33 categories and their subcategories, paged) yielded **581 books**.
Every one got a unique `post_id`; we de-duplicated and stored them in
`catalog_all_books.json`, then fetched per-book details into `book_details.json`.

## 5. Filtering to Haque + matching to BTEB codes

### 5.1 Keep only Haque

The catalog has several publishers. We kept books whose author is **Haque Publication**,
then extracted the 5-digit BTEB code from each title (titles embed the code in brackets,
e.g. `[26841]`). This collapsed the 364 Haque catalog entries to **133 unique Haque PDFs**
(the same book appears in multiple departments/semesters).

### 5.2 Match against the official structure

For every missing subject in the BTEB structure we did:

- **Exact code match** (`match_targets.py`) — the same 5-digit code exists in the catalog.
- **Fuzzy title match** (`fuzzy_match.py`) — using RapidFuzz `token_set_ratio` against a
  searchable title index, for subjects where the code wasn't a clean hit.

The result was a manifest mapping every Haque book to its code, name, filename and
**all** departments/semesters that teach it (from `a.txt` / `course_dept_sem.json`).

## 6. Downloading (resumable)

Downloads were batched with a resumable state file. For each job:

1. Check if already done (state + on-disk PDF + `%PDF` magic + size).
2. Solve the WAF once, then for each URL: `goto` → `expect_download` → `save_as`.
3. Verify the file is a real PDF (`%PDF-` header, size > 1 KB).
4. Record success/failure in state so a crash restarts cleanly.

The collection ended at **136 PDFs / 13.78 GB** (133 unique Haque + 3 technical fillers
used for a few code gaps).

## 7. Organizing into departments / semesters

Using the authoritative `course_dept_sem.json` (derived from `a.txt`), each book was
copied into **every** `Department/Semester N/Subject.pdf` slot where its subject code
appears in the course structure:

```
<Department>/
  Semester 1/
    Bangla-I.pdf
    English-I.pdf
    ...
```

This produced **33 departments × semesters = 982 placements (~103 GB)** in a
`Books/` mirror of the FreeMax layout.

## 8. Publishing

### 8.1 Why split hosting

~103 GB is far too large for GitHub. Solution:

- **Internet Archive** hosts the actual PDFs.
- **GitHub** hosts only catalogs + direct links.

### 8.2 Internet Archive

1. Install the `internetarchive` CLI and authenticate: `pip install internetarchive && ia configure`.
2. Build one archive per department (store-mode zip): `build_archives.py`.
3. Upload each department archive to its own item `haque-books-<department-slug>`:
   `upload_archiveorg.sh`.
4. Then upload each department's **individual PDFs** flat (basename) into that same item so
   every book gets a direct, clickable URL:
   `https://archive.org/download/haque-books-<slug>/<Subject>.pdf`
   → `upload_pdfs_to_items.sh` (batched, resumable, `--no-derive`).
5. Once all PDFs of a department are present, delete the whole-department zip from the item
   to avoid duplication: `delete_zips_when_done.sh` (only removes when every PDF is verified
   present, so nothing is lost).

### 8.3 GitHub

Because each PDF now has a stable direct URL, we could build a **lightweight browsable tree**
of `.md` pages (one per subject) instead of uploading 103 GB. `build_book_tree.py`
regenerates the `Books/` tree where every subject is a small markdown page with:

- subject code, department, semester, filename, size
- a **one-click "Download this book"** link straight to the PDF on archive.org
- short "how to save it as a file" instructions (with an animated GIF)

The manifests (`manifest.csv` = 982 placements, `catalog_unique.csv` = unique subjects) and
a small `download.py` tool complete the repo. `publish_github.sh` creates the repo and
pushes only this metadata.

## 9. Repo layout (what you're looking at)

```
docs/HOW-IT-WAS-DONE.md   <- this file
scripts/                  <- sanitized, generalized copies of the pipeline scripts
Books/                    <- Browse the collection (one .md per subject, with download link)
manifest.csv              <- every book placement: dept, semester, code, subject, file, size
catalog_unique.csv        <- unique subjects + which departments teach them
download.py               <- download a whole department or a single subject from archive.org
assets/save-mobile.gif    <- "how to save on mobile" helper animation
```

## 10. Honest limits / what's NOT included

- **2 Haque 2022-Probidhan books are not freely available anywhere** (`26843` Networks,
  Filters & Transmission Lines; `26844` Electronic Servicing). They are confirmed **not** in
  the Poly eBook app (re-verified by a fresh full-catalog re-query in 2026 that returned
  exactly 581 books, 0 new/0 removed, and zero title/description hits for those codes) and
  not on the free web. Only physical print copies exist. This collection therefore covers
  **980 / 982** of the Haque placements.
- This recovered the **Poly eBook / Haque** catalog, which is separate from the Softmax
  publisher's pass books. Those are a different body of work, kept out of this repo.

## 11. Ethics & caution notes

- Run discovery at **low rate limits** with delays between calls; the scripts back off and
  re-solve the WAF on 429/403 rather than hammering the server.
- This project involved **bypassing a bot-protection WAF**. Use such techniques only for
  content you are permitted to access, on infrastructure you are allowed to query, and at
  a respectful rate. The goal here was public archival of official public textbooks.
- The `.md` book pages' download links point at **Internet Archive**, not at the original
  host, so normal visitors never hit the WAF.

---

*Companion material: see the `scripts/` folder for the generalized pipeline scripts and a
step-by-step run order.*
