from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'method', 'amount', 'reference', 'status', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['order__order_number', 'user__email', 'reference']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']

    fieldsets = (
        ('Información del Pago', {
            'fields': ('order', 'user', 'method', 'amount', 'reference', 'voucher')
        }),
        ('Revisión Admin', {
            'fields': ('status', 'admin_notes')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
