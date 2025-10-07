# agent/views.py
from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
import logging

from .chains import run_nl_to_sql

logger = logging.getLogger(__name__)

@csrf_protect
def ask_view(request): 
    """Vista principal para formular preguntas NL y ver el SQL/resultados.

    Ahora la validación de seguridad y el LIMIT se realizan dentro de run_nl_to_sql,
    por lo que eliminamos la lógica duplicada aquí.
    """
    context = {"question": "", "sql": "", "rows": [], "error": ""}
    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        context["question"] = question
        if question:
            try:
                sql, rows = run_nl_to_sql(question)
                context["sql"] = sql
                context["rows"] = rows
            except Exception as e:
                # Log interno y mensaje simple al usuario
                logger.warning("Fallo al procesar pregunta '%s': %s", question, e)
                context["error"] = str(e)
        else:
            context["error"] = "La pregunta no puede estar vacía."
    # Ajuste: el template existente en la app es 'nl_sql_agent/ask.html'
    return render(request, "nl_sql_agent/ask.html", context)
