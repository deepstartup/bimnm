"""COE CSV processor: complexity scoring, duplicate detection, effort estimation."""
import io
import json
from collections import defaultdict
from typing import Any

import pandas as pd

from app.utils.sql_parser import (
    calculate_complexity_score,
    complexity_category,
    estimate_migration_hours,
    generate_sql_fingerprint,
    sql_similarity_percent,
)

# Expected CSV columns (handoff)
REPORT_NAME = "Report Name"
REPORT_ID = "Report ID"
QUERY_SQL = "Query SQL"
REPORT_OWNER = "Report Owner"
LAST_REFRESH = "Last Refresh Date"
ROW_COUNT = "Row Count"
RUN_TIME = "Run Time (seconds)"

# Alternative column names for flexibility
COL_ALIASES = {
    "report name": REPORT_NAME,
    "reportname": REPORT_NAME,
    "report id": REPORT_ID,
    "reportid": REPORT_ID,
    "query sql": QUERY_SQL,
    "querysql": QUERY_SQL,
    "sql": QUERY_SQL,
    "report owner": REPORT_OWNER,
    "owner": REPORT_OWNER,
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map columns to standard names if possible."""
    col_map = {}
    for c in df.columns:
        key = (c or "").strip().lower()
        if key in COL_ALIASES:
            col_map[c] = COL_ALIASES[key]
        else:
            col_map[c] = c
    return df.rename(columns=col_map)


def _sql_column(df: pd.DataFrame) -> str | None:
    for candidate in [QUERY_SQL, "Query SQL", "SQL", "sql"]:
        if candidate in df.columns:
            return candidate
    return None


def _name_column(df: pd.DataFrame) -> str | None:
    for candidate in [REPORT_NAME, "Report Name", "Name", "name"]:
        if candidate in df.columns:
            return candidate
    return None


def process_coe_csv(content: bytes, filename: str) -> dict[str, Any]:
    """
    Parse COE CSV and return analysis: complexity distribution, duplicates,
    total hours, top complex, by owner.
    """
    df = pd.read_csv(io.BytesIO(content))
    df = _normalize_columns(df)
    sql_col = _sql_column(df)
    name_col = _name_column(df) or "Report"
    if sql_col is None:
        return {
            "error": "No SQL column found. Expected 'Query SQL' or similar.",
            "report_count": 0,
        }

    reports = []
    for idx, row in df.iterrows():
        sql = row.get(sql_col)
        if pd.isna(sql):
            sql = ""
        sql = str(sql).strip()
        name = str(row.get(name_col, f"Report_{idx}")).strip()
        owner = str(row.get(REPORT_OWNER, "")).strip() if REPORT_OWNER in df.columns else ""
        score = calculate_complexity_score(sql)
        cat = complexity_category(score)
        hours = estimate_migration_hours(score)
        fingerprint = generate_sql_fingerprint(sql) if sql else ""
        reports.append({
            "report_name": name,
            "report_id": str(row.get(REPORT_ID, idx)) if REPORT_ID in df.columns else str(idx),
            "sql": sql,
            "owner": owner,
            "complexity_score": score,
            "complexity_category": cat,
            "estimated_hours": hours,
            "fingerprint": fingerprint,
        })

    # Complexity distribution
    dist = defaultdict(int)
    for r in reports:
        dist[r["complexity_category"]] += 1
    complexity_distribution = dict(dist)

    # Duplicate groups by fingerprint (exact) and by similarity (>= 85%)
    fingerprint_groups = defaultdict(list)
    for r in reports:
        if r["fingerprint"]:
            fingerprint_groups[r["fingerprint"]].append(r)

    exact_duplicate_groups = [
        {"reports": g, "similarity": 100, "type": "EXACT"}
        for g in fingerprint_groups.values()
        if len(g) > 1
    ]

    # Near duplicates: unique by fingerprint, then pairwise similarity >= 85%
    unique_by_fp = {fp: group[0] for fp, group in fingerprint_groups.items()}
    unique_list = list(unique_by_fp.values())
    near_duplicate_groups = []
    seen_pairs = set()
    for i, r1 in enumerate(unique_list):
        for r2 in unique_list[i + 1 :]:
            if not r1.get("sql") or not r2.get("sql"):
                continue
            sim = sql_similarity_percent(r1["sql"], r2["sql"])
            if sim >= 85 and sim < 100:
                pair_key = tuple(sorted([r1["report_name"], r2["report_name"]]))
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    near_duplicate_groups.append({
                        "reports": [r1, r2],
                        "similarity": round(sim, 1),
                        "type": "NEAR_DUPLICATE",
                    })

    total_hours = sum(r["estimated_hours"] for r in reports)
    total_duplicates = sum(max(0, len(g["reports"]) - 1) for g in exact_duplicate_groups)
    total_duplicates += len(near_duplicate_groups)  # approximate

    # Top 10 most complex
    sorted_by_complexity = sorted(reports, key=lambda x: -x["complexity_score"])[:10]

    # By owner
    by_owner = defaultdict(list)
    for r in reports:
        by_owner[r.get("owner") or "Unknown"].append(r["report_name"])
    reports_by_owner = {k: len(v) for k, v in by_owner.items()}

    duplicate_groups = exact_duplicate_groups + near_duplicate_groups

    return {
        "report_count": len(reports),
        "unique_count": len(unique_list),
        "duplicate_count": int(total_duplicates),
        "complexity_distribution": complexity_distribution,
        "total_estimated_hours": round(total_hours, 1),
        "avg_complexity": round(sum(r["complexity_score"] for r in reports) / len(reports), 1) if reports else 0,
        "duplicate_groups": [
            {
                "similarity": g["similarity"],
                "type": g["type"],
                "report_names": [x["report_name"] for x in g["reports"]],
                "recommendation": "Consolidate into single parameterized report" if g["similarity"] >= 95 else "Review for consolidation",
            }
            for g in duplicate_groups
        ],
        "top_complex_reports": [
            {
                "report_name": r["report_name"],
                "complexity_score": r["complexity_score"],
                "complexity_category": r["complexity_category"],
                "estimated_hours": r["estimated_hours"],
            }
            for r in sorted_by_complexity
        ],
        "reports_by_owner": reports_by_owner,
        "reports": reports,
    }
