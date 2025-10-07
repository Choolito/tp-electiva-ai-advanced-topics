import re

BLOCKLIST = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b", r"\bALTER\b",
    r"\bCREATE\b", r"\bATTACH\b", r"\bDETACH\b", r";", r"--", r"/\*"
]

def is_safe_sql(sql: str) -> bool:
    sql_up = sql.upper().strip()
    if not sql_up.startswith("SELECT"):
        return False
    for pat in BLOCKLIST:
        if re.search(pat, sql_up):
            return False
    return True

def enforce_limit(sql: str, default_limit: int = 100) -> str:
    s = sql.strip().rstrip(";")
    if re.search(r"\bLIMIT\s+\d+\b", s, flags=re.IGNORECASE):
        return s
    return f"{s} LIMIT {default_limit}"
