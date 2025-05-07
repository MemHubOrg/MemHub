from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class AdminManager(BaseUserManager):
    def create_user(self, login, password=None):
        if not login:
            raise ValueError("Login is required")
        admin = self.model(login=login)
        admin.set_password(password)
        admin.save()
        return admin

    def create_superuser(self, login, password=None):
        return self.create_user(login, password)


class Admin(AbstractBaseUser):
    login = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)  # уже используется в AbstractBaseUser

    objects = AdminManager()

    USERNAME_FIELD = 'login'
    def __str__(self):
        return self.login