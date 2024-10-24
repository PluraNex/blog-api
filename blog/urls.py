# blog/urls.py
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Blog API",
        default_version="v1",
        description="API para o Blog",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contato@seublog.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("rest_framework.urls")),
    path("api/v1/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/articles/", include("articles.urls")),
    path("api/v1/users/", include("users.urls")),
    path("api/v1/profiles/", include("userprofile.urls")),
    path("api/v1/categories/", include("categories.urls")),
    path("api/v1/tags/", include("tags.urls")),        
    path("api/v1/resources/", include("resources.urls")),
    path("api/v1/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]