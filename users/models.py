from django.db import models
import uuid

class User(models.Model):
    username = models.CharField(max_length=100, unique=True, null=False)
    password = models.CharField(max_length=255, unique=False, null=False)  # Храним хешированный пароль
    unique_token = models.CharField(max_length=32, unique=True, blank=True, null=True)
    chat_id = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.unique_token:
            self.unique_token = uuid.uuid4().hex[:32]  # Уникальное значение перед сохранением
        super().save(*args, **kwargs)
    def __str__(self):
        return self.username