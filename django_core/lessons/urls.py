from rest_framework import routers
from lessons.views import NPCViewSet, LocationViewSet


app_name = "lessons"

router = routers.SimpleRouter()
router.register("npc", NPCViewSet)
router.register("locations", LocationViewSet)

urlpatterns = router.urls
