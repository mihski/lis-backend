from rest_framework.routers import SimpleRouter

from editors.views import LessonEditorViewSet, UnitEditorViewSet, QuestViewSet, CourseViewSet, EditorSessionViewSet

app_name = 'editor'

router = SimpleRouter()
router.register('lessons', LessonEditorViewSet)
router.register('units', UnitEditorViewSet)
router.register('quests', QuestViewSet)
router.register('courses', CourseViewSet)
router.register('sessions', EditorSessionViewSet)

urlpatterns = router.urls
