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


def _format_rows_for_prompt(rows, max_rows: int = 20):
    """Devuelve una representación tabular simple (markdown) de un subconjunto de filas.
    Asume que cada fila es iterable. No tenemos nombres de columnas aquí, así que usamos índices.
    """
    if not rows:
        return "(sin filas)"
    subset = rows[:max_rows]
    headers = [f"col{i+1}" for i in range(len(subset[0]))]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for r in subset:
        out.append("| " + " | ".join(str(v) for v in r) + " |")
    if len(rows) > max_rows:
        out.append(f"(Mostrando {max_rows} de {len(rows)} filas)")
    return "\n".join(out)


def generate_nl_answer(question: str, sql: str, rows, *, language: str = "es", max_rows_in_prompt: int = 20) -> str:
    """Genera una respuesta en lenguaje natural a partir de la pregunta original,
    el SQL ejecutado y las filas devueltas.

    No vuelve a tocar la base: sólo usa datos ya obtenidos.
    """
    llm = build_llm()
    if not rows:
        base_prompt = (
            f"Pregunta original: {question}\n"
            f"SQL ejecutado: {sql}\n"
            "La consulta no devolvió filas. Explica brevemente esto al usuario en el idioma solicitado."
        )
    else:
        table_md = _format_rows_for_prompt(rows, max_rows=max_rows_in_prompt)
        base_prompt = (
            f"Eres un analista de datos. Responde de forma clara y concisa en idioma '{language}'.\n"
            f"Pregunta original: {question}\n"
            f"SQL utilizado: {sql}\n"
            f"Filas devueltas: {len(rows)} (se muestra un subconjunto si es grande).\n"
            f"Muestra de resultados en tabla markdown:\n{table_md}\n\n"
            "Genera una explicación breve enfocada en responder la pregunta. Si hay conteos o agregaciones, menciona los valores clave."
        )
    try:
        answer_msg = llm.invoke(base_prompt)
        # ChatGoogleGenerativeAI suele devolver un objeto con .content (lista) o .text
        if hasattr(answer_msg, "content") and isinstance(answer_msg.content, list):
            # Extraer texto plano de content
            parts = []
            for c in answer_msg.content:
                if isinstance(c, dict) and c.get("type") == "text":
                    parts.append(c.get("text", ""))
                elif isinstance(c, str):
                    parts.append(c)
            answer = "\n".join(p for p in parts if p).strip()
        elif hasattr(answer_msg, "text"):
            answer = answer_msg.text.strip()
        else:
            answer = str(answer_msg)
        return answer
    except Exception as e:
        logger.warning("Fallo al generar respuesta NL: %s", e)
        return "(No se pudo generar la explicación en lenguaje natural)"


def run_nl_to_sql_with_answer(question: str, *, apply_limit: bool = True, safe_mode: bool = True, language: str = "es"):
    """Conveniencia: combina generación de SQL, ejecución y respuesta NL.

    Devuelve dict con keys: sql, rows, answer.
    """
    sql, rows = run_nl_to_sql(question, apply_limit=apply_limit, safe_mode=safe_mode)
    answer = generate_nl_answer(question, sql, rows, language=language)
    return {"sql": sql, "rows": rows, "answer": answer}

