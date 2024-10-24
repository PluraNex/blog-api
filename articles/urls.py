from django.urls import path

from .views import (
    ArticleCreateView,
    ArticleDetailView,
    ArticleListView,
    ArticlesByAuthorView,
    ArticleSearchView,
    ArticleStatisticsView,
    ArticleTagUpdateView,
    ArticleThemeListView,
    ArticleUpdateView,
    FilteredSortedArticleView,
    TrendingArticlesView,

)

urlpatterns = [
    # Artigos
    path("", ArticleListView.as_view(), name="article-list"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="single_post"), 
    path("create/", ArticleCreateView.as_view(), name="article-create"),
    path("<int:pk>/update/", ArticleUpdateView.as_view(), name="article-update"),
    path("search/", ArticleSearchView.as_view(), name="article-search"),
    path("filter-sort/", FilteredSortedArticleView.as_view(), name="filtered-sorted-articles"),
    path("trending/", TrendingArticlesView.as_view(), name="trending-articles"),
    path("statistics/", ArticleStatisticsView.as_view(), name="article-statistics"),
    path("<int:pk>/tags/", ArticleTagUpdateView.as_view(), name="article-tags-update"),
    path("author/<int:author_id>/", ArticlesByAuthorView.as_view(), name="articles-by-author"),
    path("themes/", ArticleThemeListView.as_view(), name="article-themes-list"),
   
]
