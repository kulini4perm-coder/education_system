from rest_framework import generics
from users.models import User, Payment
from users.serializers import UserSerializer, PaymentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter



class UserProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter] # Бэкенды для фильтрации и сортировки
    filterset_fields = ("paid_course", "paid_lesson", "payment_method") # поля для точной фильтрации
    ordering_fields = ("payment_date",) # поля для сортировки (по дате оплаты)
