from django.apps import AppConfig

class SupportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'support'

    def ready(self):
        # Import signals module to activate receivers
        from .import signals
