"""SQL parsing and complexity scoring per handoff spec."""
import re
import hashlib
from typing import Any

import sqlparse
from sqlparse.sql import Statement, Token
from sqlparse.tokens import Keyword, DML


def _count_keyword(tokens: list, keyword: str) -> int:
    return sum(1 for t in tokens if t.ttype is Keyword and t.value.upper() == keyword.upper())


def _count_any_keywords(tokens: list, keywords: list) -> int:
    upper = [k.upper() for k in keywords]
    return sum(1 for t in tokens if t.ttype is Keyword and t.value.upper() in upper)


def _flatten_tokens(parsed: Statement) -> list:
    return list(parsed.flatten())


def calculate_complexity_score(sql_query: str) -> float:
    """
    Comprehensive SQL complexity scoring (handoff algorithm).
    Base 1 + SQL factors + length penalty.
    """
    if not (sql_query or sql_query.strip()):
        return 1.0
    score = 1.0
    sql_upper = sql_query.upper()
    try:
        parsed_list = sqlparse.parse(sql_query)
        if not parsed_list:
            return score
        parsed = parsed_list[0]
        tokens = _flatten_tokens(parsed)
    except Exception:
        tokens = []
        parsed = None

    # SELECT count (additional SELECTs = subqueries)
    select_count = _count_keyword(tokens, "SELECT")
    score += max(0, select_count - 1) * 1

    # JOINs
    join_count = _count_any_keywords(tokens, ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN", "CROSS JOIN", "JOIN"])
    score += join_count * 2

    # Subqueries (SELECT inside parens)
    subquery_count = len(re.findall(r"\(\s*SELECT", sql_query, re.IGNORECASE))
    score += subquery_count * 3

    # UNION / INTERSECT / EXCEPT
    set_ops = _count_any_keywords(tokens, ["UNION", "INTERSECT", "EXCEPT"])
    score += set_ops * 2

    # CASE
    case_count = _count_keyword(tokens, "CASE")
    score += case_count * 1

    # Aggregates
    agg = ["SUM", "COUNT", "AVG", "MAX", "MIN", "STDDEV", "VARIANCE"]
    score += _count_any_keywords(tokens, agg) * 1

    # Window functions
    window = ["ROW_NUMBER", "RANK", "DENSE_RANK", "NTILE", "LAG", "LEAD", "FIRST_VALUE", "LAST_VALUE"]
    score += _count_any_keywords(tokens, window) * 3

    # CTE
    cte_count = _count_keyword(tokens, "WITH")
    if "WITH RECURSIVE" in sql_upper:
        score += 5
    else:
        score += cte_count * 2

    # Line count penalty
    lines = len(sql_query.splitlines())
    if lines > 1000:
        score += 10
    elif lines > 500:
        score += 5
    elif lines > 100:
        score += 2

    return round(score, 1)


def complexity_category(score: float) -> str:
    if score <= 5:
        return "Simple"
    if score <= 15:
        return "Medium"
    if score <= 30:
        return "Complex"
    return "Very Complex"


def estimate_migration_hours(complexity_score: float) -> float:
    """Migration Hours = Complexity Score × 0.5"""
    return round(complexity_score * 0.5, 1)


def normalize_sql_for_fingerprint(sql: str) -> str:
    """Normalize SQL for duplicate detection: remove comments, whitespace, literals."""
    if not sql:
        return ""
    try:
        no_comments = sqlparse.format(sql, strip_comments=True)
    except Exception:
        no_comments = sql
    no_comments = sqlparse.format(no_comments, reindent=False, keyword_case="upper")
    # Replace numeric and string literals with placeholder
    normalized = re.sub(r"\b\d+\b", "?", no_comments)
    normalized = re.sub(r"'[^']*'", "?", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def generate_sql_fingerprint(sql: str) -> str:
    normalized = normalize_sql_for_fingerprint(sql)
    return hashlib.sha256(normalized.encode()).hexdigest()


def levenshtein_similarity(s1: str, s2: str) -> float:
    """Return similarity 0-1 based on Levenshtein distance."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    n, m = len(s1), len(s2)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i]
        for j in range(1, m + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    dist = prev[m]
    max_len = max(n, m)
    return 1.0 - (dist / max_len) if max_len else 1.0


def jaccard_similarity(tokens1: set, tokens2: set) -> float:
    if not tokens1 and not tokens2:
        return 1.0
    inter = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    return inter / union if union else 0.0


def tokenize_sql(sql: str) -> set:
    """Extract meaningful tokens (keywords and identifiers)."""
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return set()
        tokens = []
        for t in parsed[0].flatten():
            if t.ttype and t.ttype not in (sqlparse.tokens.Whitespace, sqlparse.tokens.Newline):
                tokens.append(t.value.upper())
        return set(tokens)
    except Exception:
        return set(re.findall(r"\w+", sql.upper()))


def sql_similarity_percent(sql1: str, sql2: str) -> float:
    """Combined similarity as percentage (handoff: Jaccard + Levenshtein)."""
    norm1 = normalize_sql_for_fingerprint(sql1)
    norm2 = normalize_sql_for_fingerprint(sql2)
    jaccard = jaccard_similarity(tokenize_sql(sql1), tokenize_sql(sql2))
    lev = levenshtein_similarity(norm1, norm2)
    combined = 0.6 * jaccard + 0.4 * lev
    return round(combined * 100, 2)


def extract_table_names(sql: str) -> list[str]:
    """Simple extraction of table names from FROM and JOIN."""
    names = set()
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return []
        # Walk and find FROM ... and JOIN ... (simplified)
        for token in parsed[0].tokens:
            if token.ttype is Keyword and token.value.upper() in ("FROM", "JOIN"):
                # Next token group often contains table name
                pass
        # Fallback: regex for FROM table and JOIN table
        for m in re.finditer(r"(?:FROM|JOIN)\s+(\w+)", sql, re.IGNORECASE):
            names.add(m.group(1).upper())
        return sorted(names)
    except Exception:
        return []
