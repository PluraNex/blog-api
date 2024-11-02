# notifications/urls.py
from django.urls import path
from .views import NotificationInteractionListView, MarkNotificationInteractionAsReadView

urlpatterns = [
    path('', NotificationInteractionListView.as_view(), name='notification-interaction-list'),
    path('mark-as-read/<int:notification_id>/', MarkNotificationInteractionAsReadView.as_view(), name='mark-notification-interaction-as-read'),
]
