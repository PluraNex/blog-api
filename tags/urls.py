from django.urls import path
from .views import TagListView, TagDetailView

urlpatterns = [
    path("", TagListView.as_view(), name="tag-list"),
    path("<int:tag_id>/", TagDetailView.as_view(), name="tag-detail"),
]
