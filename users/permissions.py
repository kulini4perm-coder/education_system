from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        # Проверяем авторизован ли пользователь
        if not request.user or not request.user.is_authenticated:
            return False

        # Проверяем состоит ли в группе 'moderators'
        return request.user.groups.filter(name="moderators").exists()

class IsOwner(permissions.BasePermission):
    """Проверяет, является ли пользователь владельцем объекта."""

    def has_object_permission(self, request, view, obj):
        # Если поле owner совпадает с текущим пользователем, возвращаем True
        return obj.owner == request.user
