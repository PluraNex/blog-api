# user_preferences/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import NotificationSettings
from .serializers import NotificationSettingsSerializer

class NotificationSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve notification settings",
        operation_description="Get the current notification settings for the authenticated user.",
        responses={
            200: openapi.Response(
                description="User's notification settings",
                schema=NotificationSettingsSerializer(),
            ),
            401: openapi.Response(description="Unauthorized"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['user_preferences']
    )
    def get(self, request):
        try:
            notification_settings = request.user.userprofile.notification_settings
            serializer = NotificationSettingsSerializer(notification_settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotificationSettings.DoesNotExist:
            return Response(
                {"error": "Notification settings not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Update notification settings",
        operation_description="Update the notification settings for the authenticated user.",
        request_body=NotificationSettingsSerializer,
        responses={
            200: openapi.Response(
                description="Updated notification settings",
                schema=NotificationSettingsSerializer(),
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['user_preferences']
    )
    def put(self, request):
        try:
            notification_settings = request.user.userprofile.notification_settings
            serializer = NotificationSettingsSerializer(notification_settings, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except NotificationSettings.DoesNotExist:
            return Response(
                {"error": "Notification settings not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_summary="Partially update notification settings",
        operation_description="Partially update the notification settings for the authenticated user.",
        request_body=NotificationSettingsSerializer,
        responses={
            200: openapi.Response(
                description="Partially updated notification settings",
                schema=NotificationSettingsSerializer(),
            ),
            400: openapi.Response(description="Bad request"),
            401: openapi.Response(description="Unauthorized"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['user_preferences']
    )
    def patch(self, request):
        try:
            notification_settings = request.user.userprofile.notification_settings
            serializer = NotificationSettingsSerializer(notification_settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except NotificationSettings.DoesNotExist:
            return Response(
                {"error": "Notification settings not found"},
                status=status.HTTP_404_NOT_FOUND
            )
