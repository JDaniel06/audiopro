@echo off
echo === Audio Store Pro - Inicio en Windows ===

echo.
echo 1. Instalando dependencias del backend...
cd backend
pip install -r requirements.txt

echo.
echo 2. Aplicando migraciones...
python manage.py migrate

echo.
echo 3. Creando superusuario admin...
python manage.py shell -c "from apps.users.models import User; User.objects.filter(email='admin@audiostore.com').exists() or User.objects.create_superuser(username='admin', email='admin@audiostore.com', password='admin123', first_name='Admin', last_name='AudioStore', role='admin')"

echo.
echo 4. Iniciando backend en puerto 8000...
start "Django Backend" python manage.py runserver 0.0.0.0:8000

echo.
echo 5. Instalando dependencias del frontend...
cd ..\frontend
pip install -r requirements.txt

echo.
echo 6. Iniciando frontend Streamlit en puerto 8501...
start "Streamlit Frontend" streamlit run app.py --server.port 8501

echo.
echo ===================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8501
echo Admin:    http://localhost:8000/admin
echo Usuario:  admin@audiostore.com
echo Password: admin123
echo ===================================
pause
