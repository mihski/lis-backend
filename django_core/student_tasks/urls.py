from rest_framework import routers

from student_tasks.views import StudentTaskViewSet

app_name = 'student_tasks'

router = routers.SimpleRouter()
router.register('answers', StudentTaskViewSet)

urlpatterns = router.urls
