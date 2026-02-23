#!/usr/bin/env python3
"""
PPA Phase 1: Text integrity checker.

Takes a work_id, loads metadata and that work's pages from the JSONL corpus,
runs four integrity checks, and prints a structured report.
Streams the corpus (supports .jsonl and .jsonl.gz); does not load full corpus.
"""

import argparse
import sys
from pathlib import Path

# Allow running from repo root or from scripts/
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from src.checks import run_checks
from src.corpus import iter_pages_for_work
from src.metadata import get_work, load_metadata
from src.report import build_report, format_report_json, format_report_text


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check text integrity for a PPA work (page count, order, duplicates, empty text)."
    )
    parser.add_argument("--metadata", required=True, help="Path to metadata CSV (e.g. ppa_metadata.csv)")
    parser.add_argument("--corpus", required=True, help="Path to pages JSONL or .jsonl.gz (e.g. ppa_pages.jsonl.gz)")
    parser.add_argument("--work-id", required=True, help="PPA work_id to check")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    # 1. Load metadata
    try:
        metadata = load_metadata(args.metadata)
    except FileNotFoundError:
        print(f"Error: metadata file not found: {args.metadata}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error loading metadata: {e}", file=sys.stderr)
        return 2

    work = get_work(metadata, args.work_id)
    if work is None:
        print(f"Error: work_id not found in metadata: {args.work_id}", file=sys.stderr)
        return 2

    expected_count = work.get("page_count")
    if expected_count is None:
        print(f"Error: metadata row for {args.work_id} has no page_count", file=sys.stderr)
        return 2
    try:
        expected_count = int(expected_count)
    except (TypeError, ValueError):
        print(f"Error: page_count for {args.work_id} is not an integer: {expected_count}", file=sys.stderr)
        return 2

    # 2. Stream pages for this work
    try:
        pages = list(iter_pages_for_work(args.corpus, args.work_id))
    except FileNotFoundError:
        print(f"Error: corpus file not found: {args.corpus}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error reading corpus: {e}", file=sys.stderr)
        return 2

    # 3. Run checks
    check_results = run_checks(pages, expected_count)

    # 4. Build and print report
    report = build_report(args.work_id, work, check_results, pages)
    if args.format == "json":
        print(format_report_json(report))
    else:
        print(format_report_text(report))

    return 0 if report["summary"]["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
