# 🚀 Guía de Deploy - AudioPro

## PASO 1: Subir a GitHub ✅

```bash
# Si aún no has creado el repo en GitHub:
# 1. Ve a https://github.com/new
# 2. Nombre: AudioPro
# 3. Público o Privado (Streamlit Cloud requiere público o plan pro)
# 4. NO inicialices con README
# 5. Crea el repositorio

# Luego ejecuta (reemplaza TU_USUARIO):
git remote set-url origin https://github.com/TU_USUARIO/AudioPro.git
git push -u origin master
```

---

## PASO 2: Deploy Backend en Railway 🚂

### 2.1 Crear cuenta y proyecto
1. Ve a https://railway.app
2. **Sign up with GitHub** (usa la misma cuenta)
3. Click en **New Project**
4. Selecciona **Deploy from GitHub repo**
5. Autoriza Railway a acceder a tus repos
6. Selecciona el repo **AudioPro**

### 2.2 Configurar el servicio
Railway detectará automáticamente el `Dockerfile` en `/backend`

**IMPORTANTE:** Edita la configuración:
- Click en el servicio → **Settings**
- **Root Directory:** `backend`
- **Port:** 8000

### 2.3 Agregar PostgreSQL
1. En el mismo proyecto, click **New** → **Database** → **Add PostgreSQL**
2. Railway creará la base de datos automáticamente
3. Las variables de conexión se generan automáticamente

### 2.4 Configurar Variables de Entorno
Click en el servicio backend → **Variables** → **RAW Editor** y pega:

```env
SECRET_KEY=django-insecure-CAMBIA-ESTO-POR-UNA-CLAVE-LARGA-Y-ALEATORIA-DE-50-CARACTERES
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}},*.railway.app
DB_NAME=${{Postgres.PGDATABASE}}
DB_USER=${{Postgres.PGUSER}}
DB_PASSWORD=${{Postgres.PGPASSWORD}}
DB_HOST=${{Postgres.PGHOST}}
DB_PORT=${{Postgres.PGPORT}}
CORS_ALLOWED_ORIGINS=http://localhost:8501
DJANGO_SUPERUSER_EMAIL=admin@audiopro.com
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=Admin1234!
FRONTEND_URL=http://localhost:8501
```

**Genera una SECRET_KEY segura:**
```python
# Ejecuta esto en Python:
import secrets
print(secrets.token_urlsafe(50))
```

### 2.5 Obtener la URL del backend
1. Click en el servicio → **Settings** → **Networking**
2. Click **Generate Domain**
3. Copia la URL (ej: `https://audiopro-production.up.railway.app`)
4. **GUARDA ESTA URL** - la necesitarás para Streamlit

### 2.6 Verificar que funciona
Abre en el navegador:
- `https://TU-URL.railway.app/admin/` → Deberías ver el login de Django
- `https://TU-URL.railway.app/api/products/` → Deberías ver `{"results":[]}`

---

## PASO 3: Deploy Frontend en Streamlit Cloud ☁️

### 3.1 Preparar el proyecto
Antes de deployar, necesitamos crear un archivo de configuración:

**Crea:** `frontend/.streamlit/secrets.toml` (localmente, NO lo subas a Git)

```toml
API_BASE_URL = "https://TU-URL-DE-RAILWAY.railway.app/api"
```

### 3.2 Crear cuenta en Streamlit Cloud
1. Ve a https://share.streamlit.io
2. **Sign in with GitHub**
3. Autoriza Streamlit Cloud

### 3.3 Deploy la app
1. Click **New app**
2. Configuración:
   - **Repository:** TU_USUARIO/AudioPro
   - **Branch:** master
   - **Main file path:** `frontend/app.py`
3. Click **Advanced settings**
4. En **Secrets**, pega:

```toml
API_BASE_URL = "https://TU-URL-DE-RAILWAY.railway.app/api"
```

5. Click **Deploy!**

### 3.4 Obtener URL de Streamlit
Streamlit te dará una URL como: `https://tu-usuario-audiopro-xxxxx.streamlit.app`

**GUARDA ESTA URL**

---

## PASO 4: Actualizar CORS en Railway 🔄

Ahora que tienes la URL de Streamlit, actualiza el backend:

1. Ve a Railway → Tu proyecto → Servicio backend
2. **Variables** → Edita `CORS_ALLOWED_ORIGINS`:

```
CORS_ALLOWED_ORIGINS=https://tu-usuario-audiopro-xxxxx.streamlit.app
```

3. También actualiza `FRONTEND_URL`:

```
FRONTEND_URL=https://tu-usuario-audiopro-xxxxx.streamlit.app
```

4. Railway redesplegará automáticamente

---

## PASO 5: Probar la aplicación 🎉

### 5.1 Acceder al frontend
Abre: `https://tu-usuario-audiopro-xxxxx.streamlit.app`

### 5.2 Crear productos de prueba
1. Ve al admin de Django: `https://tu-backend.railway.app/admin/`
2. Login: `admin@audiopro.com` / `Admin1234!`
3. Crea algunas categorías y productos

### 5.3 Probar como cliente
1. En el frontend, registra un usuario nuevo
2. Navega por el catálogo
3. Agrega productos al carrito
4. Haz un pedido de prueba

---

## 🔧 Solución de Problemas

### Error: "No se puede conectar con el servidor"
- Verifica que `API_BASE_URL` en Streamlit tenga `/api` al final
- Verifica que CORS esté configurado correctamente en Railway

### Error: "CSRF verification failed"
- Asegúrate que `ALLOWED_HOSTS` incluya tu dominio de Railway

### Error: "Database connection failed"
- Verifica que las variables `${{Postgres.*}}` estén correctamente referenciadas
- Railway debe tener el servicio PostgreSQL en el mismo proyecto

### El admin no carga estilos
- Ejecuta en Railway (via terminal o comando):
  ```bash
  python manage.py collectstatic --noinput
  ```

---

## 📊 Monitoreo

### Railway
- **Logs:** Click en el servicio → **Deployments** → Click en el último deploy
- **Métricas:** CPU, RAM, Network en tiempo real

### Streamlit Cloud
- **Logs:** Click en tu app → **Manage app** → **Logs**
- **Reboot:** Si algo falla, click en **Reboot app**

---

## 🔐 Seguridad para Producción

Antes de compartir públicamente:

1. **Cambia las credenciales del admin**
2. **Genera una SECRET_KEY fuerte**
3. **Configura Stripe** (si vas a aceptar pagos reales):
   - Obtén keys de producción en https://dashboard.stripe.com
   - Agrega a Railway:
     ```
     STRIPE_SECRET_KEY=sk_live_...
     STRIPE_PUBLISHABLE_KEY=pk_live_...
     ```

---

## 🎯 URLs Finales

Anota tus URLs aquí:

- **Frontend (Streamlit):** https://_____________________.streamlit.app
- **Backend API (Railway):** https://_____________________.railway.app/api/
- **Admin Django:** https://_____________________.railway.app/admin/

---

## 💰 Costos

- **Railway:** 500 horas/mes gratis ($5/mes después)
- **Streamlit Cloud:** Ilimitado para apps públicas
- **PostgreSQL en Railway:** Incluido en el plan gratuito

**Total: $0/mes** (dentro de los límites gratuitos)
