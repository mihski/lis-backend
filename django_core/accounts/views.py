from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from accounts.models import User
from accounts.serializers import UserSerializer
from accounts.permissions import IsOwnerOrReadOnly


class UserViewSet(
    GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
):
    """ Ручка для работы с данными пользователя.
    Поменять можно только определенные поля.
    TODO: можно ли будет менять поля пользователя из фронта?
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly, )
