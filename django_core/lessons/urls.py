from django.urls import path
from rest_framework import routers

from lessons.views import NPCViewSet, LocationViewSet, LessonDetailViewSet


app_name = "lessons"

router = routers.SimpleRouter()
router.register("lessons", LessonDetailViewSet)
router.register("npc", NPCViewSet)
router.register("locations", LocationViewSet)

urlpatterns = router.urls
