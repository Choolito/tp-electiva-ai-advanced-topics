"""Utilidades para convertir preguntas NL a SQL seguro y ejecutarlas.

Incluye:
 - Cache de conexión a base y LLM para evitar sobrecarga.
 - Limpieza robusta del SQL generado por el modelo.
 - Validación de seguridad (solo SELECT) y aplicación de LIMIT.
"""

from django.conf import settings
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_sql_query_chain
import os, re, logging
from .safety import is_safe_sql, enforce_limit
import json
from sqlalchemy import text
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

_DB = None          # cache de instancia SQLDatabase, para no instanciarla cada vez
_LLM = None         # cache de LLM, para no instanciarlo cada vez
_SQL_BLOCK_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.IGNORECASE | re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def build_db(): 
    """Devuelve (cacheado) la instancia de SQLDatabase mapeando el schema."""
    global _DB
    if _DB is None:
        _DB = SQLDatabase.from_uri(settings.DB_URL)
    return _DB


def build_llm():
    """Devuelve (cacheado) el modelo LLM configurado (temperature=0 para estabilidad)."""
    global _LLM
    if _LLM is None:
        os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY or ""
        _LLM = ChatGoogleGenerativeAI(model=settings.MODEL_GEMINI, temperature=0)
    return _LLM


_PREFIXES = [
    "SQLQuery:", "SQL Query:", "SQL:", "Query:", "Consulta SQL:", "Consulta:",
    "Here is the SQL query:", "La consulta SQL es:", "La consulta es:", "Answer:", "Respuesta:"
]


def _strip_prefixes(s: str) -> str:
    for p in _PREFIXES:
        if s.lower().startswith(p.lower()):
            return _strip_prefixes(s[len(p):].strip())  # recursivo por si hay más de uno
    return s


def _extract_code_block(s: str) -> str:
    """Extrae el primer bloque de triple backticks que parezca contener SQL.
    Si no existe, intenta inline code `...`. Si nada aplica, devuelve original.
    """
    m = _SQL_BLOCK_RE.search(s)
    if m:
        inner = m.group(1).strip()
        # A veces el modelo mete explicaciones antes del SELECT dentro del bloque
        sel = re.search(r"(?is)\bselect\b|\bwith\b", inner)
        if sel:
            return inner[sel.start():].strip()
        return inner
    # Inline code (backticks simples)
    m2 = _INLINE_CODE_RE.search(s)
    if m2:
        candidate = m2.group(1).strip()
        if re.search(r"(?is)\bselect\b|\bwith\b", candidate):
            return candidate
    return s


def _first_select_segment(s: str) -> str:
    """Corta todo lo que precede al primer SELECT/WITH para evitar explicaciones previas."""
    m = re.search(r"(?is)\bselect\b|\bwith\b", s)
    if m:
        return s[m.start():].strip()
    return s.strip()


def _drop_trailing_semicolon(s: str) -> str:
    return s.rstrip(" ;\n\t\r")


def _single_statement(s: str) -> str:
    """Aísla la primera sentencia (naive). Si hay ';' toma lo anterior.
    (Para casos simples es suficiente; si se necesitan garantías fuertes se debe parsear)."""
    parts = re.split(r";\s*\n?|;\s*$", s, 1)
    return parts[0].strip()


def clean_sql(text: str) -> str:
    """Limpia output del LLM para obtener solo la sentencia SELECT/WITH.

    Pasos:
      1. Trim inicial
      2. Extraer bloque ```sql ... ``` o inline code si existe
      3. Eliminar prefijos verbosos
      4. Quedarse desde primer SELECT/WITH
      5. Quitar ; final
      6. Asegurar solo la primera sentencia
    """
    if not text or not isinstance(text, str):
        return ""
    s = text.strip()
    s = _extract_code_block(s)
    s = _strip_prefixes(s)
    s = _first_select_segment(s)
    s = _drop_trailing_semicolon(s)
    s = _single_statement(s)
    return s


def run_nl_to_sql(question: str, *, apply_limit: bool = True, safe_mode: bool = True):
    """Genera y ejecuta SQL a partir de una pregunta.

    Devuelve (sql_final, rows).
    - Limpia el SQL del modelo.
    - Valida seguridad (solo SELECT) si safe_mode.
    - Aplica LIMIT si apply_limit y no hay uno presente.
    """
    if not question or not question.strip():
        raise ValueError("La pregunta está vacía")

    db = build_db()
    llm = build_llm()
    chain = create_sql_query_chain(llm, db)

    raw = chain.invoke({"question": question})
    cleaned = clean_sql(raw)

    if safe_mode and not is_safe_sql(cleaned):
        raise ValueError("Consulta generada no es segura (solo SELECT permitido)")
    final_sql = enforce_limit(cleaned) if apply_limit else cleaned
    try:
        rows = db.run(final_sql)
    except Exception as e:
        logger.error("Error ejecutando SQL '%s': %s", final_sql, e)
        raise

    return final_sql, rows

def _sample_result_for_nlg(db, sql: str, sample_limit: int = 50):
    """Reejecuta el SELECT para obtener columnas + hasta sample_limit filas como dicts."""
    engine = db._engine  # expuesto por SQLDatabase
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        cols = list(result.keys())
        # mappings() nos da dicts por fila; acotamos para no inflar el prompt
        sample = result.mappings().fetchmany(sample_limit)
        rows = [dict(r) for r in sample]
    return cols, rows

def run_nl_sql_and_answer(question: str):
    """
    Flujo completo: NL -> SQL -> ejecutar -> NLG.
    Devuelve (sql, rows_originales, answer_text).
    - NO modifica run_nl_to_sql: lo reutiliza tal cual lo tenés.
    """
    # 1) Generamos SQL y ejecutamos (tu lógica actual)
    sql, rows = run_nl_to_sql(question)

    # 2) Reejecutamos para obtener columnas + filas como dicts (mejor para el LLM)
    db = build_db()
    cols, rows_dicts = _sample_result_for_nlg(db, sql, sample_limit=50)

    # 3) Pedimos la respuesta en español usando SOLO esos datos
    llm = build_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Sos un analista de datos. Respondé en español, breve y factual."),
        ("system", "Usá EXCLUSIVAMENTE los datos provistos. Si no hay datos, respondé: 'No se encontraron resultados'. No inventes."),
        ("human",
         "Pregunta original:\n{q}\n\nSQL ejecutado:\n{sql}\n\nColumnas:\n{cols}\n\nPrimeras filas (JSON, máx 50):\n{rows_json}\n\n"
         "Indicaciones:\n- Si hay números, incluí totales o conteos visibles.\n"
         "- Si no hay filas, respondé solo 'No se encontraron resultados'.\n"
         "- Si son muchas filas similares, resumí por grupos relevantes.")
    ])
    answer = (prompt | llm).invoke({
        "q": question,
        "sql": sql,
        "cols": ", ".join(cols) if cols else "(sin columnas)",
        "rows_json": json.dumps(rows_dicts, ensure_ascii=False)
    })
    answer_text = getattr(answer, "content", str(answer))

    return sql, rows, answer_text