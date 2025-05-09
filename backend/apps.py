from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db import connection


class BackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

class BackendConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'

    def ready(self):
        from django.db import connection
        if connection.settings_dict['NAME'] != ':memory:':  # не делать это в тестах
            from backend.signals import create_initial_templates
            post_migrate.connect(create_initial_templates, sender=self)