# interactions/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from articles.models import Article
from .models import UserInteraction, InteractionType
from userprofile.models import UserProfile

class LikeArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

        content_type = ContentType.objects.get_for_model(article)
        _, created = UserInteraction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=article.id,
            interaction_type=InteractionType.LIKE
        )
        if created:
            article.like_count += 1
            article.save()
            return Response({"message": f"You liked the article '{article.title}'"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "You have already liked this article"}, status=status.HTTP_400_BAD_REQUEST)

class UnlikeArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

        content_type = ContentType.objects.get_for_model(article)
        try:
            interaction = UserInteraction.objects.get(
                user=request.user,
                content_type=content_type,
                object_id=article.id,
                interaction_type=InteractionType.LIKE
            )
            interaction.delete()
            article.like_count -= 1
            article.save()
            return Response({"message": f"You unliked the article '{article.title}'"}, status=status.HTTP_200_OK)
        except UserInteraction.DoesNotExist:
            return Response({"message": "You have not liked this article"}, status=status.HTTP_400_BAD_REQUEST)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_follow_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Use `user.userprofile` ao invés de `user.profile`
        if request.user.userprofile == user_to_follow_profile:
            return Response({"error": "You cannot follow yourself"}, status=status.HTTP_400_BAD_REQUEST)

        content_type = ContentType.objects.get_for_model(user_to_follow_profile)
        _, created = UserInteraction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=user_to_follow_profile.id,
            interaction_type=InteractionType.FOLLOW
        )
        if created:
            user_to_follow_profile.follow_count += 1
            user_to_follow_profile.save()
            return Response({"message": f"You are now following {user_to_follow_profile.user.username}"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "You are already following this user"}, status=status.HTTP_400_BAD_REQUEST)

class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, username):
        try:
            user_to_unfollow_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        content_type = ContentType.objects.get_for_model(user_to_unfollow_profile)
        try:
            interaction = UserInteraction.objects.get(
                user=request.user,
                content_type=content_type,
                object_id=user_to_unfollow_profile.id,
                interaction_type=InteractionType.FOLLOW
            )
            interaction.delete()
            user_to_unfollow_profile.follow_count -= 1
            user_to_unfollow_profile.save()
            return Response({"message": f"You have unfollowed {user_to_unfollow_profile.user.username}"}, status=status.HTTP_200_OK)
        except UserInteraction.DoesNotExist:
            return Response({"message": "You are not following this user"}, status=status.HTTP_400_BAD_REQUEST)