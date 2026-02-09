"""SQL complexity analyzer and comparison (handoff spec)."""
from typing import Any

from app.utils.sql_parser import (
    calculate_complexity_score,
    complexity_category,
    estimate_migration_hours,
    extract_table_names,
    normalize_sql_for_fingerprint,
    sql_similarity_percent,
)
import sqlparse


def analyze_sql(sql: str) -> dict[str, Any]:
    """Full SQL analysis: complexity, category, hours, lineage, recommendations."""
    if not (sql or sql.strip()):
        return {
            "complexity_score": 1,
            "complexity_category": "Simple",
            "estimated_hours": 0.5,
            "metrics": {},
            "lineage": {"tables": [], "columns": []},
            "recommendations": [],
        }
    score = calculate_complexity_score(sql)
    cat = complexity_category(score)
    hours = estimate_migration_hours(score)
    tables = extract_table_names(sql)
    # Simple column extraction: tokens between SELECT and FROM
    columns = []
    try:
        import re
        from_idx = sql.upper().find(" FROM ")
        if from_idx > 0:
            select_part = sql[:from_idx].strip()
            if select_part.upper().startswith("SELECT"):
                select_part = select_part[6:].strip()
            for word in re.findall(r"[\w.]+", select_part):
                w = word.upper()
                if w not in ("SELECT", "DISTINCT", "AS", "FROM") and not w.isdigit():
                    columns.append(word)
        lineage = {"tables": tables, "columns": columns[:50]}
    except Exception:
        lineage = {"tables": tables, "columns": []}
    # Migration recommendations based on common patterns
    recommendations = []
    sql_upper = sql.upper()
    if "DECODE" in sql_upper:
        recommendations.append("Replace DECODE with CASE WHEN")
    if "NVL" in sql_upper:
        recommendations.append("Replace NVL with COALESCE or ISNULL")
    if "ROWNUM" in sql_upper:
        recommendations.append("Convert ROWNUM to ROW_NUMBER() OVER (ORDER BY ...)")
    if "SYSDATE" in sql_upper:
        recommendations.append("Replace SYSDATE with target DB current date function")
    if "TOP " in sql_upper and "LIMIT" not in sql_upper:
        recommendations.append("Consider TOP vs LIMIT for target platform")
    return {
        "complexity_score": score,
        "complexity_category": cat,
        "estimated_hours": hours,
        "risk_level": "HIGH" if score > 25 else "MEDIUM" if score > 15 else "LOW",
        "metrics": {
            "tables_referenced": len(tables),
            "line_count": len(sql.splitlines()),
        },
        "lineage": lineage,
        "recommendations": recommendations,
    }


def compare_sql(sql1: str, sql2: str) -> dict[str, Any]:
    """Compare two SQL queries: identical, semantically equivalent, differences."""
    norm1 = normalize_sql_for_fingerprint(sql1 or "")
    norm2 = normalize_sql_for_fingerprint(sql2 or "")
    are_identical = norm1 == norm2
    similarity = sql_similarity_percent(sql1 or "", sql2 or "") if (sql1 or sql2) else 100.0 if not sql1 and not sql2 else 0.0
    are_semantically_equivalent = similarity >= 95
    differences = {
        "select_clause": {"added": [], "removed": [], "note": ""},
        "from_clause": {"added": [], "removed": [], "note": ""},
        "where_clause": {"added": [], "removed": [], "note": ""},
    }
    if not are_identical:
        differences["select_clause"]["note"] = "Compare SELECT lists manually"
    compatibility_score = min(100, int(similarity))
    migration_quality = "EXCELLENT" if compatibility_score >= 95 else "GOOD" if compatibility_score >= 80 else "FAIR" if compatibility_score >= 60 else "REVIEW"
    return {
        "are_identical": are_identical,
        "are_semantically_equivalent": are_semantically_equivalent,
        "similarity_percent": round(similarity, 1),
        "differences": differences,
        "compatibility_score": compatibility_score,
        "migration_quality": migration_quality,
    }
