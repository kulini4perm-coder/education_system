from django.urls import path
from users.apps import UsersConfig
from users.views import UserProfileUpdateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path('profile/<int:pk>/', UserProfileUpdateAPIView.as_view(), name='user-profile'),
]
