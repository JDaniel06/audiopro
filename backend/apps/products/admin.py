from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'stock', 'status', 'created_at']
    list_filter = ['status', 'category', 'brand']
    search_fields = ['name', 'brand', 'model_number']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'status']
    readonly_fields = ['created_at', 'updated_at']
