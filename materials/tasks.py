from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from materials.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """ Фоновая задача поиска всех подписчиков курса и отправления им email """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден."

    # Находим все подписки на этот курс
    subscriptions = Subscription.objects.filter(course=course)

    # Собираем email-адреса
    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if not recipient_list:
        return f"У курса '{course.title}' нет активных подписчиков с email."

    # Отправляем письма
    send_mail(
        subject=f"Обновление материалов курса '{course.title}'",
        message=f"Здравствуйте! Материалы курса '{course.title}' были обновлены.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )

    return f"Уведомления об обновлении курса '{course.title}' успешно отправлены {len(recipient_list)} пользователям."
