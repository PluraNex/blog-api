from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ImageArticle
from .serializers import ImageArticleSerializer

class ImageArticleListView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="List all Image Articles",
        operation_description="Retrieve a list of all image articles.",
        responses={
            200: openapi.Response(
                description="A list of image articles",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT, ref="#/definitions/ImageArticle"
                    ),
                ),
            ),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['resources']
    )
    def get(self, request):
        image_articles = ImageArticle.objects.all()
        serializer = ImageArticleSerializer(image_articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ImageArticleDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get details of an Image Article",
        operation_description="Retrieve the details of a specific image article by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "image_article_id",
                openapi.IN_PATH,
                description="ID of the image article",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Details of the specified image article",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT, ref="#/definitions/ImageArticle"
                ),
            ),
            404: openapi.Response(description="Image Article not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['resources']
    )
    def get(self, request, image_article_id):
        try:
            image_article = ImageArticle.objects.get(id=image_article_id)
        except ImageArticle.DoesNotExist:
            return Response(
                {"error": "Image Article not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = ImageArticleSerializer(image_article)
        return Response(serializer.data, status=status.HTTP_200_OK)
