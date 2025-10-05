import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def query_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Sólo POST"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"error": f"JSON inválido: {e}"}, status=400)

    question = (payload.get("question") or "").strip()
    answer_mode = (payload.get("answer_mode") or "table").strip().lower()  # "table" | "text" | "both"
    if not question:
        return JsonResponse({"error": "Falta 'question'"}, status=400)

    try:
        from .schemas import get_schema_markdown
        from .sql_runner import run_sql, QueryError
        from .formatters import to_markdown_table
        from .llm import generate_sql, summarize_result
    except Exception as e:
        return JsonResponse({"error": f"Fallo import interno: {e}"}, status=500)

    # Prompt al LLM para SQL
    try:
        schema_md = get_schema_markdown()
        sql = generate_sql(question, schema_md, max_rows=200)
        if not sql or "select" not in sql.lower():
            return JsonResponse({"error": "El LLM no generó un SELECT válido", "sql": sql}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Fallo al generar SQL con LLM: {e}"}, status=500)

    # Ejecutar SQL
    try:
        cols, rows, final_sql = run_sql(sql)
    except QueryError as qe:
        return JsonResponse({"error": str(qe), "sql": sql}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Fallo al ejecutar SQL: {e}", "sql": sql}, status=500)

    # Post-procesar con LLM si se pide texto
    answer_text = None
    if answer_mode in ("text", "both"):
        try:
            answer_text = summarize_result(question, cols, rows, max_rows_for_llm=50)
        except Exception as e:
            answer_text = f"(No se pudo generar el resumen: {e})"

    resp = {
        "question": question,
        "sql": final_sql,
        "columns": cols,
        "rows": rows,
        "preview_markdown": to_markdown_table(cols, rows)
    }
    if answer_text is not None:
        resp["answer_text"] = answer_text

    return JsonResponse(resp, status=200)
