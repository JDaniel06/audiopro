"""
Modelos de pagos - AudioPro
"""
from django.db import models
from django.conf import settings
from apps.orders.models import Order


class Payment(models.Model):
    """Registro de pago asociado a un pedido."""

    class Method(models.TextChoices):
        STRIPE = 'stripe', 'Stripe (Tarjeta)'
        TRANSFER = 'transfer', 'Transferencia Bancaria'
        CASH = 'cash', 'Efectivo'
        OTHER = 'other', 'Otro'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        UNDER_REVIEW = 'under_review', 'En Revisión'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
        REFUNDED = 'refunded', 'Reembolsado'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments'
    )
    method = models.CharField(max_length=15, choices=Method.choices)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Stripe
    stripe_session_id = models.CharField(max_length=200, blank=True)
    stripe_payment_intent = models.CharField(max_length=200, blank=True)

    # Comprobante manual
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Admin
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reviewed_payments'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pago {self.order.order_number} - {self.get_status_display()}'


class PaymentEvidence(models.Model):
    """Comprobante/evidencia de pago adjuntado por el cliente."""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='evidences')
    file = models.FileField(upload_to='payment_evidences/%Y/%m/')
    file_name = models.CharField(max_length=200)
    description = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evidencia de pago'
        verbose_name_plural = 'Evidencias de pago'

    def __str__(self):
        return f'Evidencia de {self.payment.order.order_number}'
