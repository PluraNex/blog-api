# user_preferences/tests/test_signals.py
from user_preferences.tests.base_test import BaseTestSetup
from user_preferences.models import NotificationSettings

class NotificationSettingsSignalTest(BaseTestSetup):

    def test_create_notification_settings_signal(self):
        """
        Verifica se o signal cria uma instância de NotificationSettings quando um UserProfile é criado.
        Espera-se que, ao criar um novo UserProfile, uma instância de NotificationSettings seja automaticamente gerada.
        """
        # Recupera NotificationSettings associado ao UserProfile criado no setup
        notification_settings = NotificationSettings.objects.filter(user_profile=self.user_profile).first()
        
        # Valida que as configurações de notificação foram criadas com os valores padrão
        self.assertIsNotNone(notification_settings, "NotificationSettings não foi criado pelo signal.")
        self.assertTrue(notification_settings.notify_on_like)
        self.assertTrue(notification_settings.notify_on_comment)
        self.assertTrue(notification_settings.notify_on_new_follower)
        self.assertTrue(notification_settings.notify_on_milestone)
