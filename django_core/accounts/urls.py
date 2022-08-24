from rest_framework.routers import SimpleRouter

from accounts.views import UserViewSet

app_name = 'accounts'

router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = router.urls


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
