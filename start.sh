#!/bin/bash
# Script de inicio rápido para desarrollo

echo "=== Audio Store Pro - Inicio ==="

# Backend
echo ""
echo "1. Instalando dependencias del backend..."
cd backend
pip install -r requirements.txt

echo ""
echo "2. Aplicando migraciones..."
python manage.py migrate

echo ""
echo "3. Creando superusuario admin (si no existe)..."
python manage.py shell -c "
from apps.users.models import User
if not User.objects.filter(email='admin@audiostore.com').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@audiostore.com',
        password='admin123',
        first_name='Admin',
        last_name='AudioStore',
        role='admin'
    )
    print('Superusuario creado: admin@audiostore.com / admin123')
else:
    print('Superusuario ya existe.')
"

echo ""
echo "4. Cargando datos de ejemplo..."
python manage.py loaddata initial_data.json 2>/dev/null || echo "Sin datos de ejemplo."

echo ""
echo "5. Iniciando backend Django en puerto 8000..."
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Frontend
echo ""
echo "6. Instalando dependencias del frontend..."
cd ../frontend
pip install -r requirements.txt

echo ""
echo "7. Iniciando frontend Streamlit en puerto 8501..."
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "==================================="
echo "✅ Backend:  http://localhost:8000"
echo "✅ Frontend: http://localhost:8501"
echo "✅ Admin:    http://localhost:8000/admin"
echo "   Usuario:  admin@audiostore.com"
echo "   Password: admin123"
echo "==================================="

wait $BACKEND_PID $FRONTEND_PID
