from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'', ProductViewSet, basename='products')
router.register(r'stock/movements', StockMovementViewSet, basename='stock-movements')

urlpatterns = [
    path('', include(router.urls)),
]
