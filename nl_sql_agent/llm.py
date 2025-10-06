import os
import textwrap
import json
from decimal import Decimal
from datetime import date, datetime

import google.generativeai as genai
from google.api_core import exceptions as gexc
from .examples import FEW_SHOTS_TEMPLATE

DEFAULT_MODEL = "gemini-flash-latest"

SYSTEM_RULES = """Eres un traductor NLSQL. Devuelves SOLO SQL válido.
Requisitos:
- Solo SELECT. Prohibido DDL/DML.
- Respeta tablas/columnas del ESQUEMA.
- Agrega LIMIT {max_rows}.
"""

# ---------------------------------------------------------------------
# Prompt para NL -> SQL
# ---------------------------------------------------------------------
def build_prompt(user_question: str, schema_markdown: str, max_rows: int = 200) -> str:
    return textwrap.dedent(f"""
    {SYSTEM_RULES.format(max_rows=max_rows)}

    ESQUEMA:
    {schema_markdown}

    EJEMPLOS:
    {FEW_SHOTS_TEMPLATE}

    PREGUNTA:
    {user_question}

    SQL:
    """).strip()

# ---------------------------------------------------------------------
# NL -> SQL (versión estable y pragmática)
# ---------------------------------------------------------------------
def generate_sql(user_question: str, schema_markdown: str, max_rows: int = 200) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # sin API key no frenamos el flujo
        return f"SELECT 1 as placeholder LIMIT {max_rows};"

    genai.configure(api_key=api_key)
    prompt = build_prompt(user_question, schema_markdown, max_rows)

    candidates = [
        "gemini-flash-latest",
        "gemini-2.0-flash",
        # "gemini-2.5-flash-preview-09-2025",
    ]
    last_err = None
    for m in candidates:
        try:
            model = genai.GenerativeModel(m)
            resp = model.generate_content(
                prompt,
                generation_config={"temperature": 0, "max_output_tokens": 512},
            )
            sql = (getattr(resp, "text", "") or "").strip()
            # limpiar bloque de ```sql
            if sql.startswith("```"):
                sql = sql.strip("` ").split("\n", 1)[-1]
            if not sql:
                continue
            return sql
        except gexc.NotFound as e:
            last_err = e
            continue
        except Exception as e:
            last_err = e
            continue
    # si nada funcionó, devolvemos placeholder
    return f"SELECT 1 as placeholder LIMIT {max_rows};"

# ---------------------------------------------------------------------
# Util JSON-safe (para payloads al LLM)
# ---------------------------------------------------------------------
def _to_json_safe(x):
    if isinstance(x, Decimal):
        return float(x)
    if isinstance(x, (date, datetime)):
        return x.isoformat()
    return x

# ---------------------------------------------------------------------
# Extractor estricto de texto desde candidates[].content.parts
# ---------------------------------------------------------------------
def _extract_text_strict(resp):
    # Debe haber candidatos
    if not getattr(resp, "candidates", None):
        raise RuntimeError("LLM_EMPTY_RESPONSE_NO_CANDIDATES")

    cand = resp.candidates[0]
    fr = getattr(cand, "finish_reason", None)
    # 1 / "SAFETY" => bloqueado por políticas; 2 => STOP sin contenido útil
    if fr in (1, "SAFETY"):
        raise RuntimeError("LLM_BLOCKED_BY_SAFETY")
    if fr == 2:
        raise RuntimeError("LLM_EMPTY_OUTPUT_FINISH_REASON_2")

    # Intentar extraer texto de las partes
    content = getattr(cand, "content", None)
    parts = getattr(content, "parts", None) if content else None
    if parts:
        chunks = []
        for p in parts:
            t = getattr(p, "text", None)
            if t:
                chunks.append(t)
        text = "\n".join(chunks).strip()
        if text:
            return text

    # Fallback al atajo .text solo si existe
    t2 = (getattr(resp, "text", "") or "").strip()
    if t2:
        return t2

    raise RuntimeError("LLM_EMPTY_TEXT_NO_PARTS")

# ---------------------------------------------------------------------
# Resumen textual SOLO con LLM (si falla, propaga excepción)
# ---------------------------------------------------------------------
def summarize_result(question: str, columns, rows, max_rows_for_llm: int = 50) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("LLM_DISABLED_NO_API_KEY")

    # kill-switch por .env si querés apagar el resumen sin tocar código
    if os.getenv("DISABLE_SUMMARY", "false").lower() == "true":
        raise RuntimeError("SUMMARY_DISABLED")

    genai.configure(api_key=api_key)

    # Limitar y sanear filas para JSON en el prompt
    safe_rows = [[_to_json_safe(v) for v in r] for r in rows[:max_rows_for_llm]]
    payload = {"columns": columns, "rows": safe_rows, "total_rows": len(rows)}

    system = """Eres un analista de datos.
Responde en español en 1 a 3 oraciones, usando EXCLUSIVAMENTE las filas provistas.
Si no hay datos, dilo claramente. No inventes columnas ni valores."""
    user = f"""Pregunta del usuario:
{question}

Tabla (JSON):
{json.dumps(payload, ensure_ascii=False)}"""

    model = genai.GenerativeModel(DEFAULT_MODEL)
    resp = model.generate_content(
        textwrap.dedent(system + "\n\n" + user).strip(),
        generation_config={"temperature": 0, "max_output_tokens": 160},
    )

    # Extraer texto de forma robusta
    return _extract_text_strict(resp)
