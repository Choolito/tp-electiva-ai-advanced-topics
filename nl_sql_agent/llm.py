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
# Fallback simple cuando el LLM falla
# ---------------------------------------------------------------------
def _generate_simple_fallback(question: str, columns: list, rows: list) -> str:
    """Genera un resumen descriptivo genérico cuando el LLM falla"""
    if not rows:
        return "No se encontraron resultados que cumplan con los criterios especificados."
    
    num_results = len(rows)
    insights = []
    
    # Análisis genérico de columnas categóricas
    for col in columns:
        col_lower = col.lower()
        
        # Detectar columnas categóricas (texto con valores repetidos)
        if col_lower in ['tipo', 'estado', 'categoria', 'clase', 'nivel', 'origen', 'canal']:
            col_idx = columns.index(col)
            valores = [row[col_idx] for row in rows if row[col_idx] is not None]
            if valores:
                valor_counts = {}
                for valor in valores:
                    valor_counts[valor] = valor_counts.get(valor, 0) + 1
                
                if len(valor_counts) > 1:
                    detalle = ", ".join([f"{count} {valor}" for valor, count in valor_counts.items()])
                    insights.append(f"{col}: {detalle}")
                else:
                    insights.append(f"{col}: {valores[0]}")
        
        # Detectar columnas numéricas (precios, cantidades, etc.)
        elif col_lower in ['precio', 'costo', 'valor', 'monto', 'cantidad', 'total', 'suma']:
            col_idx = columns.index(col)
            numeros = []
            for row in rows:
                try:
                    num = float(row[col_idx])
                    numeros.append(num)
                except (ValueError, TypeError):
                    continue
            
            if numeros:
                num_min = min(numeros)
                num_max = max(numeros)
                if num_min == num_max:
                    insights.append(f"{col}: ${num_min:,.0f}")
                else:
                    insights.append(f"{col}: ${num_min:,.0f} - ${num_max:,.0f}")
        
        # Detectar columnas de fecha
        elif col_lower in ['fecha', 'fecha_inicio', 'fecha_fin', 'created_at', 'updated_at']:
            col_idx = columns.index(col)
            fechas = [row[col_idx] for row in rows if row[col_idx] is not None]
            if fechas:
                fechas_unicas = sorted(set(fechas))
                if len(fechas_unicas) > 1:
                    insights.append(f"{col}: {len(fechas_unicas)} fechas diferentes")
                else:
                    insights.append(f"{col}: {fechas_unicas[0]}")
        
        # Detectar columnas booleanas (0/1, true/false)
        elif col_lower in ['activo', 'disponible', 'confirmado', 'pagado', 'frigobar', 'jacuzzi', 'balcon']:
            col_idx = columns.index(col)
            activos = sum(1 for row in rows if row[col_idx] in [1, True, '1', 'true', 'activo', 'disponible'])
            if activos > 0:
                insights.append(f"{col}: {activos} activos")
    
    # Análisis de columnas ID (para detectar rangos)
    id_columns = [col for col in columns if col.lower() in ['id', 'numero', 'codigo']]
    for col in id_columns:
        col_idx = columns.index(col)
        ids = [row[col_idx] for row in rows if row[col_idx] is not None]
        if ids:
            try:
                ids_numericos = [int(id_val) for id_val in ids if str(id_val).isdigit()]
                if ids_numericos:
                    id_min = min(ids_numericos)
                    id_max = max(ids_numericos)
                    if id_min != id_max:
                        insights.append(f"{col}: {id_min}-{id_max}")
            except (ValueError, TypeError):
                pass
    
    # Construir respuesta descriptiva genérica
    if num_results == 1:
        respuesta = "Se encontró 1 resultado"
    else:
        respuesta = f"Se encontraron {num_results} resultados"
    
    if insights:
        respuesta += f" con {', '.join(insights)}"
    
    respuesta += "."
    
    return respuesta

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

    # Crear un prompt más específico para análisis de datos
    system = """Eres un analista de datos de hotel. Analiza los resultados y proporciona un resumen descriptivo en español."""
    
    # Preparar datos de forma más estructurada pero segura
    if len(rows) == 0:
        datos_texto = "No se encontraron resultados."
    elif len(rows) <= 5:
        # Para pocos resultados, mostrar detalles
        datos_texto = f"Se encontraron {len(rows)} resultados:\n"
        for i, row in enumerate(rows, 1):
            row_dict = dict(zip(columns, row))
            datos_texto += f"Resultado {i}: {row_dict}\n"
    else:
        # Para muchos resultados, mostrar resumen
        datos_texto = f"Se encontraron {len(rows)} resultados. Ejemplos:\n"
        for i, row in enumerate(rows[:3], 1):
            row_dict = dict(zip(columns, row))
            datos_texto += f"Ejemplo {i}: {row_dict}\n"
        datos_texto += f"... y {len(rows)-3} más."
    
    user = f"""Pregunta: {question}

Datos encontrados:
{datos_texto}

Proporciona un resumen descriptivo de los resultados en 2-3 oraciones, destacando información relevante como tipos, precios, características, etc."""

    # Probar con diferentes modelos y configuraciones
    candidates = [
        "gemini-flash-latest",
        "gemini-2.0-flash",
    ]
    
    last_err = None
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name)
            resp = model.generate_content(
                textwrap.dedent(system + "\n\n" + user).strip(),
                generation_config={
                    "temperature": 0.3,  # Temperatura moderada para creatividad
                    "max_output_tokens": 300,  # Más tokens para respuestas completas
                    "top_p": 0.9,  # Mayor diversidad
                    "top_k": 40,  # Agregar top_k para mejor calidad
                },
            )

            # Extraer texto de forma robusta
            return _extract_text_strict(resp)
            
        except RuntimeError as e:
            if "LLM_EMPTY_OUTPUT_FINISH_REASON_2" in str(e) or "LLM_BLOCKED_BY_SAFETY" in str(e):
                last_err = e
                continue  # Probar con el siguiente modelo
            else:
                raise  # Re-lanzar otros errores
        except Exception as e:
            last_err = e
            continue
    
    # Si todos los modelos fallan, usar un fallback inteligente
    if last_err and ("LLM_EMPTY_OUTPUT_FINISH_REASON_2" in str(last_err) or "LLM_BLOCKED_BY_SAFETY" in str(last_err)):
        return _generate_simple_fallback(question, columns, rows)
    
    # Si hay otro tipo de error, propagarlo
    raise last_err or RuntimeError("LLM_FAILED_ALL_MODELS")
