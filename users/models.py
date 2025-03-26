from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
import uuid

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self.create_user(username, password, **extra_fields)
class User(AbstractBaseUser):
    username = models.CharField(max_length=100, unique=True)
    unique_token = models.CharField(max_length=33, unique=True, blank=True, null=True)
    chat_id = models.CharField(max_length=10, unique=True, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def save(self, *args, **kwargs):
        if not self.unique_token:
            self.unique_token = uuid.uuid4().hex[:33]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username