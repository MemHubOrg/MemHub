from backend.models import Template
from django.utils.timezone import now
from django.db import connection

def create_initial_templates(sender, **kwargs):
    # Проверка, что таблица существует
    if 'backend_template' not in connection.introspection.table_names():
        return
    urls = [
        'https://storage.yandexcloud.net/memhub.bucket/templates/placeholder_pic.png',
        'https://storage.yandexcloud.net/memhub.bucket/templates/placeholder_pic2.png',
        'https://storage.yandexcloud.net/memhub.bucket/templates/placeholder_pic3.png',
        'https://storage.yandexcloud.net/memhub.bucket/templates/placeholder_pic4.png',
        'https://storage.yandexcloud.net/memhub.bucket/templates/placeholder_pic5.png',
    ]

    for url in urls:
        Template.objects.get_or_create(image_url=url, defaults={'created_at': now()})