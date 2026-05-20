"""
Serializers de usuarios - AudioPro
"""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos clientes."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone', 'address', 'city', 'country', 'password', 'password2'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = User.Role.CLIENT
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer completo de usuario (lectura)."""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone', 'address', 'city', 'country',
            'role', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'role']


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer para gestión de usuarios por el admin."""
    full_name = serializers.ReadOnlyField()
    total_orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'full_name', 'phone', 'address', 'city', 'country',
            'role', 'is_active', 'is_staff', 'created_at', 'updated_at',
            'total_orders'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_orders(self, obj):
        return obj.orders.count()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Contraseña actual incorrecta.')
        return value
