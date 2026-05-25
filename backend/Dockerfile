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

# ⚠️ EJECUTAR MIGRACIONES
# RUN python manage.py migrate --noinput

# Colectar estáticos
# RUN python manage.py collectstatic --noinput

# Exponer puerto
EXPOSE 8000

# Comando de producción con Gunicorn
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2