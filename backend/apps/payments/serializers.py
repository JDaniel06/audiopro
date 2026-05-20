"""
Serializers de pagos - AudioPro
"""
from rest_framework import serializers
from .models import Payment, PaymentEvidence


class PaymentEvidenceSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = PaymentEvidence
        fields = ['id', 'file', 'file_url', 'file_name', 'description', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class PaymentSerializer(serializers.ModelSerializer):
    evidences = PaymentEvidenceSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'user', 'user_email',
            'method', 'method_display', 'status', 'status_display',
            'amount', 'stripe_session_id', 'stripe_payment_intent',
            'reference_number', 'notes', 'evidences',
            'reviewed_by', 'reviewed_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'amount', 'stripe_session_id', 'stripe_payment_intent',
            'reviewed_by', 'reviewed_at', 'created_at', 'updated_at'
        ]


class PaymentCreateSerializer(serializers.Serializer):
    """Crear pago manual (transferencia/efectivo)."""
    order_id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=[
        ('transfer', 'Transferencia Bancaria'),
        ('cash', 'Efectivo'),
        ('other', 'Otro'),
    ])
    reference_number = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_order_id(self, value):
        from apps.orders.models import Order
        try:
            order = Order.objects.get(pk=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Pedido no encontrado.')
        if hasattr(order, 'payment'):
            raise serializers.ValidationError('Este pedido ya tiene un pago registrado.')
        return value


class PaymentReviewSerializer(serializers.Serializer):
    """Revisar pago (admin)."""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['action'] == 'reject' and not attrs.get('rejection_reason'):
            raise serializers.ValidationError(
                {'rejection_reason': 'Debe indicar el motivo del rechazo.'}
            )
        return attrs


class StripeCheckoutSerializer(serializers.Serializer):
    """Iniciar sesión de pago con Stripe."""
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        from apps.orders.models import Order
        try:
            order = Order.objects.get(pk=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Pedido no encontrado.')
        return value
