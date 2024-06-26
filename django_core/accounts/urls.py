from rest_framework.routers import SimpleRouter
from django.urls import path

from accounts.views import (
    ProfileViewSet,
    ProfileStatisticsViewSet,
    AvatarViewSet,
    ReplayAPIView,
    ProfileAlbumViewSet,
    ProfileCourseListApiView
)

app_name = "accounts"

router = SimpleRouter()
router.register("profile", ProfileStatisticsViewSet)
router.register("profile", ProfileAlbumViewSet)
router.register("avatars", AvatarViewSet, basename="avatars")



urlpatterns = [
    path(
        "profile/",
        ProfileViewSet.as_view(
            {"put": "partial_update", "get": "retrieve"}
        ),
        name="profile-retrieve-update",
    ),
    path(
        "replay/",
        ReplayAPIView.as_view(),
        name="replay-game"
    ),

    path(
        "profile/course/",
         ProfileCourseListApiView.as_view(),
         name = "profile_cources"
    )

] + router.urls


# Override only one auth for one account

from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from editors.models import EditorSession


class UniqueAccountAuthForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        # TODO: add is_closed
        if EditorSession.objects.filter(user=user, is_closed=False).exists():
            raise ValidationError(
                "Пользователь еще не закончил сессию в редакторе. Во избежание проблем, мы не можем вас авторизовать."
            )


admin.autodiscover()
admin.site.login_form = UniqueAccountAuthForm
