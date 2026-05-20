"""
Modelos de productos - AudioPro
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Categoría de equipos de audio profesional."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Producto de audio profesional."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Activo'
        INACTIVE = 'inactive', 'Inactivo'
        OUT_OF_STOCK = 'out_of_stock', 'Sin Stock'

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    brand = models.CharField(max_length=100)
    model_number = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    specifications = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.brand} {self.name}'

    @property
    def is_available(self):
        return self.status == self.Status.ACTIVE and self.stock > 0

    def reduce_stock(self, quantity):
        """Reduce el stock al confirmar un pedido."""
        if self.stock < quantity:
            raise ValueError(f'Stock insuficiente para {self.name}. Disponible: {self.stock}')
        self.stock -= quantity
        if self.stock == 0:
            self.status = self.Status.OUT_OF_STOCK
        self.save()

    def restore_stock(self, quantity):
        """Restaura stock al cancelar un pedido."""
        self.stock += quantity
        if self.status == self.Status.OUT_OF_STOCK and self.stock > 0:
            self.status = self.Status.ACTIVE
        self.save()
