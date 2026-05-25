"""
URLs de pedidos y carrito - AudioPro
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet, OrderViewSet

router = DefaultRouter()
# CartItemViewSet se registra bajo 'items'
router.register(r'items', CartItemViewSet, basename='cart-item')
# OrderViewSet se registra en la raíz
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    # Vista genérica para el carrito (no es un ViewSet)
    path('cart/', CartView.as_view(), name='cart-detail'),
]