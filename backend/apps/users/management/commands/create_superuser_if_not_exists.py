"""
Management command: crea el superusuario inicial si no existe.
Se ejecuta automáticamente en el arranque del contenedor Docker.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea el superusuario inicial si no existe'

    def handle(self, *args, **options):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@audiopro.com')
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin1234!')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                first_name='Admin',
                last_name='AudioPro',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS(f'Superusuario creado: {email}'))
        else:
            self.stdout.write(f'Superusuario ya existe: {email}')
