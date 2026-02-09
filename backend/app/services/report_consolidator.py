"""Report consolidation: duplicate detection across user reports."""
from typing import Any
from collections import defaultdict

from app.utils.sql_parser import (
    generate_sql_fingerprint,
    sql_similarity_percent,
    estimate_migration_hours,
)
from app.models.report import Report


def consolidate_reports(reports: list[Report]) -> dict[str, Any]:
    """
    Find duplicate and near-duplicate reports by SQL fingerprint and similarity.
    Returns duplicate_groups, potential_savings.
    """
    if not reports:
        return {
            "total_reports": 0,
            "unique_reports": 0,
            "duplicate_groups": [],
            "potential_savings": {"reports_to_skip": 0, "hours_saved": 0},
        }
    # Build list with sql and id
    items = []
    for r in reports:
        sql = (r.sql_query or "").strip()
        fp = generate_sql_fingerprint(sql) if sql else ""
        items.append({
            "id": r.id,
            "name": r.name,
            "sql": sql,
            "fingerprint": fp,
            "estimated_hours": r.estimated_hours or (r.complexity_score or 1) * 0.5,
        })
    # Exact duplicates by fingerprint
    fp_groups = defaultdict(list)
    for it in items:
        if it["fingerprint"]:
            fp_groups[it["fingerprint"]].append(it)
    exact_groups = [g for g in fp_groups.values() if len(g) > 1]
    unique_by_fp = {fp: g[0] for fp, g in fp_groups.items()}
    unique_list = list(unique_by_fp.values())
    # Near duplicates
    near_groups = []
    seen = set()
    for i, a in enumerate(unique_list):
        for b in unique_list[i + 1 :]:
            if not a["sql"] or not b["sql"]:
                continue
            key = tuple(sorted([a["id"], b["id"]]))
            if key in seen:
                continue
            sim = sql_similarity_percent(a["sql"], b["sql"])
            if 85 <= sim < 100:
                seen.add(key)
                near_groups.append({
                    "reports": [a, b],
                    "similarity": round(sim, 1),
                    "recommendation": "Consolidate into single parameterized report with filters",
                })
    duplicate_groups = []
    reports_to_skip = 0
    hours_saved = 0.0
    for g in exact_groups:
        duplicate_groups.append({
            "group_id": len(duplicate_groups) + 1,
            "similarity": 100,
            "type": "EXACT",
            "reports": [{"id": x["id"], "name": x["name"]} for x in g],
            "recommendation": "Migrate only one; create aliases for others",
        })
        reports_to_skip += len(g) - 1
        hours_saved += sum(x["estimated_hours"] for x in g[1:])
    for g in near_groups:
        duplicate_groups.append({
            "group_id": len(duplicate_groups) + 1,
            "similarity": g["similarity"],
            "type": "NEAR_DUPLICATE",
            "reports": [{"id": x["id"], "name": x["name"]} for x in g["reports"]],
            "recommendation": g["recommendation"],
        })
        reports_to_skip += 1
        hours_saved += g["reports"][1]["estimated_hours"]
    return {
        "total_reports": len(reports),
        "unique_reports": len(unique_list),
        "duplicate_groups": duplicate_groups,
        "potential_savings": {
            "reports_to_skip": reports_to_skip,
            "hours_saved": round(hours_saved, 1),
        },
    }
