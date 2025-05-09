import logging
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login
from django.contrib.auth.hashers import make_password

from users.forms import CustomPasswordChangeForm
from users.models import User
from backend.models import Meme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'users/index.html')

def profile(request):
    return render(request, 'users/my_account.html')

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            auth_login(request, request.user)
            # TODO Показать сообщение об успешной смене пароля
            return render(request, 'users/my_account.html')
    else:
        form = CustomPasswordChangeForm()
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def my_memes_view(request):
    memes = Meme.objects.filter(user=request.user)  # Или отфильтровать по пользователю
    memes_data = list(memes.values('id', 'image_url'))  # получаем только нужные поля
    return render(request, 'users/my_meme_list.html', {'memes': memes, 'memes_json': json.dumps(memes_data)})

@login_required
def selected_meme_view(request, image_id):
    meme = get_object_or_404(Meme, id=image_id)  # Получаем мем по id
    meme_image_url = meme.image_url  # Используем реальный URL изображения из модели
    return render(request, 'users/selected_meme.html', {'meme': meme, 'meme_image_url': meme_image_url})
