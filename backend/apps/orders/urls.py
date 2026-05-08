from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartView, CartItemViewSet, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/', CartItemViewSet.as_view({'post': 'create'}), name='cart-items'),
    path('cart/items/<int:pk>/', CartItemViewSet.as_view({'put': 'update', 'delete': 'destroy'}), name='cart-item-detail'),
    path('cart/items/clear/', CartItemViewSet.as_view({'delete': 'clear'}), name='cart-clear'),
    path('', include(router.urls)),
]
