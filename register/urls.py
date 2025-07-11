from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from users.views import change_password_view

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('verify-telegram-code/', views.verify_telegram_code, name="verify_telegram_code"),
    path("send-telegram-code/", views.send_telegram_code, name="send_telegram_code"),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('send_meme_to_telegram/', views.send_meme_to_telegram, name='send_meme_to_telegram'),
    path('save_meme_to_profile/', views.save_meme_to_profile, name='save_meme_to_profile'),
    path('reset_password/', views.check_password_reset_flag),
    path('change-password/', change_password_view, name='change_password'),
]
