# notifications/tests/test_views.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from notifications.models import NotificationInteraction
from rest_framework_simplejwt.tokens import RefreshToken

class NotificationInteractionViewTests(APITestCase):
    def setUp(self):
        # Cria um usuário e autentica-o
        self.user = User.objects.create_user(username="testuser", password="password123")
        
        # Gera o token JWT para o usuário
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Cria notificações de exemplo para o usuário (ordem invertida para garantir que a mais recente seja exibida primeiro)
        self.notification2 = NotificationInteraction.objects.create(
            user=self.user, message="Second test notification", interaction_type="FOLLOW"
        )
        self.notification1 = NotificationInteraction.objects.create(
            user=self.user, message="First test notification", interaction_type="LIKE"
        )

    def test_list_notifications(self):
        """
        Verifica se o endpoint GET /notifications/ retorna todas as notificações do usuário autenticado.
        Espera-se que o status de resposta seja 200 e que contenha a lista de notificações criadas.
        """
        url = reverse("notification-interaction-list")
        response = self.client.get(url)
        
        # Verificações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Deve conter as duas notificações criadas
        self.assertEqual(response.data[0]["message"], "First test notification")  # Confere se a primeira é a mais recente
        self.assertEqual(response.data[1]["message"], "Second test notification")

    def test_mark_notification_as_read(self):
        """
        Verifica se o endpoint POST /notifications/mark-as-read/<id>/ atualiza o status de leitura de uma notificação.
        Espera-se que o status de resposta seja 200 e que o campo 'read' da notificação seja atualizado para True.
        """
        url = reverse("mark-notification-interaction-as-read", args=[self.notification1.id])
        response = self.client.post(url)  # Usando POST em vez de PATCH
        
        # Verificações
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.read)  # O campo 'read' deve ser True após a atualização

    def test_mark_notification_as_read_invalid_id(self):
        """
        Verifica se o endpoint POST /notifications/mark-as-read/<id>/ retorna 404 quando o ID é inválido.
        Espera-se que o status de resposta seja 404, indicando que a notificação não foi encontrada.
        """
        url = reverse("mark-notification-interaction-as-read", args=[9999])  # ID inexistente
        response = self.client.post(url)  # Usando POST em vez de PATCH
        
        # Verificações
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
