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

Each department has been packaged as a single `.zip` (no compression — the PDFs are already
compressed) and uploaded to Internet Archive.

## Internet Archive Items

Each of the 33 departments is one archive.org item. Replace `<ident>` with the item identifier
(see below) and download:

```bash
# Full department (whole zip)
curl -L -o <dept>.zip \
  "https://archive.org/download/<ident>/<ident>.zip"

# Or browse/extract only what you need
```

### Department → archive.org item identifiers

Each department zip is its own archive.org item named `haque-books-<department-slug>`.
Replace `<ident>` below with the item identifier from this table.

| # | Department | archive.org item | zip |
|---|---|---|---|
| 1 | Aircraft Maintenance Technology- Aerospace | `haque-books-aircraft-maintenance-technology-aerospace` | `aircraft-maintenance-technology-aerospace.zip` |
| 2 | Aircraft Maintenance Technology- Avionics | `haque-books-aircraft-maintenance-technology-avionics` | `aircraft-maintenance-technology-avionics.zip` |
| 3 | Architecture Technology | `haque-books-architecture-technology` | `architecture-technology.zip` |
| 4 | Automobile Technology | `haque-books-automobile-technology` | `automobile-technology.zip` |
| 5 | Cadastral,Topographic Survey & Land Information Technology | `haque-books-cadastral-topographic-survey-land-information-technology` | `cadastral-topographic-survey-land-information-technology.zip` |
| 6 | Ceramic Technology | `haque-books-ceramic-technology` | `ceramic-technology.zip` |
| 7 | Chemical Technology | `haque-books-chemical-technology` | `chemical-technology.zip` |
| 8 | Civil Technology | `haque-books-civil-technology` | `civil-technology.zip` |
| 9 | Civil(Wood) Technology | `haque-books-civil-wood-technology` | `civil-wood-technology.zip` |
| 10 | Computer Science & Technology | `haque-books-computer-science-technology` | `computer-science-technology.zip` |
| 11 | Construction Technology | `haque-books-construction-technology` | `construction-technology.zip` |
| 12 | Electrical Technology | `haque-books-electrical-technology` | `electrical-technology.zip` |
| 13 | Electromedical Technology | `haque-books-electromedical-technology` | `electromedical-technology.zip` |
| 14 | Electronics Technology | `haque-books-electronics-technology` | `electronics-technology.zip` |
| 15 | Environmental Technology | `haque-books-environmental-technology` | `environmental-technology.zip` |
| 16 | Food Technology | `haque-books-food-technology` | `food-technology.zip` |
| 17 | Footwear Technology | `haque-books-footwear-technology` | `footwear-technology.zip` |
| 18 | Geoinformatics Technology | `haque-books-geoinformatics-technology` | `geoinformatics-technology.zip` |
| 19 | Glass Technology | `haque-books-glass-technology` | `glass-technology.zip` |
| 20 | Graphic Design Technology | `haque-books-graphic-design-technology` | `graphic-design-technology.zip` |
| 21 | Land Resources Survey & Environment Technology | `haque-books-land-resources-survey-environment-technology` | `land-resources-survey-environment-technology.zip` |
| 22 | Marine Technology | `haque-books-marine-technology` | `marine-technology.zip` |
| 23 | Mechanical Technology | `haque-books-mechanical-technology` | `mechanical-technology.zip` |
| 24 | Mechatronics Technology | `haque-books-mechatronics-technology` | `mechatronics-technology.zip` |
| 25 | Petroleum and Mining Technology | `haque-books-petroleum-and-mining-technology` | `petroleum-and-mining-technology.zip` |
| 26 | Photogrammetry & Remote Sensing Technology | `haque-books-photogrammetry-remote-sensing-technology` | `photogrammetry-remote-sensing-technology.zip` |
| 27 | Power Technology | `haque-books-power-technology` | `power-technology.zip` |
| 28 | Printing Technology | `haque-books-printing-technology` | `printing-technology.zip` |
| 29 | RAC Technology | `haque-books-rac-technology` | `rac-technology.zip` |
| 30 | Shipbuilding Engineering | `haque-books-shipbuilding-engineering` | `shipbuilding-engineering.zip` |
| 31 | Surveying Technology | `haque-books-surveying-technology` | `surveying-technology.zip` |
| 32 | Telecommunication Technology | `haque-books-telecommunication-technology` | `telecommunication-technology.zip` |
| 33 | Tourism and Hospitality Management Technology | `haque-books-tourism-and-hospitality-management-technology` | `tourism-and-hospitality-management-technology.zip` |

*(The full per-book table, including every subject code and its department/semester, is in
`manifest.csv`.)*

## Files in this repo

- **`manifest.csv`** — every book placement: department, semester, BTEB subject code, subject,
  filename, size (MB), and which archive.zip it came from. **982 rows.**
- **`catalog_unique.csv`** — each unique subject/code with the list of departments that teach it.
- **`download.py`** — download a whole department from Internet Archive (or a single subject).

## Usage

### Option 1 — Download a whole department

See the Internet Archive item table above, then:

```bash
python download.py --department "Civil Technology"
```

or with curl against the item you want.

### Option 2 — Find a subject

```bash
# find which departments/semesters teach a subject code
grep ",25913," manifest.csv
```

### Option 3 — Extract / browse

Download the department zip and unzip:

```bash
unzip civil-technology.zip -d Civil-Technology
```

## How this was built

- Source: the **Poly eBook** Android app (`com.polybook.diploma`) backend API
  (`polyebook3.polyebook.com`) — the complete Haque catalog was recovered by decompiling the
  APK (jadx) and enumerating all books; free downloads.
- Course structure (department → semester → subject codes from `/home/sakib/Downloads/a.txt`)
  was used to place each Haque book into every department/semester that teaches it.
- Coverage of the wider "missing subjects" project: **57 of 556** missing BTEB subject entries
  are covered by this Haque collection.

## License / Note

These are official BTEB/Haque-published textbooks. Distributed for educational/archival purposes.
If you hold rights and want an item removed, open an issue.

---
*For the technical step-by-step method (APK decompile, API auth, WAF bypass), see the project
handoff: `HAQUE_PUBLICATIONS_PROJECT.md`.*
