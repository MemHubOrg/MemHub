from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path("check-telegram-user/", views.check_telegram_user, name="check_telegram_user"),
    path("send-telegram-code/", views.send_telegram_code, name="send_telegram_code"),
]
