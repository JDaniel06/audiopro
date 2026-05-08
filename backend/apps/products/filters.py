import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.NumberFilter(field_name='category__id')
    brand = django_filters.CharFilter(field_name='brand', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status')
    featured = django_filters.BooleanFilter(field_name='featured')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'status', 'featured', 'min_price', 'max_price']
