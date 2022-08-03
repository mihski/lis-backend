from rest_framework.routers import SimpleRouter

from editors.views import LessonEditorViewSet, UnitEditorViewSet

app_name = 'editor'

router = SimpleRouter()
router.register('lessons', LessonEditorViewSet)
router.register('units', UnitEditorViewSet)

urlpatterns = router.urls
