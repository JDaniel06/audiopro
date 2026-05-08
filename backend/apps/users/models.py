from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario personalizado con campos adicionales para clientes."""

    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('client', 'Cliente'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, null=True, verbose_name='Dirección')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client', verbose_name='Rol')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser
