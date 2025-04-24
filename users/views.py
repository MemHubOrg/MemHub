import json
import requests
import logging
import pyotp
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from users.forms import LoginForm, RegisterForm, TelegramCodeForm, PasswordChangeForm
from users.models import User

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'users/index.html')

def profile(request):
    return render(request, 'users/my_account.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        # if form.is_valid():
        #     #TODO логика смены пароля
        #
    else:
        form = PasswordChangeForm()
    return render(request, 'users/change_password.html', {'form': form})

def my_memes_view(request):
     return render(request, 'users/my_meme_list.html')

def selected_meme_view(request, image_id):
     # TODO логика забора реального айди реальной картинки
 
     # А пока заглушка.
     meme_image_url = f"users/placeholder_pic.png"
 
     return render(request, 'users/selected_meme.html', {'meme_image_url': meme_image_url})