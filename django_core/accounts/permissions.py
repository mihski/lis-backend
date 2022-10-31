from rest_framework import permissions

from accounts.models import Profile


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
        Права доступа только админу или только для чтения
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user
