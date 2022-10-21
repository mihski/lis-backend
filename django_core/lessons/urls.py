from rest_framework import routers

from lessons.views import (
    NPCViewSet,
    LocationViewSet,
    LessonDetailViewSet,
    LessonActionsViewSet,
    CourseMapViewSet,
    BranchSelectViewSet,
    ReviewViewSet,
    QuestionViewSet
)

app_name = "lessons"

router = routers.SimpleRouter()
router.register("lessons", LessonDetailViewSet)
router.register("lessons", LessonActionsViewSet)
router.register("npc", NPCViewSet)
router.register("locations", LocationViewSet)
router.register("courses", CourseMapViewSet)
router.register("branchings", BranchSelectViewSet)
router.register("reviews", ReviewViewSet)
router.register("questions", QuestionViewSet)

urlpatterns = router.urls
