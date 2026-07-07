from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription

User = get_user_model()


class LMSTestCase(APITestCase):

    def setUp(self) -> None:
        """Подготовка тестовых данных перед каждым тестом."""
        # Создаем обычного пользователя и пользователя-модератора
        self.user = User.objects.create(email="student@mail.ru", is_active=True)
        self.user.set_password("12345")
        self.user.save()

        self.moderator = User.objects.create(email="moderator@mail.ru", is_active=True)
        self.moderator.set_password("12345")
        self.moderator.save()

        # Создаем группу модераторов и добавляем туда пользователя
        self.moderator_group, _ = Group.objects.get_or_create(name="moderators")
        self.moderator.groups.add(self.moderator_group)

        # Создаем тестовый курс и урок, принадлежащие обычном пользователю
        self.course = Course.objects.create(
            title="Django Course",
            description="Learn Django from scratch",
            owner=self.user,
        )
        self.lesson = Lesson.objects.create(
            title="DRF Lesson",
            description="Intro to DRF views",
            course=self.course,
            owner=self.user,
            video_url="https://youtube.com",
        )

    # Тесты по CRUD

    def test_create_lesson(self):
        """ Тест на создание урока обычным пользователем """
        self.client.force_authenticate(user=self.user)  # Авторизация

        data = {
            "title": "New Test Lesson",
            "description": "Valid test lesson",
            "course": self.course.id,
            "video_url": "https://youtube.com",
        }
        url = reverse("materials:lesson-create")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.filter(title="New Test Lesson").count(), 1)

    def test_create_lesson_by_moderator_forbidden(self):
        """ Тест запрета на создание урока модератором """
        self.client.force_authenticate(user=self.moderator)

        data = {"title": "Mod Lesson", "course": self.course.id}
        url = reverse("materials:lesson-create")
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons(self):
        """ Тест вывода списка уроков """
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Так как включена пагинация, проверяем структуру словаря
        self.assertIn("results", response.json())
        self.assertEqual(len(response.json()["results"]), 1)

    def test_retrieve_lesson(self):
        """ Тест просмотра деталей отдельного урока """
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:lesson-get", kwargs={"pk": self.lesson.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], self.lesson.title)

    def test_update_lesson(self):
        """ Тест изменения урока владельцем """
        self.client.force_authenticate(user=self.user)

        data = {"title": "Updated Title"}
        url = reverse("materials:lesson-update", kwargs={"pk": self.lesson.id})
        response = self.client.patch(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], "Updated Title")

    def test_delete_lesson_by_moderator_forbidden(self):
        """ Тест запрета удаления урока модератором """
        self.client.force_authenticate(user=self.moderator)

        url = reverse("materials:lesson-delete", kwargs={"pk": self.lesson.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_by_owner(self):
        """Тест успешного удаления урока владельцем """
        self.client.force_authenticate(user=self.user)

        url = reverse("materials:lesson-delete", kwargs={"pk": self.lesson.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.filter(pk=self.lesson.id).count(), 0)

    # Тесты подписок

    def test_subscription_toggle(self):
        """Тестирование добавления и удаления подписки на курс (функционал переключателя)."""
        self.client.force_authenticate(user=self.user)
        url = reverse("materials:course-subscribe")
        data = {"course_id": self.course.id}

        # Первая отправка запроса — подписка должна создаться
        response_add = self.client.post(url, data=data)
        self.assertEqual(response_add.status_code, status.HTTP_200_OK)
        self.assertEqual(response_add.json()["message"], "Подписка добавлена.")
        self.assertTrue(
            Subscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )

        # Вторая отправка запроса — подписка должна удалиться
        response_remove = self.client.post(url, data=data)
        self.assertEqual(response_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(response_remove.json()["message"], "Подписка удалена.")
        self.assertFalse(
            Subscription.objects.filter(
                user=self.user, course=self.course
            ).exists()
        )

