#categories/views.py
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from articles.models import Category
from articles.serializers import ArticleSerializer


class CategoryListView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="List all categories with article count",
        operation_description="Retrieve a list of categories along with the number of articles in each.",
        responses={
            200: openapi.Response(
                description="A list of categories with article count",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT, ref="#/definitions/Category"
                    ),
                ),
            ),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['categories']
    )
    def get(self, request):
        categories = Category.objects.annotate(post_count=Count("articles"))
        category_data = [
            {
                "id": category.id,
                "name": category.name,
                "post_count": category.post_count,
            }
            for category in categories
        ]
        return Response(category_data, status=status.HTTP_200_OK)

class CategoryDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get articles by category",
        operation_description="Retrieve a paginated list of articles for a specific category by its ID.",
        manual_parameters=[
            openapi.Parameter(
                "category_id",
                openapi.IN_PATH,
                description="ID of the category",
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
                description="A paginated list of articles for the specified category",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of articles in the category",
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
            404: openapi.Response(description="Category not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['categories']
    )
    def get(self, request, category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response(
                {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )

        articles = category.articles.all()
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(articles, page_size)

        try:
            articles_page = paginator.page(page)
        except PageNotAnInteger:
            articles_page = paginator.page(1)
        except EmptyPage:
            articles_page = []

        serializer = ArticleSerializer(articles_page, many=True)

        response_data = {
            "count": paginator.count,
            "next": (
                articles_page.next_page_number() if hasattr(articles_page, 'next_page_number') and articles_page.has_next() else None
            ),
            "previous": (
                articles_page.previous_page_number() if hasattr(articles_page, 'previous_page_number') and articles_page.has_previous() else None
            ),
            "results": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
