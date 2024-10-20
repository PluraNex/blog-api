# authors/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from .models import Author
from .serializers import AuthorSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class AuthorDetailView(generics.RetrieveAPIView):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    lookup_url_kwarg = 'author_id'

    @swagger_auto_schema(
        operation_summary="Get author details",
        operation_description="Retrieve detailed information about a specific author.",
        responses={
            200: openapi.Response(
                description="Detailed information about the author",
                schema=AuthorSerializer()
            ),
            404: openapi.Response(description="Author not found"),
        },
        tags=['Authors']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)