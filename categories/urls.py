from django.urls import path
from .views import CategoryListView, CategoryDetailView

urlpatterns = [
    path("", CategoryListView.as_view(), name="category-list"),
    path("<int:category_id>/", CategoryDetailView.as_view(), name="category-detail"),
]
