FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# sqlite3 para cargar schema/seed
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 ca-certificates curl bash tzdata \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencias: uv lee pyproject.toml
RUN python -m pip install --upgrade pip && pip install uv

# Copiamos deps primero para cache
COPY pyproject.toml ./
RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# Copiamos el resto del proyecto
COPY . .

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENV FORCE_DB_RELOAD=0
ENTRYPOINT ["/entrypoint.sh"]
