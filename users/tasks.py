from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import User


@shared_task
def check_inactive_users():
    """Периодическая задача поиска пользователей, которые не заходили в систему более 30 дней"""
    # Вычисляем точку отсчета времени
    one_month_ago = timezone.now() - timedelta(days=30)

    # Фильтруем пользователей:
    inactive_users = User.objects.filter(
        is_active=True, # Активный
        is_superuser=False, # Не суперпользователь
        last_login__lt=one_month_ago # Дата последнего входа меньше, чем 30 дней назад
    )

    count = inactive_users.count()

    if count > 0:
        # обновляем флаг активности
        inactive_users.update(is_active=False)
        return f"Успешно заблокировано неактивных пользователей: {count}."

    return "Неактивных пользователей для блокировки не обнаружено."
