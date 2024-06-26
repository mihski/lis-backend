from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from lessons.views import (CreatCourseViewSet,CourseDetailView)

schema_view = get_schema_view(
    openapi.Info(
        title="Life-in-Science API",
        default_version='v1',
        contact=openapi.Contact(email="egorov_michil@mail.ru"),
    ),
    public=True,
    url=f"https://{settings.HOST}/api",
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', include('loginas.urls')),
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls", namespace="accounts")),
    path("api/", include("resources.urls", namespace="resources")),
    path("api/lessons/", include("lessons.urls", namespace="lessons")),
    path("api/sso_auth/", include('sso_app.urls', namespace="sso_app")),
    path("api/editors/", include("editors.urls", namespace="editors")),
    path("api/tasks/", include("student_tasks.urls", namespace="tasks")),
    path("api/assignments/", include("assignments_app.urls", namespace="assignments")),
    path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0),
         name="schema-swagger-ui"),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/courseadd/",CreatCourseViewSet.as_view({"post":"create"})),
 #   path("api/courselist/",CreatCourseViewSet.as_view({"get":"list"})),
       
]
