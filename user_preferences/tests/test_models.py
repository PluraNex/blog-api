# user_preferences/tests/test_models.py
from user_preferences.tests.base_test import BaseTestSetup
from user_preferences.models import NotificationSettings

class NotificationSettingsModelTest(BaseTestSetup):
    
    def test_create_notification_settings(self):
        """
        Verifica se as configurações de notificação padrão são criadas corretamente.
        Espera-se que as configurações para o usuário 'testuser' sejam criadas com as preferências padrão (todas como True).
        """
        settings = self.notification_settings
        self.assertEqual(settings.user_profile, self.user_profile)
        self.assertTrue(settings.notify_on_like)
        self.assertTrue(settings.notify_on_comment)
        self.assertTrue(settings.notify_on_new_follower)
        self.assertTrue(settings.notify_on_milestone)

    def test_update_notification_settings(self):
        """
        Verifica se as configurações de notificação podem ser atualizadas corretamente.
        Espera-se que as preferências de notificação para o usuário 'testuser' possam ser alteradas e salvas no banco de dados.
        """
        settings = self.notification_settings
        settings.notify_on_like = False
        settings.notify_on_comment = False
        settings.save()

        updated_settings = NotificationSettings.objects.get(id=settings.id)
        self.assertFalse(updated_settings.notify_on_like)
        self.assertFalse(updated_settings.notify_on_comment)
        self.assertTrue(updated_settings.notify_on_new_follower)
        self.assertTrue(updated_settings.notify_on_milestone)

    def test_str_representation(self):
        """
        Verifica se a representação em string do modelo NotificationSettings está correta.
        Espera-se que a string retorne 'Notification settings for testuser'.
        """
        settings = self.notification_settings
        self.assertEqual(str(settings), "Notification settings for testuser")
