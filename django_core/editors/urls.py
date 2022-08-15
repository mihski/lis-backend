from rest_framework.routers import SimpleRouter

from editors.views import LessonEditorViewSet, UnitEditorViewSet, QuestViewSet, CourseViewSet

app_name = 'editor'

router = SimpleRouter()
router.register('lessons', LessonEditorViewSet)
router.register('units', UnitEditorViewSet)
router.register('quests', QuestViewSet)
router.register('courses', CourseViewSet)

urlpatterns = router.urls
