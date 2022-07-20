"""django_core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
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
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls', namespace='accounts')),
    path('api/sso_auth/', include('sso_app.urls', namespace='sso_app')),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
