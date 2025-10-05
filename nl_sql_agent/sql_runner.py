import os
from django.db import connection
from .guardrails import validate_sql, enforce_limit

MAX_ROWS = int(os.getenv('MAX_ROWS', '200'))
STRICT_MODE = os.getenv('STRICT_MODE', 'true').lower() == 'true'

class QueryError(Exception):
    pass

def run_sql(sql: str):
    ok, reason = validate_sql(sql, strict=STRICT_MODE)
    if not ok:
        raise QueryError(f'SQL inválido: {reason}')
    sql = enforce_limit(sql, MAX_ROWS)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        cols = [c[0] for c in cursor.description] if cursor.description else []
        rows = cursor.fetchall() if cursor.description else []
    return cols, rows, sql
