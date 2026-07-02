from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name="Название курса"
    )
    preview = models.ImageField(
        upload_to="materials/course_previews/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание курса"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс"
    )
    title = models.CharField(
        max_length=150,
        verbose_name="Название урока"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание урока"
    )
    preview = models.ImageField(
        upload_to="materials/lesson_previews/",
        blank=True,
        null=True,
        verbose_name="Превью (картинка)"
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.title


from django.conf import settings
from django.db import models


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = ("user", "course") # чтобы пользователь не мог подписаться на один курс дважды

    def __str__(self):
        return f"{self.user} -> {self.course}"
