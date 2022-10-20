from rest_framework.routers import SimpleRouter

from resources.views import ResourcesViewSet

app_name = "resources"

router = SimpleRouter()
router.register("resources", ResourcesViewSet)

urlpatterns = router.urls
