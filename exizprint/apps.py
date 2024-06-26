from django.apps import AppConfig


class ExizprintConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exizprint'
    def ready(self):
        import core.signals
