# user_preferences/apps.py
from django.apps import AppConfig

class UserPreferencesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_preferences'

    def ready(self):
        import user_preferences.signals