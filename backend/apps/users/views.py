"""
Vistas de usuarios - AudioPro
"""
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    UserAdminSerializer,
    ChangePasswordSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Registro de nuevos clientes."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': 'Usuario registrado exitosamente.', 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """Perfil del usuario autenticado."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Cambio de contraseña del usuario autenticado."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Contraseña actualizada exitosamente.'})


class UserAdminViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios para el administrador."""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active', 'city', 'country']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['created_at', 'email', 'first_name']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar o desactivar un usuario."""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_str = 'activado' if user.is_active else 'desactivado'
        return Response({'message': f'Usuario {status_str} exitosamente.', 'is_active': user.is_active})

    @action(detail=False, methods=['get'])
    def clients(self, request):
        """Listado solo de clientes (para reporte)."""
        clients = self.queryset.filter(role=User.Role.CLIENT)
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(clients, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de usuarios para dashboard."""
        from django.utils import timezone
        from datetime import timedelta
        total = User.objects.filter(role=User.Role.CLIENT).count()
        active = User.objects.filter(role=User.Role.CLIENT, is_active=True).count()
        last_30 = User.objects.filter(
            role=User.Role.CLIENT,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        return Response({
            'total_clients': total,
            'active_clients': active,
            'new_last_30_days': last_30,
        })
