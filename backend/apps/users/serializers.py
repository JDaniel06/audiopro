from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios clientes."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirmar contraseña')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'address', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = 'client'
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para ver y editar perfil de usuario."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'address', 'role', 'is_active', 'created_at']
        read_only_fields = ['id', 'email', 'role', 'created_at']


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer para administración de usuarios (solo admin)."""
    full_name = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'full_name', 'phone', 'address', 'role', 'is_active',
                  'is_staff', 'created_at', 'total_orders']
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_total_orders(self, obj):
        return obj.orders.count()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({'new_password': 'Las contraseñas no coinciden.'})
        return attrs
