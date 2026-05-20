"""
Serializers de carrito y pedidos - AudioPro
"""
from rest_framework import serializers
from apps.products.serializers import ProductListSerializer
from .models import Cart, CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['id', 'added_at']

    def validate_product_id(self, value):
        from apps.products.models import Product
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError('Producto no encontrado.')
        if not product.is_available:
            raise serializers.ValidationError('Producto no disponible.')
        return value

    def validate(self, attrs):
        from apps.products.models import Product
        product = Product.objects.get(pk=attrs['product_id'])
        if attrs.get('quantity', 1) > product.stock:
            raise serializers.ValidationError(
                {'quantity': f'Solo hay {product.stock} unidades disponibles.'}
            )
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_brand',
                  'quantity', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'user_name',
            'status', 'status_display', 'subtotal', 'tax', 'total',
            'shipping_address', 'notes', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'user', 'subtotal', 'tax', 'total',
                            'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    """Serializer para crear pedido desde el carrito."""
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar estado de pedido (admin)."""
    status = serializers.ChoiceField(choices=Order.Status.choices)
    notes = serializers.CharField(required=False, allow_blank=True)
