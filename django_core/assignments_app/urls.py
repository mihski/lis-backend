from rest_framework import routers

from .views import AssignmentListViewSet, StudentAssignmentViewSet

app_name = "assignments"

router = routers.SimpleRouter()
router.register("tasks", AssignmentListViewSet)
router.register("answers", StudentAssignmentViewSet)

urlpatterns = router.urls
