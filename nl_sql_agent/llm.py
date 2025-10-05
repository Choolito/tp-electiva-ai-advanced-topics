import os, textwrap, json
import google.generativeai as genai
from .examples import FEW_SHOTS_TEMPLATE

DEFAULT_MODEL = "gemini-flash-latest"

SYSTEM_RULES = """Eres un traductor NLSQL. Devuelves SOLO SQL válido.
Requisitos:
- Solo SELECT. Prohibido DDL/DML.
- Respeta tablas/columnas del ESQUEMA.
- Agrega LIMIT {max_rows}.
"""

def build_prompt(user_question: str, schema_markdown: str, max_rows: int = 200) -> str:
    return textwrap.dedent(f'''
    {SYSTEM_RULES.format(max_rows=max_rows)}

    ESQUEMA:
    {schema_markdown}

    EJEMPLOS:
    {FEW_SHOTS_TEMPLATE}

    PREGUNTA:
    {user_question}

    SQL:
    ''').strip()

def generate_sql(user_question: str, schema_markdown: str, max_rows: int = 200) -> str:
    import os, textwrap, google.generativeai as genai
    from google.api_core import exceptions as gexc

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return f"SELECT 1 as placeholder LIMIT {max_rows};"

    genai.configure(api_key=api_key)

    prompt = build_prompt(user_question, schema_markdown, max_rows)

    candidates = [
        "gemini-flash-latest",
        "gemini-2.0-flash",
        # si querés probar previews: "gemini-2.5-flash-preview-09-2025"
    ]
    last_err = None
    for m in candidates:
        try:
            model = genai.GenerativeModel(m)
            resp = model.generate_content(prompt)
            sql = (resp.text or "").strip()
            if sql.startswith("```"):
                sql = sql.strip("` ").split("\n", 1)[-1]
            return sql or f"SELECT 1 as placeholder LIMIT {max_rows};"
        except gexc.NotFound as e:
            last_err = e
            continue
    raise last_err or RuntimeError("No Gemini model worked")

def summarize_result(question: str, columns, rows, max_rows_for_llm: int = 50) -> str:
    """
    Genera una respuesta EN TEXTO usando SOLO los datos entregados.
    No inventa nada: si no hay filas, lo dice. Mantiene el español.
    """
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        # Sin API key, devolvemos un resumen básico
        if not rows:
            return "No hay resultados para esa consulta."
        return f"Se encontraron {len(rows)} filas. Ejemplo: {dict(zip(columns, rows[0]))}."
    genai.configure(api_key=api_key)

    safe_rows = rows[:max_rows_for_llm]
    payload = {
        "columns": columns,
        "rows": safe_rows,
        "total_rows": len(rows),
    }
    system = """Eres un analista de datos.
Responde en español, en 1 a 3 oraciones, usando EXCLUSIVAMENTE las filas provistas.
Si no hay datos, dilo claramente. No inventes números ni columnas que no existan.
Si hay precios o cantidades, menciona los valores visibles o rangos deducibles de las filas."""
    user = f"""Pregunta del usuario:
{question}

Tabla (JSON):
{json.dumps(payload, ensure_ascii=False)}"""

    model = genai.GenerativeModel("gemini-flash-latest")
    resp = model.generate_content(textwrap.dedent(system + "\n\n" + user).strip())
    ans = (resp.text or "").strip()
    if not ans:
        if not rows:
            return "No hay resultados para esa consulta."
        return f"Se obtuvieron {len(rows)} filas. Ejemplo de fila: {dict(zip(columns, rows[0]))}."
    return ans