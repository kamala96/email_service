from django.apps import AppConfig


class EmailsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'emails_app'

    def ready(self):
        from . import signals
