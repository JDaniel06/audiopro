"""
Vistas de productos - AudioPro
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import rest_framework as filters

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    StockUpdateSerializer,
)


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Product
        fields = ['status', 'brand', 'category', 'min_price', 'max_price']


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD de categorías."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD de productos con acciones adicionales."""
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand', 'model_number', 'description']
    ordering_fields = ['price', 'created_at', 'name', 'stock']
    ordering = ['-created_at']

    def get_queryset(self):
        # Clientes solo ven productos activos
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Product.objects.select_related('category').all()
        return Product.objects.select_related('category').filter(status=Product.Status.ACTIVE)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_stock(self, request, pk=None):
        """Actualizar stock de un producto."""
        product = self.get_object()
        serializer = StockUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        qty = serializer.validated_data['quantity']
        op = serializer.validated_data['operation']

        if op == 'set':
            product.stock = qty
        elif op == 'add':
            product.stock += qty
        elif op == 'subtract':
            if product.stock < qty:
                return Response(
                    {'error': 'No hay suficiente stock para restar.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            product.stock -= qty

        # Actualizar estado según stock
        if product.stock == 0:
            product.status = Product.Status.OUT_OF_STOCK
        elif product.status == Product.Status.OUT_OF_STOCK:
            product.status = Product.Status.ACTIVE
        product.save()

        return Response({
            'message': 'Stock actualizado.',
            'stock': product.stock,
            'status': product.status
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_status(self, request, pk=None):
        """Activar o desactivar un producto."""
        product = self.get_object()
        if product.status == Product.Status.ACTIVE:
            product.status = Product.Status.INACTIVE
        elif product.status == Product.Status.INACTIVE:
            product.status = Product.Status.ACTIVE
        else:
            return Response(
                {'error': 'No se puede cambiar estado de producto sin stock.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        product.save()
        return Response({'message': f'Producto {product.status}.', 'status': product.status})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Estadísticas de productos para dashboard."""
        total = Product.objects.count()
        active = Product.objects.filter(status=Product.Status.ACTIVE).count()
        inactive = Product.objects.filter(status=Product.Status.INACTIVE).count()
        out_of_stock = Product.objects.filter(status=Product.Status.OUT_OF_STOCK).count()
        low_stock = Product.objects.filter(stock__lte=5, status=Product.Status.ACTIVE).count()
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
        })
