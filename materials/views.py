from rest_framework import viewsets, generics
from materials.models import Course, Lesson, Subscription
from materials.paginators import CoursePaginator, LessonPaginator
from materials.serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsModerator, IsOwner
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView



# ViewSet для Курсов
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


# Generics для Уроков
class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModerator]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LessonPaginator

    def get_queryset(self):
        if self.request.user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)

class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerator | IsOwner]

class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsOwner]


# Контроллер управления подпиской на обновления курса
class SubscriptionAPIView(APIView):

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
