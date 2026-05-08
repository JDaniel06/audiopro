from django.contrib import admin
from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'stock', 'status', 'featured']
    list_filter = ['status', 'category', 'featured', 'brand']
    search_fields = ['name', 'brand', 'model_number']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['status', 'featured', 'stock']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'slug', 'brand', 'model_number', 'category', 'image')
        }),
        ('Descripción', {
            'fields': ('description', 'specifications')
        }),
        ('Precio y Stock', {
            'fields': ('price', 'stock', 'status', 'featured')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at']
