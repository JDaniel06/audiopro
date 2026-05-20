from django.contrib import admin
from .models import Payment, PaymentEvidence


class PaymentEvidenceInline(admin.TabularInline):
    model = PaymentEvidence
    extra = 0
    readonly_fields = ['uploaded_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'user', 'method', 'status', 'amount', 'created_at']
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['order__order_number', 'user__email', 'reference_number']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at']
    inlines = [PaymentEvidenceInline]
