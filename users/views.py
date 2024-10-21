from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        return UserSerializer
    
    @swagger_auto_schema(
        operation_summary="Create a new user",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, example="john_doe"),
                'email': openapi.Schema(type=openapi.TYPE_STRING, example="john@example.com"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, example="password123"),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, example="John"),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
            }
        ),
        responses={201: openapi.Response(description="User created successfully", schema=UserSerializer)}
    )
    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user == user or request.user.is_staff:
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        return Response({"detail": "Você não tem permissão para acessar esses detalhes."}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if request.user == user or request.user.is_staff:
            return super().update(request, *args, **kwargs)
        return Response({"detail": "Você não tem permissão para atualizar esses detalhes."}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
