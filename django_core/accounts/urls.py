from rest_framework.routers import SimpleRouter

from accounts.views import UserViewSet

app_name = 'accounts'

router = SimpleRouter()
router.register('users', UserViewSet)

urlpatterns = router.urls
