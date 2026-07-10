from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None  # Полностью удаляем поле username

    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        help_text="Укажите email (используется для входа)"
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name="Телефон"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город"
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватарка"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    CASH = 'cash'
    TRANSFER = 'transfer'
    CARD = 'card'

    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Наличные'),
        (TRANSFER, 'Перевод на счет'),
        (CARD, 'Банковская карта'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )

    paid_course = models.ForeignKey(
        'materials.Course',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        'materials.Lesson',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )

    payment_amount = models.DecimalField(
        max_length=10,
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default=CARD,
        verbose_name='Способ оплаты'
    )
    payment_url = models.URLField(
        max_length=1000,
        blank=True, null=True,
        verbose_name="Ссылка на оплату"
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии Stripe"
    )
    payment_status = models.CharField(
        max_length=50,
        default="pending",
        verbose_name="Статус платежа",
        help_text="pending, paid, canceled"
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        method_display = getattr(self, 'get_payment_method_display')()
        return f'{self.user} - {self.payment_amount} ({method_display})'



