import uuid
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from urllib.parse import urlparse
import boto3
from django.core.files.storage import default_storage as s3_storage

class Template(models.Model):
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.JSONField(default=list, blank=True)

class Meme(models.Model):
    image_url = models.CharField(max_length=256, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

# @receiver(post_delete, sender=Template)
# def delete_template_file(sender, instance, **kwargs):
#     if instance.image and instance.image.path:
#         try:
#             os.remove(instance.image.path)
#         except FileNotFoundError:
#             pass  # уже удалён
# @receiver(post_delete, sender=Template)
# def delete_template_file(sender, instance, **kwargs):
#     if instance.image_url:
#         # Получаем путь внутри бакета из URL
#         parsed = urlparse(instance.image_url)
#         object_path = parsed.path.lstrip('/')  # например: templates/placeholder_pic5.png
#
#         if s3_storage.exists(object_path):
#             s3_storage.delete(object_path)

# @receiver(post_delete, sender=Meme)
# def delete_meme_file(sender, instance, **kwargs):
#     if instance.image and instance.image.path:
#         try:
#             os.remove(instance.image.path)
#         except FileNotFoundError:
#             pass