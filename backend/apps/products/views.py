from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Category, Product, StockMovement
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    StockMovementSerializer, AddStockSerializer
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD de categorías."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]


class ProductViewSet(viewsets.ModelViewSet):
    """CRUD de productos con filtros y búsqueda."""
    queryset = Product.objects.select_related('category').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand', 'model_number', 'description']
    ordering_fields = ['price', 'name', 'created_at', 'stock']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Clientes solo ven productos activos
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            qs = qs.filter(status='active')
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def add_stock(self, request, pk=None):
        """Agregar stock a un producto."""
        product = self.get_object()
        serializer = AddStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']
        notes = serializer.validated_data.get('notes', '')

        product.add_stock(quantity)

        StockMovement.objects.create(
            product=product,
            movement_type='in',
            quantity=quantity,
            notes=notes,
            created_by=request.user
        )

        return Response({
            'message': f'Stock actualizado. Nuevo stock: {product.stock}',
            'stock': product.stock
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_status(self, request, pk=None):
        """Activar o desactivar un producto."""
        product = self.get_object()
        if product.status == 'active':
            product.status = 'inactive'
        elif product.status == 'inactive':
            product.status = 'active'
        product.save()
        return Response({'message': f'Producto {product.status}', 'status': product.status})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def featured(self, request):
        """Productos destacados."""
        products = Product.objects.filter(status='active', featured=True)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """Historial de movimientos de stock (solo admin)."""
    queryset = StockMovement.objects.select_related('product', 'created_by').all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'movement_type']
    ordering = ['-created_at']
