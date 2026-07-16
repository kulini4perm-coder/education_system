from rest_framework import viewsets, generics
from materials.models import Course, Lesson, Subscription
from materials.paginators import CoursePaginator, LessonPaginator
from materials.serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModerator, IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from materials.tasks import send_course_update_email


# ViewSet для Курсов

@extend_schema_view(
    list=extend_schema(
        summary="Получить список курсов",
        description="Возвращает список курсов. Модераторы видят все курсы, обычные пользователи — только свои."
    ),
    create=extend_schema(
        summary="Создать новый курс",
        description="Создает новый учебный курс. Доступно всем авторизованным пользователям, кроме модераторов."
    ),
    retrieve=extend_schema(
        summary="Просмотр деталей курса",
        description="Возвращает детальную информацию о конкретном курсе. Доступно владельцу курса или модератору."
    ),
    update=extend_schema(
        summary="Редактировать курс (Полное обновление)",
        description="Позволяет полностью обновить данные курса. Доступно владельцу или модератору."
    ),
    partial_update=extend_schema(
        summary="Редактировать курс (Частичное обновление)",
        description="Позволяет изменить отдельные поля курса. Доступно владельцу или модератору."
    ),
    destroy=extend_schema(
        summary="Удалить курс",
        description="Удаляет курс из системы. Функция доступна только владельцу курса (модераторам запрещено)."
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    # Разделяем курсы по роли пользователя
    def get_queryset(self):
        # Модератору — все курсы
        if request_user_is_moderator := self.request.user.groups.filter(name="moderators").exists():
            return Course.objects.all()
        # Пользователю — только его курсы
        return Course.objects.filter(owner=self.request.user)

    # Привязываем владельца при создании курса
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    # Разграничиваем права доступа
    def get_permissions(self):
        if self.action == "create":
            # Создавать могут все, кроме модераторов
            self.permission_classes = [IsAuthenticated, ~IsModerator]
        elif self.action in ["retrieve", "update", "partial_update"]:
            # Просматривать детали и редактировать могут или модераторы, или владельцы
            self.permission_classes = [IsAuthenticated, IsModerator | IsOwner]
        elif self.action == "destroy":
            # Удалять могут только владельцы
            self.permission_classes = [IsAuthenticated, IsOwner]

        return [permission() for permission in self.permission_classes]

    def perform_update(self, serializer):
        # Сохраняем измененный курс
        course = serializer.save()

        # Сравниваем текущее время с предыдущим временем обновления курса
        if course.updated_at and (timezone.now() - course.updated_at) > timedelta(hours=4): # seconds=10 для теста
            # Запускаем задачу асинхронно через .delay()
            send_course_update_email.delay(course.id)
        elif not course.updated_at:
            # Если поле пустое, тоже отправляем
            send_course_update_email.delay(course.id)


# Generics для Уроков

@extend_schema(
    summary="Создать новый урок",
    description="Добавляет новый урок в систему. Доступно всем, кроме модераторов."
)
class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

@extend_schema(
    summary="Получить список уроков",
    description="Возвращает постраничный список уроков. Модераторы видят всё, пользователи — только свои уроки."
)
class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPaginator

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

@extend_schema(
    summary="Просмотр деталей урока",
    description="Возвращает подробную информацию об уроке по его ID. Доступно владельцу или модератору."
)
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

@extend_schema(
    summary="Редактировать урок",
    description="Позволяет обновить данные урока. Доступно владельцу или модератору."
)
class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

    def perform_update(self, serializer):
        # Сохраняем обновленный урок
        lesson = serializer.save()

        # Получаем связанный курс
        course = lesson.course

        # Если урок привязан к курсу — проверяем время и обновляем дату курса
        if course:
            if (timezone.now() - course.updated_at) > timedelta(hours=4): # seconds=10 для теста
                # Активируем Celery-задачу
                send_course_update_email.delay(course.id)

            course.touch()

@extend_schema(
    summary="Удалить урок",
    description="Удаляет урок из системы. Доступно строго только владельцу урока."
)
class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


# Контроллер управления подпиской на обновления курса
class SubscriptionAPIView(APIView):
    @extend_schema(
        summary = "Управление подпиской на курс",
        description = "Позволяет подписаться или отписаться от обновлений курса. Если подписка существует — она удаляется, если нет — создается.",
        request = inline_serializer(
            name='SubscriptionRequest',
            fields={
                'course_id': serializers.IntegerField(help_text="ID курса, на который оформляется/удаляется подписка")
            }
        ),
        responses = {
            200: inline_serializer(
                name='SubscriptionResponse',
                fields={
                    'message': serializers.CharField(help_text="Статус: 'Подписка добавлена.' или 'Подписка удалена.'")
                }
            ),
            400: inline_serializer(
                name='SubscriptionErrorResponse',
                fields={
                    'error': serializers.CharField(help_text="Сообщение об ошибке валидации")
                }
            )
        }

    )

    def post(self, request, *args, **kwargs):
        user = request.user  # Текущий авторизованный пользователь
        course_id = request.data.get("course_id")  # ID курса из тела запроса

        # Проверка, передан ли ID
        if not course_id:
            return Response({"error": "Поле course_id обязательно."}, status=400)

        # Получаем объект курса или отдаем 404
        course_item = get_object_or_404(Course, pk=course_id)

        # Ищем подписку в базе данных
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists(): # если подписка уже есть -
            subs_item.delete() # удаляем ее из базы
            message = "Подписка удалена."
        else:
            Subscription.objects.create(user=user, course=course_item) # если подписки нет - создаем
            message = "Подписка добавлена."

        return Response({"message": message})
