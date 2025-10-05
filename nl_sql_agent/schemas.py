from django.db import connection

def get_schema_markdown() -> str:
    introspection = connection.introspection
    lines = []
    with connection.cursor() as cursor:
        tables = introspection.table_names(cursor)
        for t in sorted(tables):
            lines.append(f'### {t}')
            try:
                cols = introspection.get_table_description(cursor, t)
                for c in cols:
                    lines.append(f'- {c.name}')
            except Exception:
                pass
    return '\n'.join(lines)
