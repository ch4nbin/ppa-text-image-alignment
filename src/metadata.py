"""Load and query PPA metadata CSV."""

import csv
from pathlib import Path


def load_metadata(path: str) -> list[dict]:
    """Load metadata CSV; return list of row dicts. Cast page_count to int."""
    path = Path(path)
    rows = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "page_count" in row and row["page_count"].strip():
                try:
                    row["page_count"] = int(row["page_count"])
                except ValueError:
                    row["page_count"] = row["page_count"]  # leave as str if not int
            rows.append(row)
    return rows


def get_work(metadata: list[dict], work_id: str) -> dict | None:
    """Return the single row for work_id, or None if not found."""
    work_id_str = str(work_id).strip()
    for row in metadata:
        if str(row.get("work_id", "")).strip() == work_id_str:
            return row
    return None
