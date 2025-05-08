import uuid
import os

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Template(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='media/templates/')
    created_at = models.DateTimeField(auto_now_add=True)

class Meme(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='media/memes/')
    created_at = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

@receiver(post_delete, sender=Template)
def delete_template_file(sender, instance, **kwargs):
    if instance.image and instance.image.path:
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass  # уже удалён

@receiver(post_delete, sender=Meme)
def delete_meme_file(sender, instance, **kwargs):
    if instance.image and instance.image.path:
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass