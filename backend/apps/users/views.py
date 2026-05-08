from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import User
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer,
    UserAdminSerializer, ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """Registro de nuevos usuarios clientes."""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    """Ver y actualizar perfil del usuario autenticado."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Cambiar contraseña del usuario autenticado."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Contraseña actual incorrecta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Contraseña actualizada correctamente.'})


class UserAdminViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios para administradores."""
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['created_at', 'email']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar o desactivar un usuario."""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        status_str = 'activado' if user.is_active else 'desactivado'
        return Response({'message': f'Usuario {status_str} correctamente.', 'is_active': user.is_active})

    @action(detail=False, methods=['get'])
    def clients_report(self, request):
        """Reporte de clientes para exportación."""
        clients = User.objects.filter(role='client').order_by('-created_at')
        serializer = UserAdminSerializer(clients, many=True)
        return Response(serializer.data)
