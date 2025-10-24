# Esto es simplemente un script para listar los modelos que se pueden usar.
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
assert api_key, "Falta GEMINI_API_KEY en .env"
genai.configure(api_key=api_key)

print("Modelos que soportan generateContent:\n")
for m in genai.list_models():
    methods = getattr(m, "supported_generation_methods", []) or []
    if "generateContent" in methods:
        # m.name suele venir como 'models/gemini-1.5-flash-latest'
        print(f"- {m.name}")
