from typing import Callable
from functools import wraps

from rest_framework.request import Request

from accounts.exceptions import ProfileDoesNotExistException
from accounts.models import Profile


def profile_provided(func: Callable) -> Callable:
    """
        Проверка на наличие существования профиля у пользователя
    """
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        request: Request = args[-1]
        if not Profile.objects.filter(user=request.user).exists():
            raise ProfileDoesNotExistException("You should to create a profile to get access for resources")
        return func(self, *args, **kwargs)
    return wrapped
