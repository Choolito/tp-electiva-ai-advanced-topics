from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from .chains import run_nl_to_sql, build_db
from .safety import is_safe_sql, enforce_limit

@csrf_protect
def ask_view(request):
    context = {"question": "", "sql": "", "rows": [], "error": ""}
    if request.method == "POST":
        q = request.POST.get("question", "").strip()
        context["question"] = q
        try:
            sql = run_nl_to_sql(q)            # <- ahora solo genera y limpia
            if not is_safe_sql(sql):
                context["error"] = "La consulta generada no es segura (solo SELECT)."
            else:
                final_sql = enforce_limit(sql) # <- aseguramos LIMIT
                context["sql"] = final_sql
                db = build_db()
                context["rows"] = db.run(final_sql)  # <- ejecutamos recién acá
        except Exception as e:
            context["error"] = str(e)
    return render(request, "nl_sql_agent/ask.html", context)