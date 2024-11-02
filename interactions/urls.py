# interactions/urls.py
from django.urls import path
from .views import LikeArticleView, UnlikeArticleView, FollowUserView, UnfollowUserView

urlpatterns = [
    path('like/article/<int:article_id>/', LikeArticleView.as_view(), name='like-article'),
    path('unlike/article/<int:article_id>/', UnlikeArticleView.as_view(), name='unlike-article'),
    path('follow/user/<str:username>/', FollowUserView.as_view(), name='follow-user'),
    path('unfollow/user/<str:username>/', UnfollowUserView.as_view(), name='unfollow-user'),
]
