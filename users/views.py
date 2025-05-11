import logging
import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login as auth_login

from users.forms import CustomPasswordChangeForm
from backend.models import Meme

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from urllib.parse import urlparse
from django.conf import settings
from django.core.files.storage import default_storage

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

# @require_http_methods(["DELETE"])
# @login_required
# def delete_meme(request, meme_id):
#     try:
#         meme = Meme.objects.get(id=meme_id, user=request.user)
#         meme.delete()
#         return JsonResponse({'status': 'ok'})
#     except Meme.DoesNotExist:
#         return JsonResponse({'error': 'Not found'}, status=404)

@require_http_methods(["DELETE"])
@login_required
def delete_meme(request, meme_id):
    meme = get_object_or_404(Meme, id=meme_id, user=request.user)

    # Получаем путь к файлу из URL
    parsed_url = urlparse(meme.image_url)
    file_key = parsed_url.path.lstrip('/').removeprefix('memhub.bucket/')

    # Удаляем файл из S3
    if default_storage.exists(file_key):
        default_storage.delete(file_key)

    # Удаляем запись из базы
    meme.delete()
    return JsonResponse({'status': 'ok'})