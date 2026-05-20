"""
Serializers de productos - AudioPro
"""
from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'product_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_product_count(self, obj):
        return obj.products.filter(status=Product.Status.ACTIVE).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer liviano para listado de productos."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_available = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'model_number',
            'short_description', 'price', 'stock', 'status',
            'category_name', 'is_available', 'image_url', 'created_at'
        ]

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
    is_available = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'model_number',
            'description', 'short_description', 'price', 'stock',
            'status', 'category', 'category_id', 'specifications',
            'is_available', 'image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class StockUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar stock."""
    quantity = serializers.IntegerField(min_value=0)
    operation = serializers.ChoiceField(
        choices=['set', 'add', 'subtract'],
        default='set'
    )
