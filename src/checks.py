"""Text integrity checks for a single work's pages."""

from typing import Any


def run_checks(pages: list[dict], expected_page_count: int) -> list[dict[str, Any]]:
    """
    Run all four integrity checks. Returns a list of result dicts with keys:
    check, passed, message, details (optional).
    Order convention: 1-based consecutive (1..N).
    """
    results = []

    # 1. Page count
    actual_count = len(pages)
    count_ok = actual_count == expected_page_count
    results.append({
        "check": "page_count",
        "passed": count_ok,
        "message": f"Page count: expected {expected_page_count}, got {actual_count}",
        "details": {"expected": expected_page_count, "actual": actual_count},
    })

    if not pages:
        results.append({
            "check": "continuous_order",
            "passed": False,
            "message": "No pages to check; order check skipped.",
            "details": None,
        })
        results.append({
            "check": "no_duplicate_orders",
            "passed": False,
            "message": "No pages to check; duplicate order check skipped.",
            "details": None,
        })
        results.append({
            "check": "no_empty_text",
            "passed": False,
            "message": "No pages to check; empty text check skipped.",
            "details": {"empty_page_ids": [], "empty_count": 0},
        })
        return results

    orders = []
    for p in pages:
        o = p.get("order")
        if o is not None:
            try:
                orders.append(int(o))
            except (TypeError, ValueError):
                orders.append(o)

    # 2. Continuous order (1-based: 1..N)
    expected_orders = set(range(1, expected_page_count + 1))
    actual_orders = set(orders)
    continuous_ok = actual_orders == expected_orders
    if not continuous_ok:
        missing = expected_orders - actual_orders
        extra = actual_orders - expected_orders
        msg = f"Order not continuous (1-based 1..{expected_page_count})."
        if missing:
            msg += f" Missing: {sorted(missing)[:10]}{'...' if len(missing) > 10 else ''}"
        if extra:
            msg += f" Extra: {sorted(extra)[:10]}{'...' if len(extra) > 10 else ''}"
    else:
        msg = f"Order is continuous (1..{expected_page_count})."
    results.append({
        "check": "continuous_order",
        "passed": continuous_ok,
        "message": msg,
        "details": {"expected_range": [1, expected_page_count], "missing": sorted(expected_orders - actual_orders) if not continuous_ok else [], "extra": sorted(actual_orders - expected_orders) if not continuous_ok else []},
    })

    # 3. No duplicate orders
    seen = {}
    for p in pages:
        o = p.get("order")
        pid = p.get("id", "")
        if o not in seen:
            seen[o] = []
        seen[o].append(pid)
    dupes = {o: ids for o, ids in seen.items() if len(ids) > 1}
    no_dupes_ok = len(dupes) == 0
    results.append({
        "check": "no_duplicate_orders",
        "passed": no_dupes_ok,
        "message": f"Duplicate orders: {len(dupes)}" if dupes else "No duplicate orders.",
        "details": dict(dupes) if dupes else None,
    })

    # 4. No empty text
    empty_page_ids = []
    for p in pages:
        text = p.get("text")
        if text is None or (isinstance(text, str) and not text.strip()):
            empty_page_ids.append(p.get("id", ""))
    no_empty_ok = len(empty_page_ids) == 0
    results.append({
        "check": "no_empty_text",
        "passed": no_empty_ok,
        "message": f"Empty text pages: {len(empty_page_ids)}" if empty_page_ids else "No empty text pages.",
        "details": {"empty_page_ids": empty_page_ids, "empty_count": len(empty_page_ids)},
    })

    return results
