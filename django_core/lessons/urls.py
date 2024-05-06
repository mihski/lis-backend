from django.urls import path
from rest_framework import routers

from lessons.views import (
    NPCViewSet,
    LocationViewSet,
    LessonDetailViewSet,
    LessonActionsViewSet,
    CourseMapViewSet,
    CourseNameAPIView,
    BranchSelectViewSet,
    ReviewViewSet,
    QuestionViewSet,
    CallbackAPIView,
    NewCourseMapViewSet,
    ProfileLessonAPIView,
    ValidateSkipTaskAPIView,
    FirstSkippedTaskAPIView,
    CourseDetailView,
)

app_name = "lessons"

router = routers.SimpleRouter()
router.register("map", NewCourseMapViewSet)
router.register("lessons", LessonDetailViewSet)

router.register("lessons", LessonActionsViewSet)
router.register("npc", NPCViewSet)
router.register("locations", LocationViewSet)
router.register("courses", CourseMapViewSet)
router.register("branchings", BranchSelectViewSet)
router.register("reviews", ReviewViewSet)
router.register("questions", QuestionViewSet)

urlpatterns = [
    path("course/<int:pk>/",CourseDetailView.as_view()),
    *router.urls,
    path("callbacks/<str:pk>/", CallbackAPIView.as_view()),
    path("saved-lesson/<str:pk>/", ProfileLessonAPIView.as_view()),
    path("course-name/<int:pk>/", CourseNameAPIView.as_view()),
    path("validate-skip-task/<int:pk>", ValidateSkipTaskAPIView.as_view()),
    path("first-undone-task/<int:pk>", FirstSkippedTaskAPIView.as_view()),
    
]
