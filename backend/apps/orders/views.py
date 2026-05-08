from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer, OrderSerializer,
    CreateOrderSerializer, UpdateOrderStatusSerializer
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

    def create(self, request):
        """Agregar producto al carrito."""
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = self.get_cart()
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        from apps.products.models import Product
        product = Product.objects.get(id=product_id)

        if product.stock < quantity:
            return Response(
                {'error': f'Stock insuficiente. Disponible: {product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Actualizar cantidad de un ítem."""
        cart = self.get_cart()
        try:
            item = CartItem.objects.get(id=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity', 1)
        if int(quantity) < 1:
            item.delete()
            return Response({'message': 'Ítem eliminado del carrito.'})

        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item).data)

    def destroy(self, request, pk=None):
        """Eliminar ítem del carrito."""
        cart = self.get_cart()
        try:
            item = CartItem.objects.get(id=pk, cart=cart)
            item.delete()
            return Response({'message': 'Ítem eliminado.'}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Ítem no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

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

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user=user)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        """Crear pedido desde el carrito."""
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        if not cart.items.exists():
            return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar stock
        for item in cart.items.select_related('product').all():
            if item.product.stock < item.quantity:
                return Response(
                    {'error': f'Stock insuficiente para {item.product.name}. Disponible: {item.product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crear pedido
        order = Order.objects.create(
            user=request.user,
            notes=serializer.validated_data.get('notes', ''),
            shipping_address=serializer.validated_data.get('shipping_address', request.user.address or ''),
        )

        total = 0
        for item in cart.items.select_related('product').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            item.product.reduce_stock(item.quantity)
            total += item.subtotal

        order.subtotal = total
        order.total = total
        order.save()

        # Vaciar carrito
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        """Actualizar estado del pedido (admin)."""
        order = self.get_object()
        serializer = UpdateOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data['status']
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def sales_report(self, request):
        """Datos para reporte de ventas."""
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncMonth

        orders = Order.objects.filter(status__in=['paid', 'processing', 'shipped', 'delivered'])

        monthly = (
            orders.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_sales=Sum('total'), order_count=Count('id'))
            .order_by('month')
        )

        return Response({
            'monthly_sales': list(monthly),
            'total_revenue': orders.aggregate(Sum('total'))['total__sum'] or 0,
            'total_orders': orders.count(),
        })
