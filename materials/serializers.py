from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import YoutubeOnlyValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

        validators = [YoutubeOnlyValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField() # новое поле признака подписки

    class Meta:
        model = Course
        fields = ['id', 'title', 'preview', 'description', 'lessons_count', 'lessons', 'is_subscribed']

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        ''' Метод проверки подписки текущего пользователя '''
        request = self.context.get('request')

        # Если запроса нет (None) или пользователь не авторизован — возвращаем False
        if not request or not request.user or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(user=request.user, course=obj).exists()

