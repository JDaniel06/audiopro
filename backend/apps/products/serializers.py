from rest_framework import serializers
from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'slug', 'is_active', 'product_count']

    def get_product_count(self, obj):
        return obj.products.filter(status='active').count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado de productos."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'brand', 'model_number', 'category_name',
                  'price', 'stock', 'status', 'is_available', 'featured', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalle de producto."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    is_available = serializers.BooleanField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'brand', 'model_number', 'category', 'category_id',
                  'description', 'specifications', 'price', 'stock', 'status',
                  'is_available', 'featured', 'image', 'image_url', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer para movimientos de stock."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'product_name', 'movement_type', 'quantity',
                  'notes', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']


class AddStockSerializer(serializers.Serializer):
    """Serializer para agregar stock a un producto."""
    quantity = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(required=False, allow_blank=True)
