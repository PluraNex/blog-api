# blog/urls.py
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from blog import settings
from rest_framework import permissions

# Configuração do Swagger para a documentação da API
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
    path("api/v1/authors/", include("authors.urls")),
    path("api/v1/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
]