# tp-electiva-ai-advanced-topics

Este repositorio contiene un pequeño proyecto Django que integra un agente NL->SQL
apoyado en modelos de Google Generative (Gemini) mediante LangChain.

Este README explica cómo configurar y levantar el proyecto localmente usando Docker
y cómo preparar las variables de entorno necesarias.

## Requisitos previos

- Docker instalado en la máquina.


## Pasos rápidos

1. Copiar el archivo de ejemplo de variables de entorno:

	 Copia `.env.example` a `.env` y rellena los valores necesarios:


	 En `.env` necesitas al menos:
	 - `GEMINI_API_KEY`: tu API key para Gemini / Google Generative AI.
	 - `MODEL_GEMINI`: modelo a usar (por ejemplo `gemini-2.5-flash` o `gemini-1.5-flash`).
	 - `DB_URL`: URI de la base de datos (por defecto `sqlite:///./db/hotel.db`).

	 El repositorio incluye un `.env.example` con valores de ejemplo.

2. Construir y levantar con Docker Compose

	 
	 docker compose build
	 docker compose up
	

	 El servicio expone la app en el puerto `8000` (http://localhost:8000).

	 Nota: el `docker-compose.yml` del proyecto contiene una rutina que (si la variable
	 `FORCE_DB_RELOAD` está en `1`) regenerará `DB/hotel.db` desde `DB/schema.sql` y
	 `DB/seed.sql` cada vez que arranque el contenedor. Esto está pensado para desarrollo. Si se quiere trabajar sobre más datos, o se quiere alterar los datos para pruebas, solo se tiene que modificar desde `DB/seed.sql`, agregando, modificando, o sacando filas.



## Uso del agente

- Accedé a la ruta raíz (por defecto http://localhost:8000/) y verás un formulario para preguntar en
	lenguaje natural. El agente generará una consulta SQL, la ejecutará contra la DB
	y devolverá tanto la consulta como una explicación en lenguaje natural de los resultados.


## Problemas comunes

- Si ves errores 404 del modelo (p.ej. `models/gemini-1.5-flash-latest is not found`),
	actualiza `MODEL_GEMINI` en el `.env` a un modelo soportado (por ejemplo `gemini-2.5-flash`)
	o ejecuta `list_models.py` para ver la lista de modelos disponibles.
