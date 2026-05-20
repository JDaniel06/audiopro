"""
Modelos de carrito y pedidos - AudioPro
"""
from django.db import models
from django.conf import settings
from apps.products.models import Product
from decimal import Decimal


class Cart(models.Model):
    """Carrito de compras del usuario."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    def __str__(self):
        return f'Carrito de {self.user.email}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    """Ítem dentro del carrito."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ítem de carrito'
        verbose_name_plural = 'Ítems de carrito'
        unique_together = ['cart', 'product']

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """Pedido confirmado."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PAYMENT_PENDING = 'payment_pending', 'Pago Pendiente'
        PAID = 'paid', 'Pagado'
        PROCESSING = 'processing', 'En Proceso'
        SHIPPED = 'shipped', 'Enviado'
        DELIVERED = 'delivered', 'Entregado'
        CANCELLED = 'cancelled', 'Cancelado'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders'
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    shipping_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.order_number} - {self.user.email}'

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f'AP-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Ítem dentro de un pedido."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Ítem de pedido'
        verbose_name_plural = 'Ítems de pedido'

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Pedido #{self.order.order_number})'

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
