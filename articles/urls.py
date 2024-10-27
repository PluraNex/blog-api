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
    path("articles/", ArticleListView.as_view(), name="article-list"),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path("articles/slug/<slug:slug>/", ArticleDetailView.as_view(), name="article-detail-slug"),
    path("articles/create/", ArticleCreateView.as_view(), name="article-create"),
    path("articles/<int:pk>/update/", ArticleUpdateView.as_view(), name="article-update"),
    path("articles/search/", ArticleSearchView.as_view(), name="article-search"),
    path("articles/filter-sort/", FilteredSortedArticleView.as_view(), name="filtered-sorted-articles"),
    path("articles/trending/", TrendingArticlesView.as_view(), name="trending-articles"),
    path("articles/statistics/", ArticleStatisticsView.as_view(), name="article-statistics"),
    path("articles/<int:article_id>/tags/", ArticleTagUpdateView.as_view(), name="article-tags-update"), 
    path("articles/author/<int:author_id>/", ArticlesByAuthorView.as_view(), name="articles-by-author"),
    path("articles/themes/", ArticleThemeListView.as_view(), name="article-themes-list"),
]
