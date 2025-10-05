import re, sqlparse
from typing import Tuple

DML_DDL_BLOCKLIST = re.compile(r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE)\b', re.IGNORECASE)

def validate_sql(sql: str, strict: bool = True) -> Tuple[bool, str]:
    if not sql.strip():
        return False, 'Vacío'
    parsed = sqlparse.parse(sql)
    if len(parsed) != 1:
        return False, 'Múltiples sentencias'
    first = next((t for t in parsed[0].tokens if not t.is_whitespace), None)
    if strict and (not first or first.normalized.upper() != 'SELECT'):
        return False, 'Sólo SELECT en modo estricto'
    if DML_DDL_BLOCKLIST.search(sql):
        return False, 'Palabra clave prohibida'
    return True, 'OK'

def enforce_limit(sql: str, max_rows: int) -> str:
    low = sql.lower()
    if 'limit ' in low:
        return sql
    return f"{sql.strip().rstrip(';')}\nLIMIT {int(max_rows)};"
