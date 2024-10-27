from django.urls import path
from .views import ProfileDetailView, ProfileListView

urlpatterns = [
    path('', ProfileDetailView.as_view(), name='profile-detail'),  
    path('all/', ProfileListView.as_view(), name='profile-list')
]
