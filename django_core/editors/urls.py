from rest_framework.routers import SimpleRouter

from editors.views import LessonEditorViewSet

app_name = 'editor'

router = SimpleRouter()
router.register('lessons', LessonEditorViewSet)

urlpatterns = router.urls
