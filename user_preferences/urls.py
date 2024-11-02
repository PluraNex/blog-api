# user_preferences/urls.py
from django.urls import path
from .views import NotificationSettingsView

urlpatterns = [
    path('notification-settings/', NotificationSettingsView.as_view(), name='notification-settings'),
]
