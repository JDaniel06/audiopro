"""
Vistas de pagos - AudioPro
"""
import stripe
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.orders.models import Order
from .models import Payment, PaymentEvidence
from .serializers import (
    PaymentSerializer, PaymentCreateSerializer,
    PaymentReviewSerializer, PaymentEvidenceSerializer,
    StripeCheckoutSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    """Gestión de pagos."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.select_related('order', 'user').prefetch_related('evidences').all()
        return Payment.objects.select_related('order', 'user').prefetch_related('evidences').filter(user=user)

    def get_permissions(self):
        if self.action in ['review', 'stats']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def create_manual(self, request):
        """Registrar pago manual (transferencia/efectivo)."""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.get(pk=serializer.validated_data['order_id'])

        # Verificar que el pedido pertenece al usuario (o es admin)
        if not request.user.is_staff and order.user != request.user:
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        payment = Payment.objects.create(
            order=order,
            user=request.user,
            method=serializer.validated_data['method'],
            amount=order.total,
            reference_number=serializer.validated_data.get('reference_number', ''),
            notes=serializer.validated_data.get('notes', ''),
            status=Payment.Status.UNDER_REVIEW,
        )
        order.status = Order.Status.PAYMENT_PENDING
        order.save()

        return Response(
            PaymentSerializer(payment, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def upload_evidence(self, request, pk=None):
        """Adjuntar comprobante de pago."""
        payment = self.get_object()

        if not request.user.is_staff and payment.user != request.user:
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        if 'file' not in request.FILES:
            return Response({'error': 'No se adjuntó ningún archivo.'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
        if file.content_type not in allowed_types:
            return Response(
                {'error': 'Tipo de archivo no permitido. Use JPG, PNG, WEBP o PDF.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Validar tamaño (5MB máximo)
        if file.size > 5 * 1024 * 1024:
            return Response({'error': 'El archivo no puede superar 5MB.'}, status=status.HTTP_400_BAD_REQUEST)

        evidence = PaymentEvidence.objects.create(
            payment=payment,
            file=file,
            file_name=file.name,
            description=request.data.get('description', '')
        )
        # Cambiar estado a revisión si estaba pendiente
        if payment.status == Payment.Status.PENDING:
            payment.status = Payment.Status.UNDER_REVIEW
            payment.save()

        return Response(
            PaymentEvidenceSerializer(evidence, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def review(self, request, pk=None):
        """Aprobar o rechazar un pago (admin)."""
        payment = self.get_object()
        serializer = PaymentReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']
        payment.reviewed_by = request.user
        payment.reviewed_at = timezone.now()

        if action_type == 'approve':
            payment.status = Payment.Status.APPROVED
            payment.order.status = Order.Status.PAID
            payment.order.save()
        else:
            payment.status = Payment.Status.REJECTED
            payment.rejection_reason = serializer.validated_data.get('rejection_reason', '')

        payment.save()
        return Response(PaymentSerializer(payment, context={'request': request}).data)

    @action(detail=False, methods=['post'])
    def stripe_checkout(self, request):
        """Crear sesión de pago con Stripe."""
        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {'error': 'Pasarela de pago no configurada.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        serializer = StripeCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = Order.objects.get(pk=serializer.validated_data['order_id'])
        if not request.user.is_staff and order.user != request.user:
            return Response({'error': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            line_items = []
            for item in order.items.select_related('product').all():
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': f'{item.product.brand} {item.product.name}'},
                        'unit_amount': int(item.unit_price * 100),
                    },
                    'quantity': item.quantity,
                })

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
                metadata={'order_id': order.id, 'order_number': order.order_number},
            )

            # Crear registro de pago
            payment, _ = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'method': Payment.Method.STRIPE,
                    'amount': order.total,
                    'stripe_session_id': session.id,
                }
            )
            if not _:
                payment.stripe_session_id = session.id
                payment.save()

            return Response({'checkout_url': session.url, 'session_id': session.id})

        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def stripe_webhook(self, request):
        """Webhook de Stripe para confirmar pagos."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            try:
                payment = Payment.objects.get(stripe_session_id=session['id'])
                payment.status = Payment.Status.APPROVED
                payment.stripe_payment_intent = session.get('payment_intent', '')
                payment.save()
                payment.order.status = Order.Status.PAID
                payment.order.save()
            except Payment.DoesNotExist:
                pass

        return Response({'status': 'ok'})

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def stats(self, request):
        """Estadísticas de pagos para dashboard."""
        from django.db.models import Sum, Count
        total = Payment.objects.count()
        approved = Payment.objects.filter(status=Payment.Status.APPROVED).count()
        pending = Payment.objects.filter(status=Payment.Status.UNDER_REVIEW).count()
        rejected = Payment.objects.filter(status=Payment.Status.REJECTED).count()
        total_collected = Payment.objects.filter(
            status=Payment.Status.APPROVED
        ).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            'total_payments': total,
            'approved': approved,
            'pending_review': pending,
            'rejected': rejected,
            'total_collected': float(total_collected),
        })
