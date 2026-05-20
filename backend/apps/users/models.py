"""
Modelos de usuarios - AudioPro
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario personalizado con campos adicionales para clientes."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        CLIENT = 'client', 'Cliente'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CLIENT)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Venezuela')
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
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_staff

    @property
    def full_name(self):
        return self.get_full_name() or self.email
