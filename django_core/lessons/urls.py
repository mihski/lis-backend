from rest_framework import routers

from lessons.views import NPCViewSet, LocationViewSet, LessonDetailViewSet, CourseMapViewSet, BranchSelectViewSet

app_name = "lessons"

router = routers.SimpleRouter()
router.register("lessons", LessonDetailViewSet)
router.register("npc", NPCViewSet)
router.register("locations", LocationViewSet)
router.register("courses", CourseMapViewSet)
router.register("branchings", BranchSelectViewSet)

urlpatterns = router.urls
