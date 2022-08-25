from rest_framework.routers import SimpleRouter
from resources.views import ResourceViewSet


app_name = 'resources'

router = SimpleRouter()
router.register('resources', ResourceViewSet)

urlpatterns = router.urls
