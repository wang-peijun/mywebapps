from django.apps import AppConfig


class MyauthConfig(AppConfig):
    name = 'myauth'

    def ready(self):
        import myauth.signals