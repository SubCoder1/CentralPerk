from django.apps import AppConfig

class NotifSignalsConfig(AppConfig):
    name = 'Home'

    def ready(self):
        import Home.signals