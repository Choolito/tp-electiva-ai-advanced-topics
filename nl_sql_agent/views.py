from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
import logging

# antes importabas run_nl_to_sql; ahora importá la nueva
from .chains import run_nl_sql_and_answer

logger = logging.getLogger(__name__)

@csrf_protect
def ask_view(request):
    context = {"question": "", "sql": "", "rows": [], "answer": "", "error": ""}
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        context["question"] = question
        if question:
            try:
                sql, rows, answer = run_nl_sql_and_answer(question)
                context["sql"] = sql
                context["rows"] = rows
                context["answer"] = answer
            except Exception as e:
                logger.warning("Fallo al procesar pregunta '%s': %s", question, e)
                context["error"] = str(e)
        else:
            context["error"] = "La pregunta no puede estar vacía."
    return render(request, "nl_sql_agent/ask.html", context)