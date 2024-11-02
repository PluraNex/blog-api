# notifications/tests/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from notifications.models import NotificationInteraction

class NotificationInteractionModelTest(TestCase):
    def setUp(self):
        # Cria um usuário para associar com a notificação
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_create_notification_interaction(self):
        """
        Verifica se uma instância de NotificationInteraction é criada corretamente com os valores esperados.
        Espera-se que 'user', 'message', 'interaction_type', 'read' e 'created_at' estejam preenchidos corretamente,
        e que o campo 'read' tenha o valor padrão False.
        """
        # Cria uma notificação de interação para o usuário
        notification = NotificationInteraction.objects.create(
            user=self.user,
            message="This is a test notification",
            interaction_type="LIKE"
        )
        
        # Verificações
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.message, "This is a test notification")
        self.assertEqual(notification.interaction_type, "LIKE")
        self.assertFalse(notification.read)  # Deve ser False por padrão
        self.assertIsNotNone(notification.created_at)

    def test_mark_notification_as_read(self):
        """
        Verifica se o campo 'read' de uma instância de NotificationInteraction pode ser atualizado para True.
        Espera-se que, após a atualização e salvamento, o valor de 'read' seja True ao recuperar a instância.
        """
        # Cria uma notificação de interação
        notification = NotificationInteraction.objects.create(
            user=self.user,
            message="Another test notification",
            interaction_type="FOLLOW"
        )
        
        # Marca a notificação como lida e verifica
        notification.read = True
        notification.save()
        
        # Recarrega a notificação do banco de dados
        updated_notification = NotificationInteraction.objects.get(id=notification.id)
        self.assertTrue(updated_notification.read)
