from django.apps import AppConfig
import user.signals.handlers


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    def ready(self):
        user.signals.handlers
