# tp-electiva-ai-advanced-topics

Este repositorio contiene un pequeño proyecto **Django** que integra un agente **NL → SQL** apoyado en modelos **Google Generative (Gemini)** mediante **LangChain**.

Este documento explica cómo configurar y levantar el proyecto localmente usando **Docker**, además de detallar las variables de entorno necesarias.


## Requisitos previos

Para poder ejecutar el proyecto correctamente, es necesario tener instalado:

- **Docker**
- **Docker Compose**

Ambas herramientas deben estar disponibles en tu entorno de desarrollo.


## Pasos rápidos

### 1. Crear archivo `.env`

Primero, crear un nuevo archivo llamado `.env` en la raíz del proyecto y copiar dentro el contenido del archivo de ejemplo `.env.example`.

```bash
cp .env.example .env
```

Luego, completar los valores necesarios según el entorno.  
En particular, asegurarse de definir:

- `GEMINI_API_KEY`: API key de Gemini / Google Generative AI.
- `MODEL_GEMINI`: modelo a usar (por ejemplo `gemini-2.5-flash` o `gemini-1.5-flash`).
- `DB_URL`: URI de la base de datos (por defecto `sqlite:///./db/hotel.db`).

El archivo `.env.example` incluye ejemplos de valores válidos.

### 2. Construir y levantar los contenedores

Desde la raíz del repositorio, ejecutar los siguientes comandos:

```bash
docker-compose build
docker-compose up
```

La aplicación estará disponible en [http://localhost:8000](http://localhost:8000).

El archivo `docker-compose.yml` incluye una rutina que, si la variable `FORCE_DB_RELOAD` está configurada en `1`, regenerará automáticamente la base `DB/hotel.db` a partir de `DB/schema.sql` y `DB/seed.sql` cada vez que se inicie el contenedor.  
Esto está pensado para desarrollo.  
Si se desea probar con más datos o modificar los existentes, se puede editar directamente `DB/seed.sql`.


## Uso del agente

1. Acceder a [http://localhost:8000](http://localhost:8000)
2. Ingresar una consulta en lenguaje natural (por ejemplo, “¿Qué reservas hay para hoy?”)
3. El agente:
   - Generará la consulta SQL correspondiente.
   - La ejecutará contra la base de datos.
   - Mostrará tanto la consulta como una explicación en texto natural.


## Problemas comunes

**Error 404 de modelo**  
Ejemplo: `models/gemini-1.5-flash-latest is not found`

Verificar el valor de `MODEL_GEMINI` en el archivo `.env` y asegurarse de usar un modelo disponible (por ejemplo `gemini-2.5-flash`).

Para ver la lista de modelos disponibles, ejecutar:

```bash
python list_models.py
```
