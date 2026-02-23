"""Stream PPA pages JSONL (plain or gzip) filtered by work_id."""

import gzip
import json
from pathlib import Path


def iter_pages_for_work(corpus_path: str, work_id: str):
    """
    Yield page dicts for the given work_id. Streams line-by-line; does not load
    the full corpus. Supports .jsonl and .jsonl.gz.
    """
    corpus_path = Path(corpus_path)
    work_id_str = str(work_id).strip()

    if corpus_path.suffix == ".gz" or str(corpus_path).endswith(".gz"):
        opener = lambda: gzip.open(corpus_path, mode="rt", encoding="utf-8")
    else:
        opener = lambda: corpus_path.open(encoding="utf-8")

    with opener() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                page = json.loads(line)
            except json.JSONDecodeError:
                continue
            if str(page.get("work_id", "")).strip() != work_id_str:
                continue
            yield page
