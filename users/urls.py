from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.apps import UsersConfig
from users.views import UserProfileUpdateAPIView, PaymentListAPIView, UserRegisterAPIView, PaymentCreateAPIView, \
    PaymentCheckStatusAPIView

app_name = UsersConfig.name

urlpatterns = [
    # Регистрация (доступна всем)
    path('register/', UserRegisterAPIView.as_view(), name='user-register'),
    # Авторизация / Получение JWT-токена (доступна всем)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/<int:pk>/', UserProfileUpdateAPIView.as_view(), name='user-profile'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payment/status/<int:pk>/', PaymentCheckStatusAPIView.as_view(), name='payment-status'),

]
