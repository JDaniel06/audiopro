# 🎵 Audio Store Pro

Plataforma de gestión de pedidos de equipos de audio profesional.

**Stack:** Django REST Framework + Streamlit + SQLite (práctica) / PostgreSQL (producción)

---

## Inicio Rápido (Ambiente de Práctica)

### Requisitos
- Python 3.10+
- pip

### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/audio-store-pro.git
cd audio-store-pro
```

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias del backend
```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar base de datos y datos iniciales
```bash
python manage.py migrate
python manage.py seed_data          # Carga productos de ejemplo
python manage.py createsuperuser    # O usa el script automático
```

### 5. Crear admin automáticamente
```bash
python manage.py shell -c "
from apps.users.models import User
User.objects.create_superuser(
    username='admin', email='admin@audiostore.com',
    password='admin123', first_name='Admin',
    last_name='AudioStore', role='admin'
)
"
```

### 6. Iniciar el backend
```bash
python manage.py runserver
# Disponible en: http://localhost:8000
# Admin Django:  http://localhost:8000/admin
```

### 7. Instalar dependencias del frontend
```bash
cd ../frontend
pip install -r requirements.txt
```

### 8. Iniciar el frontend
```bash
streamlit run app.py
# Disponible en: http://localhost:8501
```

### Windows: Script automático
```bat
start_windows.bat
```

---

## Credenciales por defecto
| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@audiostore.com | admin123 |

---

## Estructura del Proyecto
```
audio-store-pro/
├── backend/
│   ├── config/          # Settings, URLs, WSGI
│   ├── apps/
│   │   ├── users/       # Usuarios y autenticación JWT
│   │   ├── products/    # Catálogo, stock, categorías
│   │   ├── orders/      # Carrito y pedidos
│   │   └── payments/    # Comprobantes de pago
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   │   ├── 1_Login.py
│   │   ├── 2_Registro.py
│   │   ├── 3_Catalogo.py
│   │   ├── 4_Detalle_Producto.py
│   │   ├── 5_Carrito.py
│   │   ├── 6_Checkout.py
│   │   ├── 7_Mis_Pedidos.py
│   │   ├── 8_Admin_Productos.py
│   │   ├── 9_Admin_Pedidos.py
│   │   ├── 10_Admin_Usuarios.py
│   │   └── 11_Reportes.py
│   ├── utils/
│   │   ├── api.py       # Cliente HTTP
│   │   └── auth.py      # Helpers de autenticación
│   ├── app.py           # Página principal
│   └── requirements.txt
├── start.sh             # Inicio Linux/Mac
├── start_windows.bat    # Inicio Windows
├── .gitignore
└── README.md
```

---

## API Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/users/auth/login/` | Login JWT |
| POST | `/api/users/auth/register/` | Registro cliente |
| GET | `/api/products/` | Catálogo de productos |
| GET | `/api/products/{id}/` | Detalle de producto |
| GET | `/api/orders/cart/` | Ver carrito |
| POST | `/api/orders/cart/items/` | Agregar al carrito |
| POST | `/api/orders/orders/checkout/` | Confirmar pedido |
| POST | `/api/payments/` | Registrar pago |
| POST | `/api/payments/{id}/review/` | Aprobar/rechazar pago (admin) |

---

## Deploy en host gratuito

### Railway (recomendado)
1. Crear cuenta en [railway.app](https://railway.app)
2. Conectar repositorio GitHub
3. Agregar servicio PostgreSQL
4. Configurar variables de entorno
5. Deploy automático

### Render
1. Crear cuenta en [render.com](https://render.com)
2. New Web Service → conectar repo
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn config.wsgi:application`

---

## Repositorio GitHub

```bash
git init
git add .
git commit -m "feat: Audio Store Pro - proyecto completo"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/audio-store-pro.git
git push -u origin main
```
