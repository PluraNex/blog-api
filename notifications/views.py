# notifications/views.py
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import NotificationInteraction
from .serializers import NotificationInteractionSerializer


class NotificationInteractionListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all interaction notifications for a user",
        operation_description="Retrieve a list of interaction notifications for the authenticated user.",
        responses={
            200: openapi.Response(
                description="A list of interaction notifications",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Notification ID"),
                            "message": openapi.Schema(type=openapi.TYPE_STRING, description="Notification message"),
                            "read": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Read status"),
                            "interaction_type": openapi.Schema(type=openapi.TYPE_STRING, description="Type of interaction, e.g., LIKE, FOLLOW"),
                            "created_at": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Timestamp of notification"),
                            "object_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the related object"),
                            "object_type": openapi.Schema(type=openapi.TYPE_STRING, description="Type of the related object, e.g., article or userprofile"),
                            "origin_user": openapi.Schema(type=openapi.TYPE_STRING, description="Username of the user who triggered the notification"),
                        },
                    ),
                ),
            ),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['notifications']
    )
    def get(self, request):
        notifications = NotificationInteraction.objects.filter(user=request.user).order_by('-created_at')
        serializer = NotificationInteractionSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkNotificationInteractionAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Mark a notification as read",
        operation_description="Mark a specific notification as read by providing its ID.",
        manual_parameters=[
            openapi.Parameter(
                "notification_id",
                openapi.IN_PATH,
                description="ID of the notification to mark as read",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(description="Notification marked as read"),
            404: openapi.Response(description="Notification not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['notifications']
    )
    def post(self, request, notification_id):
        try:
            notification = NotificationInteraction.objects.get(id=notification_id, user=request.user)
            notification.read = True
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except NotificationInteraction.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
