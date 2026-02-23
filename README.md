# PPA Text–Image Alignment Pipeline

Reusable data alignment pipeline for the Princeton PPA (Prosody of the English Verse) dataset: align page-level full-text with page-level images (HathiTrust, Gale) and output a clean, structured dataset for publication.

## Phase 1: Text Integrity Checking

A script that verifies text integrity for a single work: page count, continuous order, no duplicate orders, no empty text. It streams the pages JSONL (or gzipped JSONL) and does **not** load the full corpus into memory.

### Data inputs

- **Metadata CSV**: `ppa_metadata.csv` or `refined_ppa_metadata.csv` — columns include `work_id`, `page_count`, `source` (HathiTrust, Gale/ECCO, EEBO-TCP). UTF-8.
- **Pages**: `ppa_pages.jsonl` or `ppa_pages.jsonl.gz` — one JSON object per line with `id`, `order`, `text`, `work_id`.

### Run the checker

From the repo root:

```bash
python scripts/check_text_integrity.py \
  --metadata /path/to/ppa_metadata.csv \
  --corpus /path/to/ppa_pages.jsonl.gz \
  --work-id A01224
```

Options:

- `--metadata` (required): path to metadata CSV
- `--corpus` (required): path to pages JSONL or `.jsonl.gz`
- `--work-id` (required): PPA work identifier
- `--format` `text` | `json`: output format (default: `text`)

Exit codes: `0` = all checks passed; `1` = one or more checks failed; `2` = missing work or file error.

### Checks performed

1. **Page count**: number of pages for the work matches metadata `page_count`
2. **Continuous order**: `order` values are 1-based consecutive (1, 2, …, N) with no gaps
3. **No duplicate orders**: each `order` appears at most once
4. **No empty text**: every page has non-empty `text` (after stripping whitespace)

### Project layout

```
ppa-text-image-alignment/
├── src/
│   ├── metadata.py   # load CSV, get work by work_id
│   ├── corpus.py     # stream JSONL/.gz pages for one work_id
│   ├── checks.py     # four integrity checks
│   └── report.py     # build and format report (text/JSON)
├── scripts/
│   └── check_text_integrity.py
├── requirements.txt
└── README.md
```

Alignment (text–image matching) is not implemented in Phase 1.
