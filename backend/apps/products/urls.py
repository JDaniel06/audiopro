"""
URLs de pedidos y carrito - AudioPro
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet

router = DefaultRouter()
# CartItemViewSet se registra bajo 'items'
router.register(r'categories', CategoryViewSet)
# OrderViewSet se registra en la raíz
router.register(r'', ProductViewSet) # o r'products'

urlpatterns = [
    path('', include(router.urls)),
    # Vista genérica para el carrito (no es un ViewSet)
    #path('cart/', CartView.as_view(), name='cart-detail'),
]