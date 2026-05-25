#!/bin/bash

# Ejecutar migraciones
python manage.py migrate --noinput

# Colectar estáticos
python manage.py collectstatic --noinput

# Iniciar Gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2