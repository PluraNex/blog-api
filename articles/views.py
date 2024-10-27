from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Count, F, Q, Sum
from django.forms import ValidationError
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from articles.models import Article, ArticleTheme,Category, Tag
from articles.serializers import ArticleSerializer, ArticleThemeSerializer 


from userprofile.models import UserProfile

ARTICLE_NOT_FOUND_ERROR = {"error": "Article not found"}

PAGINATED_ARTICLE_RESPONSE = {
    200: openapi.Response(
        description="A paginated list of articles",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of articles"),
                "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the next page", nullable=True),
                "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the previous page", nullable=True),
                "results": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_OBJECT, ref="#/definitions/Article"),
                    description="List of articles in the current page",
                ),
            },
        ),
    ),
    500: openapi.Response(description="Internal server error"),
}

class BasePaginatedView(APIView):
    def paginate_queryset(self, queryset, request, serializer_class):
        page = request.query_params.get("page", 1)
        page_size = request.query_params.get("page_size", 10)
        paginator = Paginator(queryset, page_size)
        try:
            paginated_items = paginator.page(page)
        except PageNotAnInteger:
            paginated_items = paginator.page(1)
        except EmptyPage:
            paginated_items = paginator.page(paginator.num_pages)
        
        serializer = serializer_class(paginated_items, many=True, context={"request": request})
        return {
            "count": paginator.count,
            "next": paginated_items.next_page_number() if paginated_items.has_next() else None,
            "previous": (
                paginated_items.previous_page_number() if paginated_items.has_previous() else None
            ),
            "results": serializer.data,
        }

class ArticleListView(BasePaginatedView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="List all articles",
        operation_description="Retrieve a paginated list of articles, which can be filtered by various parameters.",
        manual_parameters=[
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
        responses=PAGINATED_ARTICLE_RESPONSE,
        tags=['articles']
    )
    def get(self, request):
        articles = Article.objects.all()
        response_data = self.paginate_queryset(articles, request, ArticleSerializer)
        return Response(response_data)

class ArticleDetailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Get a single article by ID or Slug",
        operation_description="Retrieve detailed information about a specific article by its ID or Slug and increment the view count.",
        responses={
            200: openapi.Response(
                description="Detailed information about the article",
                schema=ArticleSerializer(),
            ),
            404: openapi.Response(description="Article not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['articles']
    )
    def get(self, request, pk=None, slug=None):
        try:
            if pk:
                article = Article.objects.get(pk=pk)
            elif slug:
                article = Article.objects.get(slug=slug)
            else:
                return Response(
                    {"error": "Article identifier missing"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            Article.objects.filter(pk=article.pk).update(views_count=F("views_count") + 1)
            serializer = ArticleSerializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            return Response(
                ARTICLE_NOT_FOUND_ERROR , status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ArticleThemeListView(BasePaginatedView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="List all article themes",
        operation_description="Retrieve a paginated list of article themes.",
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number to retrieve",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of themes per page",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="A paginated list of article themes",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of themes"),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the next page", nullable=True),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL of the previous page", nullable=True),
                        "results": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT, ref="#/definitions/ArticleTheme"),
                            description="List of article themes in the current page",
                        ),
                    },
                ),
            ),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['articles']
    )
    def get(self, request):
        themes = ArticleTheme.objects.all()
        response_data = self.paginate_queryset(themes, request, ArticleThemeSerializer)
        return Response(response_data)

class ArticleCreateView(APIView):
    @swagger_auto_schema(
        operation_summary="Create a new article",
        operation_description="Submit a new article with all required fields.",
        request_body=ArticleSerializer,
        responses={
            201: openapi.Response(
                description="Article created successfully", schema=ArticleSerializer
            ),
            400: "Invalid data received",
            500: "Internal server error",
        },
        tags=['articles']
    )
    def post(self, request, *args, **kwargs):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            article = serializer.save()
            return Response(
                ArticleSerializer(article).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleSearchView(APIView):
    @swagger_auto_schema(
        operation_summary="Search articles",
        operation_description="Search for articles based on keywords, theme, category, or author.",
        manual_parameters=[
            openapi.Parameter(
                "keywords",
                openapi.IN_QUERY,
                description="Keywords to search in the article title",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "theme",
                openapi.IN_QUERY,
                description="Theme of the articles to filter",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Category of the articles to filter",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "author",
                openapi.IN_QUERY,
                description="Author of the articles to filter",
                type=openapi.TYPE_STRING,
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
        responses=PAGINATED_ARTICLE_RESPONSE,
        tags=['articles']
    )
    def get(self, request):
        query_params = request.query_params
        keywords = query_params.get("keywords")
        theme = query_params.get("theme")
        category = query_params.get("category")
        author = query_params.get("author")
        page_number = query_params.get("page", 1)
        page_size = query_params.get("page_size", 10)

        try:
            page_number = int(page_number)
            page_size = int(page_size)
            if page_number < 1 or page_size < 1:
                raise ValidationError(
                    "Page number and page size must be positive integers."
                )
        except ValueError:
            return Response(
                {"error": "Invalid page number or page size."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ArticleSerializer()
        articles = serializer.search(keywords, theme, category, author)

        paginator = Paginator(articles, page_size)
        try:
            articles_page = paginator.page(page_number)
        except EmptyPage:
            articles_page = paginator.page(paginator.num_pages)

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

        return Response(response_data)

class TrendingArticlesView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Retrieve trending articles",
        operation_description="Get a list of the top trending articles based on the number of views.",
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Limit the number of articles returned",
                type=openapi.TYPE_INTEGER,
                required=False,
            )
        ],
        responses={
            200: openapi.Response(
                description="A list of trending articles",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT, ref="#/definitions/Article"
                    ),
                    description="List of trending articles sorted by view count",
                ),
            ),
            400: openapi.Response(description="Invalid request parameters"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['articles']
    )
    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
            if limit < 1:
                return Response(
                    {"error": "Limit must be a positive integer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            trending_articles = Article.objects.order_by("-views_count")[:limit]
            serializer = ArticleSerializer(trending_articles, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Limit must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FilteredSortedArticleView(BasePaginatedView):
    permission_classes = [AllowAny]
    valid_sort_fields = ["publication_date", "views_count", "reading_time_minutes"]
    valid_orders = ["asc", "desc"]

    @swagger_auto_schema(
        operation_summary="List filtered and sorted articles",
        operation_description="Retrieve articles filtered by keyword, category, tag and sorted by various parameters.",
        manual_parameters=[
            openapi.Parameter(
                "keyword",
                openapi.IN_QUERY,
                description="Keyword to search in title or description",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "category",
                openapi.IN_QUERY,
                description="Filter by category name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "tag",
                openapi.IN_QUERY,
                description="Filter by tag name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "sort_by",
                openapi.IN_QUERY,
                description="Field to sort by",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "order",
                openapi.IN_QUERY,
                description="Order of sorting (asc or desc)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of filtered and sorted articles",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT, ref="#/definitions/Article"
                    ),
                ),
            ),
            400: openapi.Response(description="Invalid parameters"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['Articles']
    )
    def get(self, request):
        keyword = request.query_params.get("keyword")
        category_name = request.query_params.get("category")
        tag_name = request.query_params.get("tag")
        sort_by = request.query_params.get("sort_by", "publication_date")
        order = request.query_params.get("order", "desc")

        if sort_by not in self.valid_sort_fields:
            return Response(
                {"error": "Invalid sort field"}, status=status.HTTP_400_BAD_REQUEST
            )
        if order not in self.valid_orders:
            return Response(
                {"error": "Invalid order. Use 'asc' or 'desc'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query = Q()
        if keyword:
            query &= Q(title__icontains=keyword) | Q(description__icontains=keyword)
        if category_name:
            query &= Q(categories__name=category_name)
        if tag_name:
            query &= Q(tags__name=tag_name)

        sort_by = sort_by if order == "asc" else f"-{sort_by}"

        articles = Article.objects.filter(query).order_by(sort_by)
        response_data = self.paginate_queryset(articles, request, ArticleSerializer)
        return Response(response_data, status=status.HTTP_200_OK)

class ArticlesByAuthorView(BasePaginatedView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Retrieve articles by author",
        operation_description="Get a list of articles published by a specific author based on the author's ID.",
        manual_parameters=[
            openapi.Parameter(
                "author_id",
                openapi.IN_PATH,
                description="The ID of the author",
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
        responses=PAGINATED_ARTICLE_RESPONSE,
        tags=['articles']
    )
    def get(self, request, author_id):
        try:
            user_profile = UserProfile.objects.get(id=author_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND
            )

        articles = Article.objects.filter(author=user_profile)
        response_data = self.paginate_queryset(articles, request, ArticleSerializer)
        return Response(response_data, status=status.HTTP_200_OK)


class ArticleTagUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update tags for an article",
        operation_description="Update or add tags to a specific article based on its ID.",
        manual_parameters=[
            openapi.Parameter(
                "article_id",
                openapi.IN_PATH,
                description="The ID of the article",
                type=openapi.TYPE_INTEGER,
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "tags": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of tags to associate with the article"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Tags updated successfully", schema=ArticleSerializer
            ),
            404: openapi.Response(description="Article not found"),
            400: openapi.Response(description="Invalid data"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['articles']
    )
    def put(self, request, article_id):
        try:
            article = Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            return Response(
               ARTICLE_NOT_FOUND_ERROR , status=status.HTTP_404_NOT_FOUND
            )
        
        tags_data = request.data.get("tags")
        if not tags_data or not isinstance(tags_data, list):
            return Response(
                {"error": "Invalid data. 'tags' should be a list of strings."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clear existing tags and add new ones
        article.tags.clear()
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            article.tags.add(tag)

        return Response(
            ArticleSerializer(article).data, status=status.HTTP_200_OK
        )

class ArticleStatisticsView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Get statistics about articles",
        operation_description="Retrieve detailed statistics about articles such as total views, average reading time, and article count per category.",
        responses={
            200: openapi.Response(
                description="Statistics about articles",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total_views": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of views across all articles",
                        ),
                        "average_reading_time": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Average reading time across all articles",
                        ),
                        "articles_per_category": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "category_name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Name of the category",
                                    ),
                                    "article_count": openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description="Number of articles in this category",
                                    ),
                                },
                            ),
                            description="Number of articles per category",
                        ),
                    },
                ),
            ),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['articles']
    )
    def get(self, request):
        total_views = Article.objects.aggregate(total_views=Sum("views_count"))[
            "total_views"
        ]
        average_reading_time = Article.objects.aggregate(
            average_reading_time=Avg("reading_time_minutes")
        )["average_reading_time"]
        articles_per_category = Category.objects.annotate(
            article_count=Count("articles")
        ).values("name", "article_count")

        statistics = {
            "total_views": total_views if total_views is not None else 0,
            "average_reading_time": (
                int(average_reading_time) if average_reading_time is not None else 0
            ),
            "articles_per_category": list(articles_per_category),
        }

        return Response(statistics)

class ArticleUpdateView(APIView):    
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update an article",
        operation_description="Update the details of an existing article by ID.",
        request_body=ArticleSerializer,
        responses={
            200: openapi.Response(
                description="Article updated successfully", schema=ArticleSerializer()
            ),
            400: openapi.Response(description="Invalid input data"),
            404: openapi.Response(description="Article not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['articles']
    )
    def put(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response(
                ARTICLE_NOT_FOUND_ERROR , status=status.HTTP_404_NOT_FOUND
            )

        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)