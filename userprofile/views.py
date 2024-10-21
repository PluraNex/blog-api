# userprofile/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UserProfile
from .serializers import UserProfileSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class ProfileDetailView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Retrieve the profile of the authenticated user",
        operation_description="Retrieve detailed information about the profile of the currently authenticated user.",
        responses={
            200: openapi.Response(description="Profile retrieved successfully", schema=UserProfileSerializer),
            404: openapi.Response(description="Profile not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['profile']
    )
    def get(self, request):
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_summary="Update the profile of the authenticated user",
        operation_description="Update the profile information of the authenticated user, including the profile picture.",
        consumes=["multipart/form-data"],
        manual_parameters=[  # Definindo os parâmetros de formulário manualmente com exemplos
            openapi.Parameter(
                'bio', openapi.IN_FORM, description="User bio", type=openapi.TYPE_STRING, example="Software engineer with 10 years of experience"
            ),
            openapi.Parameter(
                'location', openapi.IN_FORM, description="User location", type=openapi.TYPE_STRING, example="São Paulo, Brazil"
            ),
            openapi.Parameter(
                'birth_date', openapi.IN_FORM, description="Birth date", type=openapi.TYPE_STRING, format="date", example="1990-01-01"
            ),
            openapi.Parameter(
                'profile_picture', openapi.IN_FORM, description="Profile picture", type=openapi.TYPE_FILE
            ),
            openapi.Parameter(
                'gender', openapi.IN_FORM, description="Gender of the user", type=openapi.TYPE_STRING, enum=["M", "F"], example="M"
        ),
        ],
        responses={
            200: openapi.Response(description="Profile updated successfully", schema=UserProfileSerializer),
            400: openapi.Response(description="Invalid input data"),
            404: openapi.Response(description="Profile not found"),
            500: openapi.Response(description="Internal server error"),
        },
        tags=['profile']
    )
    def put(self, request):
        """
        Update the profile of the authenticated user.
        """
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)