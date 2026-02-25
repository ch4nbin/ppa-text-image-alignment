#!/usr/bin/env python3
"""
Minimal alignment prototype: clean HathiTrust cases only.

Text page i ↔ image i (no offset). Lists .jp2 names inside ZIP; does not extract.
"""

import argparse
import sys
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.corpus import iter_pages_for_work


def htid_to_pairtree(htid: str) -> str:
    """Convert HathiTrust ID to pairtree folder name: : → +, / → =."""
    return htid.replace(":", "+").replace("/", "=")


def main() -> int:
    parser = argparse.ArgumentParser(description="Align text pages to images (clean Hathi only).")
    parser.add_argument("--work-id", required=True, help="HathiTrust work_id (e.g. aeu.ark:/13960/t0ft9gj3x)")
    parser.add_argument("--metadata", required=True, help="Path to metadata CSV")
    parser.add_argument("--corpus", required=True, help="Path to pages JSONL or .jsonl.gz")
    parser.add_argument("--hathi-base", required=True, help="HathiTrust snapshot base path")
    args = parser.parse_args()

    # 1. Load text pages for work_id, sort by order
    pages = list(iter_pages_for_work(args.corpus, args.work_id))
    pages.sort(key=lambda p: p.get("order", 0))
    if not pages:
        print("Error: no pages found for this work_id", file=sys.stderr)
        return 2

    # 2. Pairtree folder name
    folder_name = htid_to_pairtree(args.work_id)
    volume_path = Path(args.hathi_base) / folder_name
    if not volume_path.is_dir():
        print(f"Error: volume folder not found: {volume_path}", file=sys.stderr)
        return 2

    # 3. Find ZIP (first .zip in folder)
    zips = sorted(volume_path.glob("*.zip"))
    if not zips:
        print(f"Error: no ZIP in {volume_path}", file=sys.stderr)
        return 2
    zip_path = zips[0]

    # 4. List .jp2 filenames inside ZIP (do not extract)
    with zipfile.ZipFile(zip_path, "r") as z:
        jp2_files = sorted(n for n in z.namelist() if n.endswith(".jp2"))

    # 5. Verify lengths
    if len(pages) != len(jp2_files):
        print(f"Mismatch: {len(pages)} text pages, {len(jp2_files)} images", file=sys.stderr)
        return 1
    print(f"OK: {len(pages)} text pages, {len(jp2_files)} images")

    # 6. First 5 text→image mappings
    print("\nFirst 5 text→image mappings:")
    for i in range(min(5, len(pages))):
        page = pages[i]
        img = jp2_files[i]
        print(f"  order {page.get('order')} (id={page.get('id')}) → {img}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
