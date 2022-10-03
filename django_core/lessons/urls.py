from django.urls import path
from rest_framework import routers

from lessons.views import NPCViewSet, LocationViewSet, LessonDetailViewSet


app_name = "lessons"

router = routers.SimpleRouter()
router.register("npc", NPCViewSet)
router.register("locations", LocationViewSet)

urlpatterns = [
    path("<str:lesson_id>/", LessonDetailViewSet.as_view({'get': 'retrieve'})),
]
urlpatterns += router.urls
