FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código fuente
COPY . .

# Crear directorios
RUN mkdir -p /app/media /app/staticfiles

# ⚠️ Dar permisos de ejecución al script
RUN chmod +x /app/start.sh

# Exponer puerto
EXPOSE 8000

# Usar el script de inicio
CMD ["/app/start.sh"]