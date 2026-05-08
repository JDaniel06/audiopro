from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer para ver pagos."""
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    order_total = serializers.DecimalField(source='order.total', max_digits=10, decimal_places=2, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    voucher_url = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'order_total',
            'user_email', 'user_name', 'method', 'method_display',
            'amount', 'reference', 'voucher', 'voucher_url',
            'status', 'status_display', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'admin_notes', 'created_at', 'updated_at']

    def get_voucher_url(self, obj):
        request = self.context.get('request')
        if obj.voucher and request:
            return request.build_absolute_uri(obj.voucher.url)
        return None


class CreatePaymentSerializer(serializers.ModelSerializer):
    """Serializer para que el cliente registre su pago."""

    class Meta:
        model = Payment
        fields = ['order', 'method', 'amount', 'reference', 'voucher']

    def validate_order(self, value):
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError('No tienes permiso sobre este pedido.')
        if hasattr(value, 'payment'):
            raise serializers.ValidationError('Este pedido ya tiene un pago registrado.')
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReviewPaymentSerializer(serializers.Serializer):
    """Serializer para que el admin apruebe o rechace un pago."""
    status = serializers.ChoiceField(choices=[('approved', 'Aprobado'), ('rejected', 'Rechazado')])
    admin_notes = serializers.CharField(required=False, allow_blank=True)
