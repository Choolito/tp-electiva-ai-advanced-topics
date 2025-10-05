def to_markdown_table(columns, rows, max_preview=50):
    if not columns:
        return '_Sin resultados_'
    head = '| ' + ' | '.join(columns) + ' |'
    sep  = '| ' + ' | '.join(['---']*len(columns)) + ' |'
    body = []
    for r in rows[:max_preview]:
        body.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    if len(rows) > max_preview:
        body.append(f'_ {len(rows)-max_preview} filas más no mostradas_')
    return '\n'.join([head, sep] + body)
