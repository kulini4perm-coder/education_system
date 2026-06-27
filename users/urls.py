from django.urls import path
from users.apps import UsersConfig
from users.views import UserProfileUpdateAPIView, PaymentListAPIView

app_name = UsersConfig.name

urlpatterns = [
    path('profile/<int:pk>/', UserProfileUpdateAPIView.as_view(), name='user-profile'),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
