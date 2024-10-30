# user_preferences/tests/test_serializers.py
from user_preferences.tests.base_test import BaseTestSetup
from user_preferences.serializers import NotificationSettingsSerializer

class NotificationSettingsSerializerTest(BaseTestSetup):

    def test_serializer_data(self):
        """
        Verifica se o serializer retorna os dados corretos para uma instância de NotificationSettings.
        Espera-se que os campos do serializer correspondam aos valores do objeto.
        """
        serializer = NotificationSettingsSerializer(instance=self.notification_settings)
        expected_data = {
            'notify_on_like': True,
            'notify_on_comment': True,
            'notify_on_new_follower': True,
            'notify_on_milestone': True
        }
        self.assertEqual(serializer.data, expected_data)

    def test_update_notification_settings(self):
        """
        Verifica se o serializer consegue atualizar corretamente uma instância de NotificationSettings.
        Espera-se que os novos dados sejam salvos e refletidos no objeto.
        """
        data = {
            'notify_on_like': False,
            'notify_on_comment': False,
            'notify_on_new_follower': True,
            'notify_on_milestone': False
        }
        serializer = NotificationSettingsSerializer(instance=self.notification_settings, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()

        self.notification_settings.refresh_from_db()
        self.assertFalse(self.notification_settings.notify_on_like)
        self.assertFalse(self.notification_settings.notify_on_comment)
        self.assertTrue(self.notification_settings.notify_on_new_follower)
        self.assertFalse(self.notification_settings.notify_on_milestone)
