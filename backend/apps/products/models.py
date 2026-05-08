from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Categoría de equipos de audio."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    slug = models.SlugField(unique=True)
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

    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('out_of_stock', 'Sin Stock'),
    ]

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='products', verbose_name='Categoría'
    )
    name = models.CharField(max_length=200, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=100, verbose_name='Marca')
    model_number = models.CharField(max_length=100, blank=True, verbose_name='Modelo')
    description = models.TextField(verbose_name='Descripción')
    specifications = models.JSONField(default=dict, blank=True, verbose_name='Especificaciones técnicas')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Precio'
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='Stock')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Imagen')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active', verbose_name='Estado')
    featured = models.BooleanField(default=False, verbose_name='Destacado')
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
        return self.status == 'active' and self.stock > 0

    def reduce_stock(self, quantity):
        """Reduce el stock al confirmar un pedido."""
        if self.stock < quantity:
            raise ValueError(f'Stock insuficiente para {self.name}. Disponible: {self.stock}')
        self.stock -= quantity
        if self.stock == 0:
            self.status = 'out_of_stock'
        self.save()

    def add_stock(self, quantity):
        """Agrega stock al producto."""
        self.stock += quantity
        if self.status == 'out_of_stock' and self.stock > 0:
            self.status = 'active'
        self.save()


class StockMovement(models.Model):
    """Registro de movimientos de stock."""

    MOVEMENT_TYPES = [
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjustment', 'Ajuste'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=15, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'users.User', on_delete=models.SET_NULL, null=True, related_name='stock_movements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.product.name} - {self.movement_type} ({self.quantity})'
