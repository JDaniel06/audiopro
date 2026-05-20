"""
Vistas de carrito y pedidos - AudioPro
"""
from decimal import Decimal
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
)


class CartView(generics.RetrieveAPIView):
    """Ver el carrito del usuario autenticado."""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemViewSet(viewsets.ViewSet):
    """Gestión de ítems del carrito."""
    permission_classes = [IsAuthenticated]

    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request):
        cart = self.get_cart()
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        """Agregar producto al carrito."""
        cart = self.get_cart()
        serializer = CartItemSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)
        product = Product.objects.get(pk=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            new_qty = item.quantity + quantity
            if new_qty > product.stock:
                return Response(
                    {'error': f'Solo hay {product.stock} unidades disponibles.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            item.quantity = new_qty
            item.save()

        cart_serializer = CartSerializer(cart, context={'request': request})
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        """Actualizar cantidad de un ítem."""
        cart = self.get_cart()
        try:
            item = CartItem.objects.get(pk=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is None or int(quantity) < 1:
            return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

        quantity = int(quantity)
        if quantity > item.product.stock:
            return Response(
                {'error': f'Solo hay {item.product.stock} unidades disponibles.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item, context={'request': request}).data)

    def destroy(self, request, pk=None):
        """Eliminar ítem del carrito."""
        cart = self.get_cart()
        try:
            item = CartItem.objects.get(pk=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Vaciar el carrito."""
        cart = self.get_cart()
        cart.items.all().delete()
        return Response({'message': 'Carrito vaciado.'})


class OrderViewSet(viewsets.ModelViewSet):
    """Gestión de pedidos."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['order_number']
    ordering_fields = ['created_at', 'total']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.select_related('user').prefetch_related('items__product').all()
        return Order.objects.select_related('user').prefetch_related('items__product').filter(user=user)

    def get_permissions(self):
        if self.action in ['update_status']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Crear pedido desde el carrito."""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar stock
        for item in cart.items.select_related('product').all():
            if not item.product.is_available:
                return Response(
                    {'error': f'El producto "{item.product.name}" no está disponible.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if item.quantity > item.product.stock:
                return Response(
                    {'error': f'Stock insuficiente para "{item.product.name}". Disponible: {item.product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Calcular totales
        subtotal = cart.total
        tax = subtotal * Decimal('0.16')  # IVA 16%
        total = subtotal + tax

        # Crear pedido
        order = Order.objects.create(
            user=request.user,
            status=Order.Status.PAYMENT_PENDING,
            subtotal=subtotal,
            tax=tax,
            total=total,
            shipping_address=serializer.validated_data.get('shipping_address', request.user.address),
            notes=serializer.validated_data.get('notes', '')
        )

        # Crear ítems y reducir stock
        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            item.product.reduce_stock(item.quantity)

        # Vaciar carrito
        cart.items.all().delete()

        return Response(
            OrderSerializer(order, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Actualizar estado de un pedido (admin)."""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_status = order.status
        new_status = serializer.validated_data['status']

        # Si se cancela, restaurar stock
        if new_status == Order.Status.CANCELLED and old_status != Order.Status.CANCELLED:
            for item in order.items.select_related('product').all():
                item.product.restore_stock(item.quantity)

        order.status = new_status
        if serializer.validated_data.get('notes'):
            order.notes = serializer.validated_data['notes']
        order.save()

        return Response(OrderSerializer(order, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Estadísticas de pedidos para dashboard."""
        from django.db.models import Sum, Count
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        last_30 = timezone.now() - timedelta(days=30)

        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(
            status__in=[Order.Status.PAID, Order.Status.DELIVERED]
        ).aggregate(total=Sum('total'))['total'] or 0

        orders_last_30 = Order.objects.filter(created_at__gte=last_30).count()
        revenue_last_30 = Order.objects.filter(
            created_at__gte=last_30,
            status__in=[Order.Status.PAID, Order.Status.DELIVERED]
        ).aggregate(total=Sum('total'))['total'] or 0

        by_status = Order.objects.values('status').annotate(count=Count('id'))

        return Response({
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'orders_last_30_days': orders_last_30,
            'revenue_last_30_days': float(revenue_last_30),
            'by_status': list(by_status),
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def sales_by_month(self, request):
        """Ventas agrupadas por mes (para gráfica)."""
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth

        sales = (
            Order.objects
            .filter(status__in=[Order.Status.PAID, Order.Status.DELIVERED])
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total=Sum('total'), count=Sum('id'))
            .order_by('month')
        )
        return Response(list(sales))

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def top_products(self, request):
        """Productos más vendidos."""
        from django.db.models import Sum
        top = (
            OrderItem.objects
            .values('product__id', 'product__name', 'product__brand')
            .annotate(total_sold=Sum('quantity'), total_revenue=Sum('subtotal'))
            .order_by('-total_sold')[:10]
        )
        return Response(list(top))
