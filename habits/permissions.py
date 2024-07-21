from rest_framework.permissions import BasePermission
from rest_framework import status


class IsCurrentUser(BasePermission):
    """Права доступа только для текущего пользователя
    """
    message = {
        'published': 'Данную привычку может просматривать только владелец',
        }
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        pk = view.kwargs['pk']
        instance = view.queryset.get(pk=pk)
        return request.user == instance.owner


class IsAdmin(BaseException):
    """Класс доступа администратора
    """
    message = {
        'published': 'Данную привычку может просматривать только владелец',
        }
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        return request.user.is_superuser
