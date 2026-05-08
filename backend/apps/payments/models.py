from django.db import models


class Payment(models.Model):
    """Registro de pago asociado a un pedido."""

    METHOD_CHOICES = [
        ('transfer', 'Transferencia Bancaria'),
        ('mobile_pay', 'Pago Móvil'),
        ('cash', 'Efectivo'),
        ('other', 'Otro'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pendiente de Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
    ]

    order = models.OneToOneField(
        'orders.Order', on_delete=models.CASCADE, related_name='payment'
    )
    user = models.ForeignKey(
        'users.User', on_delete=models.PROTECT, related_name='payments'
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='transfer')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia / Nro. de confirmación')
    voucher = models.FileField(
        upload_to='payment_vouchers/',
        blank=True, null=True,
        verbose_name='Comprobante de pago'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, verbose_name='Notas del administrador')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pago #{self.order.order_number} - {self.status}'
