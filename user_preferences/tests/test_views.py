# user_preferences/tests/test_views.py
from unittest.mock import patch, PropertyMock
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user_preferences.tests.base_test import BaseTestSetup
from user_preferences.models import NotificationSettings
from user_preferences.serializers import NotificationSettingsSerializer


class NotificationSettingsViewTest(BaseTestSetup, APITestCase):

    def setUp(self):
        """
        Configura o cliente de teste com autenticação do usuário e cria as configurações iniciais.
        """
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("notification-settings")

    def test_get_notification_settings(self):
        """
        Verifica se o endpoint GET /notification-settings/ retorna as configurações corretas.
        Espera-se que retorne status 200 e os dados das configurações de notificação.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_data = NotificationSettingsSerializer(self.notification_settings).data
        self.assertEqual(response.data, expected_data)

    def test_put_update_notification_settings(self):
        """
        Verifica se o endpoint PUT /notification-settings/ atualiza as configurações corretamente.
        Espera-se que retorne status 200 e os dados atualizados das configurações de notificação.
        """
        data = {
            'notify_on_like': False,
            'notify_on_comment': False,
            'notify_on_new_follower': True,
            'notify_on_milestone': False
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification_settings.refresh_from_db()
        self.assertFalse(self.notification_settings.notify_on_like)
        self.assertFalse(self.notification_settings.notify_on_comment)
        self.assertTrue(self.notification_settings.notify_on_new_follower)
        self.assertFalse(self.notification_settings.notify_on_milestone)

    def test_patch_update_notification_settings(self):
        """
        Verifica se o endpoint PATCH /notification-settings/ atualiza parcialmente as configurações.
        Espera-se que retorne status 200 e os dados parcialmente atualizados das configurações de notificação.
        """
        data = {'notify_on_like': False}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification_settings.refresh_from_db()
        self.assertFalse(self.notification_settings.notify_on_like)
        self.assertTrue(self.notification_settings.notify_on_comment)
        self.assertTrue(self.notification_settings.notify_on_new_follower)
        self.assertTrue(self.notification_settings.notify_on_milestone)

    @patch('userprofile.models.UserProfile.notification_settings', new_callable=PropertyMock)
    def test_get_notification_settings_not_found(self, mock_notification_settings):
        """
        Verifica se o endpoint GET /notification-settings/ retorna 404 quando as configurações não existem.
        Espera-se que retorne status 404 e uma mensagem de erro indicando que as configurações de notificação não foram encontradas.
        """
        mock_notification_settings.side_effect = NotificationSettings.DoesNotExist
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Notification settings not found"})

    @patch('userprofile.models.UserProfile.notification_settings', new_callable=PropertyMock)
    def test_put_notification_settings_not_found(self, mock_notification_settings):
        """
        Verifica se o endpoint PUT /notification-settings/ retorna 404 quando as configurações não existem.
        Espera-se que retorne status 404 e uma mensagem de erro indicando que as configurações de notificação não foram encontradas.
        """
        mock_notification_settings.side_effect = NotificationSettings.DoesNotExist
        data = {
            'notify_on_like': False,
            'notify_on_comment': False,
            'notify_on_new_follower': True,
            'notify_on_milestone': False
        }
        response = self.client.put(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Notification settings not found"})

    @patch('userprofile.models.UserProfile.notification_settings', new_callable=PropertyMock)
    def test_patch_notification_settings_not_found(self, mock_notification_settings):
        """
        Verifica se o endpoint PATCH /notification-settings/ retorna 404 quando as configurações não existem.
        Espera-se que retorne status 404 e uma mensagem de erro indicando que as configurações de notificação não foram encontradas.
        """
        mock_notification_settings.side_effect = NotificationSettings.DoesNotExist
        data = {'notify_on_like': False}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Notification settings not found"})

    def test_put_invalid_data(self):
        """
        Verifica se o endpoint PUT /notification-settings/ retorna 400 quando os dados enviados são inválidos.
        Espera-se que retorne status 400 e uma mensagem de erro indicando o campo inválido.
        """
        invalid_data = {
            'notify_on_like': "invalid",
            'notify_on_comment': False,
            'notify_on_new_follower': True,
            'notify_on_milestone': False
        }
        response = self.client.put(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notify_on_like", response.data)

    def test_patch_invalid_data(self):
        """
        Verifica se o endpoint PATCH /notification-settings/ retorna 400 quando os dados enviados são inválidos.
        Espera-se que retorne status 400 e uma mensagem de erro indicando o campo inválido.
        """
        invalid_data = {'notify_on_like': "invalid"}
        response = self.client.patch(self.url, invalid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notify_on_like", response.data)
