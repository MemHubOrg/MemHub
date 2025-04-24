import json
import requests
import logging
import pyotp
import os

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage

from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from register.forms import LoginForm, RegisterForm, TelegramCodeForm, PasswordChangeForm
from register.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_simplejwt.tokens import RefreshToken

from io import BytesIO


logger = logging.getLogger(__name__)
EXTERNAL_API_IP = "192.168.0.153"

def index(request):
    #return render(request, 'users/index.html')
    return render(request, 'register/index.html')


def register(request):
    if request.method == 'POST':
        image_file = request.FILES.get('file')
        if not image_file:
            return JsonResponse({'success': False, 'error': 'Файл не получен'})

        try:
            user_profile = User.objects.get(username=request.user)
            chat_id = user_profile.chat_id
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль пользователя не найден'})

        # Считываем содержимое файла в память
        buffer = BytesIO()
        for chunk in image_file.chunks():
            buffer.write(chunk)
        buffer.seek(0)

        if buffer.getbuffer().nbytes == 0:
            return JsonResponse({'success': False, 'error': 'Файл пустой'})

        files = {
            'file': ('meme.png', buffer, 'image/png')  # Принудительно отправляем как PNG
        }
        data = {
            'chat_id': chat_id
        }

        url = f'http://{EXTERNAL_API_IP}:8081/send_meme'

        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': response.text})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

@csrf_exempt
def verify_telegram_code(request):
    if request.method != 'POST':
        logger.warning("Invalid request method")
        return JsonResponse({
            "success": False,
            "error": "Only POST requests are allowed"
        }, status=405)

    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON format"
        }, status=400)

    form = TelegramCodeForm(data=json_data)

    if form.is_valid():
        user_input = form.cleaned_data['telegram_code']
        username = form.cleaned_data['username']

        user = User.objects.get(username=username)

        if pyotp.TOTP(user.unique_token, interval=300).now() == user_input:
            auth_login(request, user)
             
            # JWT-token
            refresh = RefreshToken.for_user(user)
            token_data = {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
 
            form = LoginForm()
            return JsonResponse({
                "success": True,
                "access_token": token_data["access"],
                "refresh_token": token_data["refresh"],
                "redirect_url": "/"
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "error": "Неверный код. Попробуйте ещё раз."
            }, status=400)

    return JsonResponse({"success": False}, status=400)

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if not User.objects.filter(username=username).exists():
                form = RegisterForm(initial={"username": ""})
                return render(
                    request,
                    "register/register.html",#"users/register.html",
                    {"form": form, "error": "Пользователь с таким именем не найден! Пройдите регистрацию!"}
                )

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                send_code_to_user(username)
                return render(request, "register/verify_code.html",
                              {'username': username,
                               "form": TelegramCodeForm(request.POST)})
            return render(request, "register/login.html", {"form": form, "error": "Неверный логин или пароль!"})
            #return render(request, "users/login.html", {"form": form, "error": "Неверный логин или пароль!"})

        # return render(request, "users/login.html", {"form": form})
        return render(request, "register/login.html", {"form": form})

    else:
        form = LoginForm()
        return render(request, "register/login.html", {"form": form})
        # return render(request, "users/login.html", {"form": form})

@csrf_exempt
def send_meme_to_telegram(request):
    if request.method == 'POST':
        image_file = request.FILES.get('file')
        if not image_file:
            return JsonResponse({'success': False, 'error': 'Файл не получен'})

        # # Сохраняем файл в media/
        # meme_path = os.path.join('', image_file.name)
        # full_path = os.path.join(settings.MEDIA_ROOT, meme_path)

        # with default_storage.open(meme_path, 'wb+') as destination:
        #     for chunk in image_file.chunks():
        #         destination.write(chunk)

        try:
            # Получаем chat_id из профиля
            user_profile = User.objects.get(username=request.user)
            chat_id = user_profile.chat_id
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Профиль пользователя не найден'})
        
        files = {
            'file': (image_file.name, image_file, image_file.content_type)
        }
        data = {
            'chat_id': chat_id
        }
        url = f'http://{EXTERNAL_API_IP}:8081/send_meme'

        try:
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': f"Ошибка: {response.json().get('message')}"})
        except requests.exceptions.RequestException as e:
            return JsonResponse({'success': False, 'error': f"Ошибка запроса: {str(e)}"})

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

@csrf_exempt
def send_telegram_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username", "")
        success = send_code_to_user(username)
        return JsonResponse({"success": success})

    return JsonResponse({"success": False}, status=400)

def send_code_to_user(username):
    #url = 'http://109.68.215.67:8081/send_code'
    url = f'http://{EXTERNAL_API_IP}:8081/send_code'
    payload = {'username': username}
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return True
        else:
            print(f"Error: {response.json().get('message')}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    
class CustomTokenView(TokenObtainPairView):
     @swagger_auto_schema(
         request_body=openapi.Schema(
             type=openapi.TYPE_OBJECT,
             required=["username", "password"],
             properties={
                 "username": openapi.Schema(type=openapi.TYPE_STRING),
                 "password": openapi.Schema(type=openapi.TYPE_STRING),
             },
         ),
         responses={200: openapi.Schema(
             type=openapi.TYPE_OBJECT,
             properties={
                 "access": openapi.Schema(type=openapi.TYPE_STRING),
                 "refresh": openapi.Schema(type=openapi.TYPE_STRING),
             }
         )}
     )
     def post(self, request, *args, **kwargs):
         return super().post(request, *args, **kwargs)