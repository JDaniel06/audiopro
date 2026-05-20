# 🎵 AudioPro — Sistema de Gestión de Pedidos

Plataforma completa para la venta de equipos de audio profesional.

**Stack:** Django REST Framework · Streamlit · PostgreSQL · Docker

---

## Estructura del Proyecto

```
AudioPro/
├── backend/                  # Django REST Framework
│   ├── apps/
│   │   ├── users/            # Usuarios y autenticación
│   │   ├── products/         # Catálogo de productos
│   │   ├── orders/           # Carrito y pedidos
│   │   └── payments/         # Pagos y comprobantes
│   ├── config/               # Settings, URLs, WSGI
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # Streamlit
│   ├── pages/
│   │   ├── 1_Login.py
│   │   ├── 2_Detalle_Producto.py
│   │   ├── 3_Carrito.py
│   │   ├── 4_Pago.py
│   │   ├── 5_Mis_Pedidos.py
│   │   ├── 6_Admin_Productos.py
│   │   ├── 7_Admin_Pedidos.py
│   │   ├── 8_Admin_Pagos.py
│   │   ├── 9_Admin_Usuarios.py
│   │   └── 10_Reportes.py
│   ├── utils/
│   │   ├── api.py            # Cliente HTTP
│   │   └── auth.py           # Helpers de autenticación
│   ├── app.py                # Catálogo principal
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── PLAN_DESARROLLO.md
```

---

## Inicio Rápido con Docker

```bash
# 1. Clonar y configurar variables
cp .env.example .env
# Editar .env con tus valores

# 2. Levantar todos los servicios
docker-compose up --build -d

# 3. Acceder
# Backend API:  http://localhost:8000/api/
# Admin Django: http://localhost:8000/admin/
# Frontend:     http://localhost:8501
```

---

## Desarrollo Local (sin Docker)

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Configurar base de datos PostgreSQL local
# Crear archivo .env con las variables

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
pip install -r requirements.txt

# Configurar API_BASE_URL en .env o variable de entorno
streamlit run app.py
```

---

## API Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login/` | Login JWT |
| POST | `/api/users/register/` | Registro de cliente |
| GET | `/api/products/` | Catálogo de productos |
| GET | `/api/products/{id}/` | Detalle de producto |
| GET | `/api/orders/cart/` | Ver carrito |
| POST | `/api/orders/cart/items/` | Agregar al carrito |
| POST | `/api/orders/checkout/` | Confirmar pedido |
| POST | `/api/payments/stripe_checkout/` | Pago con Stripe |
| POST | `/api/payments/create_manual/` | Pago manual |
| POST | `/api/payments/{id}/upload_evidence/` | Subir comprobante |

---

## Deploy Gratuito

### Backend → Railway
1. Crear proyecto en [railway.app](https://railway.app)
2. Conectar repositorio GitHub
3. Agregar servicio PostgreSQL
4. Configurar variables de entorno del `.env.example`
5. Railway detecta el `Dockerfile` automáticamente

### Frontend → Streamlit Cloud
1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Conectar repositorio GitHub
3. Seleccionar `frontend/app.py` como archivo principal
4. Agregar `API_BASE_URL` en los secrets de Streamlit Cloud

---

## Credenciales por Defecto (Docker)

- **Admin Django:** admin@audiopro.com / Admin1234!
- Cambiar en producción via variables de entorno `DJANGO_SUPERUSER_*`
