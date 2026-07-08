from rest_framework import serializers
from users.models import User, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'first_name', 'last_name']
        read_only_fields = ['email']

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Payment
        fields = '__all__'


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'phone', 'city', 'avatar']

    def create(self, validated_data):
        # Извлекаем пароль из проверенных данных
        password = validated_data.pop('password')
        # Создаем пользователя
        user = User.objects.create(**validated_data)
        # Хешируем пароль и сохраняем
        user.set_password(password)
        user.save()
        return user
