from rest_framework import permissions

from accounts.exceptions import ProfileDoesNotExistException
from accounts.models import Profile


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
        Права доступа только админу или только для чтения
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj == request.user


class HasProfilePermission(permissions.BasePermission):
    """
        Права доступа только тем, у кого есть профиль
    """
    def has_permission(self, request, view):
        has_profile = Profile.objects.filter(user=request.user).exists()
        if not has_profile:
            raise ProfileDoesNotExistException("You should to create a profile to get access for requested resource")

        return has_profile
