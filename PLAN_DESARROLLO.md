# Plan de Desarrollo - Audio Store Pro

## Descripción del Proyecto
Plataforma de gestión de pedidos de equipos de audio profesional con backend Django REST Framework y frontend Streamlit.

---

## Stack Tecnológico
- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** Streamlit
- **Base de Datos:** PostgreSQL
- **Contenedores:** Docker + Docker Compose
- **Autenticación:** JWT (djangorestframework-simplejwt)

---

## Backlog del Producto

### ÉPICA 1: Autenticación y Usuarios
| ID | Historia de Usuario | Prioridad | Estimación |
|----|---------------------|-----------|------------|
| US-01 | Como cliente quiero registrarme con email y contraseña | Alta | 3 pts |
| US-02 | Como cliente quiero iniciar sesión y obtener token JWT | Alta | 2 pts |
| US-03 | Como admin quiero gestionar usuarios (activar/desactivar) | Alta | 3 pts |
| US-04 | Como admin quiero ver listado de clientes con filtros | Media | 2 pts |

### ÉPICA 2: Catálogo de Productos
| ID | Historia de Usuario | Prioridad | Estimación |
|----|---------------------|-----------|------------|
| US-05 | Como cliente quiero ver catálogo de productos con filtros | Alta | 3 pts |
| US-06 | Como cliente quiero ver detalle de un producto | Alta | 2 pts |
| US-07 | Como admin quiero agregar/editar/eliminar productos | Alta | 5 pts |
| US-08 | Como admin quiero cambiar estado activo/inactivo de producto | Alta | 1 pt |
| US-09 | Como admin quiero gestionar stock de productos | Alta | 3 pts |

### ÉPICA 3: Carrito y Pedidos
| ID | Historia de Usuario | Prioridad | Estimación |
|----|---------------------|-----------|------------|
| US-10 | Como cliente quiero agregar productos al carrito | Alta | 3 pts |
| US-11 | Como cliente quiero modificar cantidades en el carrito | Alta | 2 pts |
| US-12 | Como cliente quiero ver resumen del carrito | Alta | 2 pts |
| US-13 | Como cliente quiero confirmar mi pedido | Alta | 3 pts |

### ÉPICA 4: Pagos
| ID | Historia de Usuario | Prioridad | Estimación |
|----|---------------------|-----------|------------|
| US-14 | Como cliente quiero acceder a pasarela de pago (Stripe) | Alta | 5 pts |
| US-15 | Como cliente quiero adjuntar comprobante de pago | Alta | 3 pts |
| US-16 | Como admin quiero ver y gestionar evidencias de pago | Alta | 3 pts |
| US-17 | Como admin quiero aprobar/rechazar pagos | Alta | 2 pts |

### ÉPICA 5: Reportes y Dashboard
| ID | Historia de Usuario | Prioridad | Estimación |
|----|---------------------|-----------|------------|
| US-18 | Como admin quiero ver reporte de clientes | Media | 3 pts |
| US-19 | Como admin quiero ver reporte de ventas | Media | 3 pts |
| US-20 | Como admin quiero ver dashboard de ventas con gráficas | Media | 5 pts |

---

## Sprint Planning

### Sprint 1 (Semana 1-2): Fundamentos
- [ ] Configuración del proyecto Django
- [ ] Modelos de Usuario personalizado
- [ ] Autenticación JWT
- [ ] Modelos de Productos y Categorías
- [ ] Docker Compose inicial
- **US-01, US-02, US-05, US-06**

### Sprint 2 (Semana 3-4): Core del Negocio
- [ ] CRUD completo de Productos
- [ ] Gestión de Stock
- [ ] Modelos de Carrito y Pedidos
- [ ] APIs de Carrito
- **US-07, US-08, US-09, US-10, US-11, US-12, US-13**

### Sprint 3 (Semana 5-6): Pagos y Admin
- [ ] Integración pasarela de pago
- [ ] Upload de comprobantes
- [ ] Panel admin Django
- [ ] Gestión de usuarios admin
- **US-03, US-04, US-14, US-15, US-16, US-17**

### Sprint 4 (Semana 7-8): Frontend Streamlit
- [ ] Página de login/registro
- [ ] Catálogo de productos
- [ ] Detalle de producto
- [ ] Carrito de compras
- [ ] Proceso de pago
- **US-05, US-06, US-10, US-11, US-12, US-13, US-14, US-15**

### Sprint 5 (Semana 9-10): Reportes y Deploy
- [ ] Dashboard de ventas
- [ ] Reporte de clientes
- [ ] Reporte de ventas
- [ ] Docker Compose producción
- [ ] Deploy en Railway/Render
- **US-18, US-19, US-20**

---

## Criterios de Aceptación Generales
1. Todos los endpoints protegidos requieren autenticación JWT
2. El admin de Django gestiona usuarios y productos
3. Los comprobantes de pago se almacenan en el servidor
4. Los reportes exportan a CSV/Excel
5. La aplicación corre completamente en Docker
