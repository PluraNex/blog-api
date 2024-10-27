from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from articles.serializers import ArticleSerializer
from .models import Tag
from .serializers import TagSerializer

import logging

# Configurar o logger
logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)

class TagDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="Get articles by tag",
        operation_description="Retrieve a paginated list of articles for a specific tag by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "tag_id",
                openapi.IN_PATH,
                description="ID of the tag",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number to retrieve",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of articles per page",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="A paginated list of articles for the specified tag",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of articles with the tag",
                        ),
                        "next": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="URL of the next page",
                            nullable=True,
                        ),
                        "previous": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="URL of the previous page",
                            nullable=True,
                        ),
                        "results": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT, ref="#/definitions/Article"
                            ),
                            description="List of articles in the current page",
                        ),
                    },
                ),
            ),
            404: openapi.Response(description="Tag not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Tags']
    )
    def get(self, request, tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return Response(
                {"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND
            )

        articles = tag.articles.all().order_by("-publication_date")
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(articles, page_size)

        try:
            articles_page = paginator.page(page)
        except PageNotAnInteger:
            logger.info(f"Page '{page}' is not an integer. Defaulting to page 1.")
            articles_page = paginator.page(1)
        except EmptyPage:
            logger.info(f"Page '{page}' is out of range. Returning empty results.")
            return Response({
                "count": paginator.count,
                "next": None,
                "previous": None,
                "results": []
            }, status=status.HTTP_200_OK)

        serializer = ArticleSerializer(articles_page, many=True)

        response_data = {
            "count": paginator.count,
            "next": (
                articles_page.next_page_number() if articles_page.has_next() else None
            ),
            "previous": (
                articles_page.previous_page_number()
                if articles_page.has_previous()
                else None
            ),
            "results": serializer.data,
        }

        logger.info(f"Returning page {page}. Total articles: {paginator.count}")
        return Response(response_data, status=status.HTTP_200_OK)








class TagListView(APIView):
    @swagger_auto_schema(
        operation_summary="List all tags with article count",
        operation_description="Retrieve a list of tags along with the number of articles tagged with each.",
        responses={
            200: openapi.Response(
                description="A list of tags with article count",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT, ref="#/definitions/Tag"
                    ),
                ),
            ),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Tags']
    )
    def get(self, request):
        tags = Tag.objects.annotate(article_count=Count("articles"))
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
