from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    """ Для вывода списка курсов."""

    page_size = 5  # Количество на одной странице
    page_size_query_param = (
        "page_size"  # Позволяет клиенту задать количество элементов
    )
    max_page_size = 20  # Максимальное количество выводимых элементов


class LessonPaginator(PageNumberPagination):
    """ Для вывода списка уроков."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20
