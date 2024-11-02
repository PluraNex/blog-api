# notifications/tests.py
from django.test import TestCase
from notifications.models import NotificationInteraction
from notifications.serializers import NotificationInteractionSerializer
from notifications.tests.base_test import BaseNotificationTest
from userprofile.models import UserProfile
from django.contrib.auth.models import User

class NotificationInteractionSerializerTest(BaseNotificationTest):
    """
    Testa a serialização de notificações, verificando se os dados são formatados
    corretamente com todos os campos necessários.
    """
    def setUp(self):
        """
        Configura o ambiente de teste com usuário e perfil para a serialização de notificações.
        """
        User.objects.all().delete()
        UserProfile.objects.all().delete()

        self.user = User.objects.create_user(username="testuser", password="password123")
        self.user_profile, _ = UserProfile.objects.get_or_create(user=self.user, defaults={'is_author': True})

        self.notification = NotificationInteraction.objects.create(
            user=self.user,
            message="Test notification message",
            interaction_type="LIKE"
        )

    def test_serializer_fields(self):
        """
        Verifica os campos do serializer `NotificationInteractionSerializer` para garantir que
        estão formatados corretamente, incluindo `message`, `interaction_type` e `read`.
        """
        serializer = NotificationInteractionSerializer(instance=self.notification)
        data = serializer.data
        self.assertEqual(data['message'], "Test notification message")
        self.assertEqual(data['interaction_type'], "LIKE")
        self.assertEqual(data['read'], False)
