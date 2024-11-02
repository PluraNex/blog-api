# notifications/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from notifications.models import NotificationInteraction

class NotificationInteractionModelTest(TestCase):
    """
    Testa a criação de uma notificação de interação e verifica seus atributos principais.
    """
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_notification_creation(self):
        """
        Verifica se uma notificação é criada corretamente com os campos `user`, `message`,
        `interaction_type`, e se o campo `read` está configurado como False por padrão.
        """
        notification = NotificationInteraction.objects.create(
            user=self.user,
            message="This is a test notification",
            interaction_type="LIKE"
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, "This is a test notification")
        self.assertEqual(notification.interaction_type, "LIKE")
        self.assertFalse(notification.read)
