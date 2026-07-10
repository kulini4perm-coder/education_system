from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import User, Payment
from users.serializers import UserSerializer, PaymentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from users.serializers import UserRegisterSerializer
from drf_spectacular.utils import extend_schema

from users.services import create_stripe_product, create_stripe_price, create_stripe_session, \
    retrieve_stripe_session_status


@extend_schema(
    summary="Просмотр и редактирование профиля пользователя",
    description="Позволяет получить детальную информацию о пользователе, а также обновить данные его профиля."
)
class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@extend_schema(
    summary="Получить список платежей",
    description=(
        "Возвращает историю платежей всех пользователей. "
        "Поддерживает фильтрацию по курсу, уроку и способу оплаты, сортировку по дате оплаты"
    )
)
class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter] # Бэкенды для фильтрации и сортировки
    filterset_fields = ("paid_course", "paid_lesson", "payment_method") # поля для точной фильтрации
    ordering_fields = ("payment_date",) # поля для сортировки (по дате оплаты)

@extend_schema(
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя в системе. Открыт для всех"
)
class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    # Открываем этот эндпоинт для неавторизованных пользователей
    permission_classes = [AllowAny]


@extend_schema(
    summary="Создание платежа и получение ссылки на оплату",
    description="Принимает ID курса или урока и сумму. Генерирует в Stripe платежную сессию и возвращает URL для оплаты."
)
class PaymentCreateAPIView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Сохраняем базовый платеж в БД
        payment = serializer.save(user=self.request.user)
        # test_user = User.objects.first() для тестирования
        # payment = serializer.save(user=test_user) для тестирования

        # Определяем имя продукта
        product_name = payment.paid_course.title if payment.paid_course else payment.paid_lesson.title

        # Интеграция со Stripe через сервисы
        product_id = create_stripe_product(product_name)
        price_id = create_stripe_price(payment.payment_amount, product_id)
        payment_url, session_id = create_stripe_session(price_id)

        # Обновляем модель платежа полученными данными от Stripe
        payment.payment_url = payment_url
        payment.session_id = session_id
        payment.save()

@extend_schema(
        summary="Проверить и обновить статус платежа",
        description="Принимает ID платежа, запрашивает актуальный статус из Stripe, обновляет его в БД и возвращает пользователю."
    )
class PaymentCheckStatusAPIView(APIView):
    # permission_classes = [AllowAny]  # Временно для теста

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)

        if payment.session_id:
            # Запрашиваем статус у Stripe
            stripe_status = retrieve_stripe_session_status(payment.session_id)
            # Синхронизируем с нашей моделью
            payment.payment_status = stripe_status
            payment.save()

            return Response({"payment_id": payment.id, "status": payment.payment_status}, status=200)

        return Response({"error": "У этого платежа нет зарегистрированной сессии Stripe."}, status=400)
