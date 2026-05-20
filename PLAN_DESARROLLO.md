# Plan de Desarrollo - AudioPro

## Stack Tecnológico
- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** Streamlit
- **Base de Datos:** PostgreSQL
- **Contenedores:** Docker + Docker Compose
- **Hosting gratuito:** Railway / Render (backend) + Streamlit Cloud (frontend)

---

## Backlog del Producto

### ÉPICA 1: Autenticación y Usuarios
| ID | Historia de Usuario | Prioridad | Estado |
|----|---------------------|-----------|--------|
| US-01 | Como cliente quiero registrarme con email y contraseña | Alta | ✅ |
| US-02 | Como cliente quiero iniciar sesión y obtener token JWT | Alta | ✅ |
| US-03 | Como admin quiero gestionar usuarios (activar/desactivar) | Alta | ✅ |
| US-04 | Como admin quiero ver listado de clientes con filtros | Media | ✅ |

### ÉPICA 2: Catálogo de Productos
| ID | Historia de Usuario | Prioridad | Estado |
|----|---------------------|-----------|--------|
| US-05 | Como cliente quiero ver catálogo de productos activos | Alta | ✅ |
| US-06 | Como cliente quiero ver detalle de un producto | Alta | ✅ |
| US-07 | Como admin quiero agregar/editar/eliminar productos | Alta | ✅ |
| US-08 | Como admin quiero cambiar estado activo/inactivo de producto | Alta | ✅ |
| US-09 | Como admin quiero gestionar stock de productos | Alta | ✅ |

### ÉPICA 3: Carrito y Pedidos
| ID | Historia de Usuario | Prioridad | Estado |
|----|---------------------|-----------|--------|
| US-10 | Como cliente quiero agregar productos al carrito | Alta | ✅ |
| US-11 | Como cliente quiero modificar cantidades en el carrito | Alta | ✅ |
| US-12 | Como cliente quiero confirmar mi pedido | Alta | ✅ |
| US-13 | Como admin quiero ver todos los pedidos | Alta | ✅ |

### ÉPICA 4: Pagos
| ID | Historia de Usuario | Prioridad | Estado |
|----|---------------------|-----------|--------|
| US-14 | Como cliente quiero acceder a pasarela de pago (Stripe) | Alta | ✅ |
| US-15 | Como cliente quiero adjuntar comprobante de pago | Alta | ✅ |
| US-16 | Como admin quiero gestionar evidencias de pago | Alta | ✅ |
| US-17 | Como admin quiero aprobar/rechazar pagos | Alta | ✅ |

### ÉPICA 5: Reportes y Dashboard
| ID | Historia de Usuario | Prioridad | Estado |
|----|---------------------|-----------|--------|
| US-18 | Como admin quiero reporte de clientes registrados | Media | ✅ |
| US-19 | Como admin quiero reporte de ventas por período | Media | ✅ |
| US-20 | Como admin quiero dashboard con gráficas de ventas | Media | ✅ |

---

## Sprint Plan

### Sprint 1 (Semana 1-2): Base del Proyecto
- Configuración Django + DRF + PostgreSQL
- Modelos: User, Product, Category
- Autenticación JWT
- CRUD Productos (admin)

### Sprint 2 (Semana 3-4): Carrito y Pedidos
- Modelos: Cart, CartItem, Order, OrderItem
- API carrito de compras
- API pedidos
- Validación de stock

### Sprint 3 (Semana 5-6): Pagos
- Modelo Payment + PaymentEvidence
- Integración Stripe (checkout session)
- Upload de comprobantes
- Gestión admin de pagos

### Sprint 4 (Semana 7-8): Frontend Streamlit
- Página de login/registro
- Catálogo y detalle de productos
- Carrito de compras
- Checkout y pago

### Sprint 5 (Semana 9-10): Reportes y Deploy
- Dashboard con Plotly/Altair
- Reporte clientes y ventas
- Docker Compose producción
- Deploy en Railway + Streamlit Cloud

---

## Arquitectura

```
[Streamlit Frontend] <--HTTP/REST--> [Django REST API] <--> [PostgreSQL]
                                            |
                                     [Stripe API]
                                     [File Storage]
```
