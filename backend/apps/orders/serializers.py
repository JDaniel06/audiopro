from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from apps.products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'product_detail', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['id', 'added_at']

    def validate_product_id(self, value):
        from apps.products.models import Product
        try:
            product = Product.objects.get(id=value, status='active')
        except Product.DoesNotExist:
            raise serializers.ValidationError('Producto no disponible.')
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('La cantidad debe ser al menos 1.')
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_brand',
                  'quantity', 'unit_price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user_email', 'user_name', 'status',
                  'status_display', 'subtotal', 'total', 'notes',
                  'shipping_address', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'order_number', 'subtotal', 'total', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer para crear pedido desde el carrito."""
    notes = serializers.CharField(required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)


class UpdateOrderStatusSerializer(serializers.Serializer):
    """Serializer para actualizar estado de pedido (admin)."""
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
