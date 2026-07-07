import re
from rest_framework.serializers import ValidationError


class YoutubeOnlyValidator:
    """Проверяет, что ссылка ведет исключительно на youtube.com."""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        # Извлекаем значение проверяемого поля из словаря данных
        url = value.get(self.field)

        # Если поле пустое или ссылка не указана, пропускаем проверку
        if not url:
            return

        # Регулярное выражение для поиска совпадений с youtube.com
        youtube_regex = r'(https?://)?(www\.)?youtube\.com(/?.*)$'

        # Если ссылка не соответствует паттерну YouTube, вызываем ошибку
        if not re.match(youtube_regex, url):
            raise ValidationError(
                {
                    self.field: "Разрешены ссылки только на видео-ресурс youtube.com."
                }
            )
