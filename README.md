# Haque Publications — BTEB Polytechnic Textbook Collection (Probidhan 2022)

A complete, standalone collection of **Haque Publications** BTEB polytechnic diploma textbooks
(Probidhan 2022), organized by department and semester. This is a SEPARATE collection from
Softmax/FreeMax — these are Haque-authored books, not Softmax pass books.

**Important:** The actual PDF files are **too large for GitHub** (~103 GB).
They are hosted on **Internet Archive**. This repository provides the catalog, links, and a
download tool — it does not host the PDFs directly.

## Contents

| Item | Detail |
|---|---|
| Departments | **33** |
| Book placements (dept × semester) | **982** |
| Unique subjects | **122** (with BTEB codes) |
| Unique Haque books | **136 PDFs** (133 Haque + 3 technical fillers) |
| Total size | **~103 GB** |

## Structure

The collection mirrors the FreeMax layout:

```
<Department>/
  Semester 1/
    Bangla-I.pdf
    English-I.pdf
    ...
  Semester 2/
    ...
```

Each department is one archive.org item (`haque-books-<department-slug>`), and every book's PDF is
uploaded to that item as a standalone file — so each book has its own direct download link.

### `Books/` tree — browse like FreeMax

The real PDFs are ~103 GB, too large for GitHub, so the `Books/` folder here is a
**lightweight mirror of the FreeMax tree** — same `Department → Semester → Subject` layout,
but every subject is a tiny `.md` page (code, size, archive.org source) with a direct
download link. Browse the tree on GitHub exactly like the FreeMax repo:

```
Books/
├── Civil Technology/
│   ├── Semester 1/
│   │   ├── Engineering Drawing.md
│   │   ├── Bangla-I.md
│   │   └── ...
│   ├── Semester 2/
│   │   └── ...
└── Computer Science & Technology/
    ├── Semester 1/
    └── ...
```

Every `.md` page has a **one-click "Download this book" button** that starts downloading just that
book's PDF directly from Internet Archive — no zip extraction needed.

## Internet Archive Items

Each of the 33 departments is one archive.org item (`haque-books-<department-slug>`). Every book
PDF is stored in its department's item, so catalogues/links below point straight at each book.

### Department → archive.org item identifiers

| # | Department | archive.org item |
|---|---|---|
| 1 | Aircraft Maintenance Technology- Aerospace | `haque-books-aircraft-maintenance-technology-aerospace` |
| 2 | Aircraft Maintenance Technology- Avionics | `haque-books-aircraft-maintenance-technology-avionics` |
| 3 | Architecture Technology | `haque-books-architecture-technology` |
| 4 | Automobile Technology | `haque-books-automobile-technology` |
| 5 | Cadastral,Topographic Survey & Land Information Technology | `haque-books-cadastral-topographic-survey-land-information-technology` |
| 6 | Ceramic Technology | `haque-books-ceramic-technology` |
| 7 | Chemical Technology | `haque-books-chemical-technology` |
| 8 | Civil Technology | `haque-books-civil-technology` |
| 9 | Civil(Wood) Technology | `haque-books-civil-wood-technology` |
| 10 | Computer Science & Technology | `haque-books-computer-science-technology` |
| 11 | Construction Technology | `haque-books-construction-technology` |
| 12 | Electrical Technology | `haque-books-electrical-technology` |
| 13 | Electromedical Technology | `haque-books-electromedical-technology` |
| 14 | Electronics Technology | `haque-books-electronics-technology` |
| 15 | Environmental Technology | `haque-books-environmental-technology` |
| 16 | Food Technology | `haque-books-food-technology` |
| 17 | Footwear Technology | `haque-books-footwear-technology` |
| 18 | Geoinformatics Technology | `haque-books-geoinformatics-technology` |
| 19 | Glass Technology | `haque-books-glass-technology` |
| 20 | Graphic Design Technology | `haque-books-graphic-design-technology` |
| 21 | Land Resources Survey & Environment Technology | `haque-books-land-resources-survey-environment-technology` |
| 22 | Marine Technology | `haque-books-marine-technology` |
| 23 | Mechanical Technology | `haque-books-mechanical-technology` |
| 24 | Mechatronics Technology | `haque-books-mechatronics-technology` |
| 25 | Petroleum and Mining Technology | `haque-books-petroleum-and-mining-technology` |
| 26 | Photogrammetry & Remote Sensing Technology | `haque-books-photogrammetry-remote-sensing-technology` |
| 27 | Power Technology | `haque-books-power-technology` |
| 28 | Printing Technology | `haque-books-printing-technology` |
| 29 | RAC Technology | `haque-books-rac-technology` |
| 30 | Shipbuilding Engineering | `haque-books-shipbuilding-engineering` |
| 31 | Surveying Technology | `haque-books-surveying-technology` |
| 32 | Telecommunication Technology | `haque-books-telecommunication-technology` |
| 33 | Tourism and Hospitality Management Technology | `haque-books-tourism-and-hospitality-management-technology` |

*(The full per-book table, including every subject code and its department/semester, is in
`manifest.csv`.)*

## Files in this repo

- **`Books/`** — browsable `Department/Semester/Subject` tree (mirrors FreeMax) — each
  subject is a `.md` page linking to its archive.org download. **982 pages.**
- **`manifest.csv`** — every book placement: department, semester, BTEB subject code, subject,
  filename, size (MB), and which archive.zip it came from. **982 rows.**
- **`catalog_unique.csv`** — each unique subject/code with the list of departments that teach it.
- **`download.py`** — download a whole department from Internet Archive (or a single subject).
- **`docs/HOW-IT-WAS-DONE.md`** — the full public methodology write-up.
- **`scripts/`** — generalized copies of all pipeline scripts.

## Usage

### Option 1 — Browse & download a single book

Use the `Books/` tree: open any subject page and click **"Download this book"** — the PDF downloads
straight from Internet Archive.

### Option 2 — Find a subject

```bash
# find which departments/semesters teach a subject code
grep ",25913," manifest.csv
```

## How this was built

- Source: the **Poly eBook** Android app (`com.polybook.diploma`) backend API
  (`polyebook3.polyebook.com`) — the complete Haque catalog was recovered by decompiling the
  APK (jadx) and enumerating all books; free downloads.
- Course structure (department → semester → subject codes from the BTEB 2022 plan) was used
  to place each Haque book into every department/semester that teaches it.
- Coverage of the wider "missing subjects" project: **57 of 556** missing BTEB subject entries
  are covered by this Haque collection.

### Read more

- **[`docs/HOW-IT-WAS-DONE.md`](docs/HOW-IT-WAS-DONE.md)** — a full, public walkthrough of the
  methodology: APK reverse-engineering, the API auth scheme, the Imunify360 (WAF) bypass with
  Playwright, catalog enumeration, matching, downloading, and publishing to archive.org/GitHub.
- **[`scripts/`](scripts/README.md)** — generalized, sanitized copies of every pipeline script,
  plus the run order and per-script explanation.

## License / Note

These are official BTEB/Haque-published textbooks. Distributed for educational/archival purposes.
If you hold rights and want an item removed, open an issue.

---
*For the technical step-by-step method (APK decompile, API auth, WAF bypass), see the project
handoff: `HAQUE_PUBLICATIONS_PROJECT.md`.*
