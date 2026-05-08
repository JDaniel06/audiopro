from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Payment
from .serializers import PaymentSerializer, CreatePaymentSerializer, ReviewPaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """Gestión de pagos."""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.select_related('order', 'user').all()
        return Payment.objects.select_related('order', 'user').filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatePaymentSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save()
        # Actualizar estado del pedido a "en revisión"
        order = payment.order
        order.status = 'payment_review'
        order.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review(self, request, pk=None):
        """Admin aprueba o rechaza el pago."""
        payment = self.get_object()
        serializer = ReviewPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment.status = serializer.validated_data['status']
        payment.admin_notes = serializer.validated_data.get('admin_notes', '')
        payment.save()

        # Actualizar estado del pedido
        order = payment.order
        if payment.status == 'approved':
            order.status = 'paid'
        elif payment.status == 'rejected':
            order.status = 'pending'
        order.save()

        return Response(PaymentSerializer(payment, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def pending_review(self, request):
        """Pagos pendientes de revisión."""
        payments = Payment.objects.filter(status='pending').select_related('order', 'user')
        serializer = PaymentSerializer(payments, many=True, context={'request': request})
        return Response(serializer.data)
