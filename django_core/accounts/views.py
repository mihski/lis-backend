from rest_framework import viewsets, mixins, permissions, response

from accounts.models import Profile
from accounts.serializers import ProfileSerializer


class ProfileViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    """ Ручка для работы с профилем персонажа
    Все взаимодействие будет происходить с помощью
    идентификатора пользователя.

    Ошибки:
    - 400 - с тегом "scientific_director", если NPC не может быть научником
    - 403 - если не авторизован или если пытаешься изменить не свой профиль
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        self.check_object_permissions(self.request, profile)
        return profile

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
