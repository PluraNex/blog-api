from django.urls import path
from .views import ImageArticleListView, ImageArticleDetailView

urlpatterns = [
    path("image-articles/", ImageArticleListView.as_view(), name="image-article-list"),
    path("image-articles/<int:image_article_id>/", ImageArticleDetailView.as_view(), name="image-article-detail"),
]
