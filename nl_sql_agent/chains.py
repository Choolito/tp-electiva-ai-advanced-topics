# agent/chains.py
from django.conf import settings
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
import os, re

def build_db():
    return SQLDatabase.from_uri(settings.DB_URL)

def build_llm():
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
    return ChatGoogleGenerativeAI(model=settings.MODEL_GEMINI, temperature=0)

_SQL_BLOCK_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)

def clean_sql(text: str) -> str:
    s = text.strip()

    # 1) Si vino en bloque ```sql ... ```
    m = _SQL_BLOCK_RE.search(s)
    if m:
        s = m.group(1).strip()

    # 2) Sacar prefijos molestos
    prefixes = [
        "SQLQuery:", "SQL Query:", "SQL:", "Query:", "Consulta SQL:", "Consulta:",
        "Here is the SQL query:", "La consulta SQL es:"
    ]
    for p in prefixes:
        if s.lower().startswith(p.lower()):
            s = s[len(p):].strip()

    # 3) Borrar explicaciones al final tipo "This query does ..."
    # (opcional: cortamos en la primera línea que empieza con SELECT)
    sel = re.search(r"(?is)\bselect\b", s)
    if sel:
        s = s[sel.start():].strip()

    # 4) Quitar ; final (lo volveremos a poner si hace falta)
    s = s.rstrip(" ;\n\t\r")

    return s

def run_nl_to_sql(question: str) -> str:
    db = build_db()
    llm = build_llm()
    chain = create_sql_query_chain(llm, db)
    raw = chain.invoke({"question": question})
    return clean_sql(raw)

