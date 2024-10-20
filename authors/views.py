# authors/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from drf_yasg import openapi 
from drf_yasg.utils import swagger_auto_schema
from .models import Author
from .serializers import AuthorSerializer
from django.shortcuts import get_object_or_404

class AuthorDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Get author details",
        operation_description="Retrieve detailed information about a specific author.",
        responses={
            200: openapi.Response(
                description="Detailed information about the author",
                schema=AuthorSerializer(),
            ),
            404: openapi.Response(description="Author not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Authors']
    )
    def get(self, request, author_id):
        try:
            author = Author.objects.get(id=author_id)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        except Author.DoesNotExist:
            return Response(
                {"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
