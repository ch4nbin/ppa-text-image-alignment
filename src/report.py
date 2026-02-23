"""Build and format the text-integrity summary report."""

import json
from typing import Any


def build_report(
    work_id: str,
    work_metadata: dict | None,
    check_results: list[dict[str, Any]],
    pages: list[dict],
) -> dict[str, Any]:
    """Build a structured summary dict for work_id, metadata, checks, and stats."""
    expected_count = work_metadata.get("page_count", 0) if work_metadata else 0
    if isinstance(expected_count, str):
        try:
            expected_count = int(expected_count)
        except ValueError:
            expected_count = 0
    actual_count = len(pages)
    all_passed = all(r["passed"] for r in check_results)

    orders = []
    for p in pages:
        o = p.get("order")
        if o is not None:
            try:
                orders.append(int(o))
            except (TypeError, ValueError):
                pass
    min_order = min(orders) if orders else None
    max_order = max(orders) if orders else None

    empty_check = next((r for r in check_results if r["check"] == "no_empty_text"), None)
    empty_count = 0
    if empty_check and empty_check.get("details"):
        empty_count = empty_check["details"].get("empty_count", 0)

    return {
        "work_id": work_id,
        "metadata": work_metadata,
        "summary": {
            "all_passed": all_passed,
            "expected_page_count": expected_count,
            "actual_page_count": actual_count,
            "order_range": [min_order, max_order],
            "empty_text_count": empty_count,
        },
        "checks": check_results,
    }


def format_report_text(report: dict[str, Any]) -> str:
    """Format the report as human-readable text."""
    lines = [
        "=== PPA Text Integrity Report ===",
        f"work_id: {report['work_id']}",
        "",
    ]
    meta = report.get("metadata") or {}
    if meta:
        lines.append(f"Source: {meta.get('source', '—')}")
        title = (meta.get("title") or "—")
        if len(title) > 80:
            title = title[:80] + "..."
        lines.append(f"Title: {title}")
        lines.append("")
    s = report.get("summary", {})
    lines.append(f"Expected page count: {s.get('expected_page_count', '—')}")
    lines.append(f"Actual page count:   {s.get('actual_page_count', '—')}")
    lines.append(f"Order range:         {s.get('order_range', [None, None])}")
    lines.append(f"Empty text pages:    {s.get('empty_text_count', 0)}")
    lines.append("")
    lines.append("Checks:")
    for r in report.get("checks", []):
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"  [{status}] {r['check']}: {r['message']}")
    lines.append("")
    lines.append("Overall: " + ("PASS" if report.get("summary", {}).get("all_passed") else "FAIL"))
    return "\n".join(lines)


def format_report_json(report: dict[str, Any]) -> str:
    """Format the report as a single JSON object (one line or pretty)."""
    out = {
        "work_id": report["work_id"],
        "summary": report["summary"],
        "checks": report["checks"],
    }
    if report.get("metadata"):
        out["metadata"] = {
            "work_id": report["metadata"].get("work_id"),
            "source": report["metadata"].get("source"),
            "page_count": report["metadata"].get("page_count"),
            "title": report["metadata"].get("title"),
        }
    return json.dumps(out, indent=2)
