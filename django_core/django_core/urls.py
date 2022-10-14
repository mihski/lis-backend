from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Life-in-Science API",
      default_version='v1',
      contact=openapi.Contact(email="egorov_michil@mail.ru"),
   ),
   public=True,
   permission_classes=[permissions.IsAdminUser],
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("accounts.urls", namespace="accounts")),
    path("api/", include("resources.urls", namespace="resources")),
    path("api/lessons/", include("lessons.urls", namespace="lessons")),
    path("api/sso_auth/", include('sso_app.urls', namespace="sso_app")),
    path("api/editors/", include("editors.urls", namespace="editors")),
    path("api/tasks/", include("student_tasks.urls", namespace="tasks")),
    path("api/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
]
