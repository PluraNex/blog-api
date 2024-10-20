# authors/urls.py
from django.urls import path
from .views import AuthorDetailView

urlpatterns = [
    path('author/<int:author_id>/', AuthorDetailView.as_view(), name='author-detail'),
]
