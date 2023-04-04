from django.apps import AppConfig

class PerfilesConfig(AppConfig):
    name = 'perfiles'

    def ready(self):
        import perfiles.signals