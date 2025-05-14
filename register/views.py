import json
import requests
import logging
import pyotp
import uuid
import boto3
import time

from backend.models import Meme

from backend.models import Template

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.core.files.storage import default_storage as s3_storage
from django.core.files.base import ContentFile, File

from django.conf import settings
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from register.forms import LoginForm, RegisterForm, TelegramCodeForm
from register.models import User

from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.tokens import AccessToken

# For fail2ban
logger_auth = logging.getLogger('django.security.Authentication')

# For debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTERNAL_API_IP = "192.168.0.6"

def index(request):
    templates = Template.objects.all()
    return render(request, 'register/index.html', {'templates': templates})

def health_check(request):
    return JsonResponse({"status": "ok"})

def register(request):
    message = request.session.pop('register_message', None)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                return render(
                    request,
                    "register/register.html",
                    {"form": form, "error": "Пользователь с таким именем уже существует!", "message": message}
                )
            
            request.session['register_data'] = {
                "username": username,
                "password": password,
                "unique_token": pyotp.random_base32()
            }

            return render(
                request,
                'register/verify_code.html',
                {'username': username, "form": TelegramCodeForm(request.POST)}
            )

        return render(request, "register/register.html", {"form": form, "message": message})

    else:
        form = RegisterForm()
        return render(request, "register/register.html", {"form": form, "message": message})

@csrf_exempt
def verify_telegram_code(request):
    if request.method != 'POST':
        return JsonResponse({
            "success": False,
            "error": "Only POST requests are allowed"
        }, status=405)

    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Invalid JSON format"
        }, status=400)

    form = TelegramCodeForm(data=json_data)

    if not form.is_valid():
        return JsonResponse({"success": False, "error": "Некорректные данные формы"}, status=400)

    user_input = form.cleaned_data['telegram_code']
    username = form.cleaned_data['username']

    register_data = request.session.get("register_data")

    if register_data and register_data.get("username") == username:
        # Пользователь на этапе регистрации
        unique_token = register_data.get("unique_token")

        if pyotp.TOTP(unique_token, interval=300).now() != user_input:
            return JsonResponse({
                "success": False,
                "error": "Неверный код. Попробуйте ещё раз."
            }, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Пользователь не найден в базе. Сначала инициализируйте диалог с ботом."
            }, status=404)

        # Обновляем пароль и токен
        user.password = make_password(register_data.get("password"))
        user.unique_token = unique_token
        user.save()

        del request.session["register_data"]
        auth_login(request, user)

    else:
        # Пользователь на этапе логина
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({
                "success": False,
                "error": "Пользователь не найден"
            }, status=404)

        if pyotp.TOTP(user.unique_token, interval=300).now() != user_input:
            return JsonResponse({
                "success": False,
                "error": "Неверный код. Попробуйте ещё раз."
            }, status=400)

        auth_login(request, user)

    # Возвращаем JWT токены
    refresh = RefreshToken.for_user(user)
    return JsonResponse({
        "success": True,
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "redirect_url": "/"
    }, status=200)

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if not User.objects.filter(username=username).exists():
                request.session['register_message'] = "Пользователь с таким именем не найден! Пройдите регистрацию!"
                return redirect("register")  # перенаправляем на путь, который обрабатывает регистрацию
                # form = RegisterForm(initial={"username": ""})
                # return render(
                #     request,
                #     "register/register.html",#"users/register.html",
                #     {"form": form, "error": "Пользователь с таким именем не найден! Пройдите регистрацию!"}
                # )

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                unique_token = user.unique_token
                send_code_to_user(username, unique_token)
                return render(
                    request, "register/verify_code.html",
                    {'username': username, "form": TelegramCodeForm(request.POST)}
                )
            
            # Get IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

            # if x_forwarded_for: 
            #     ip = x_forwarded_for.split(',')[0].strip()
            # else: 
            ip = request.META.get('REMOTE_ADDR')

            logger_auth.warning(f"Authentication failed for {username} from {ip}")

            return render(request, "register/login.html", {"form": form, "error": "Неверный логин или пароль!"})

        return render(request, "register/login.html", {"form": form})

    else:
        form = LoginForm()
        return render(request, "register/login.html", {"form": form})

@csrf_exempt
def send_meme_to_telegram(request):
    if request.method == 'POST' and request.FILES.get('file'):

        uploaded_file = request.FILES['file']
        filename = f"memes/send_in_telegram/{uuid.uuid4().hex}.png"  # Уникальное имя

        try:
            # Сохраняем в объектное хранилище
            saved_path = s3_storage.save(filename, ContentFile(uploaded_file.read()))
            file_url = s3_storage.url(saved_path)

            # Получаем chat_id из профиля
            chat_id = request.user.chat_id

            # Формируем json-файл
            url = f'http://{EXTERNAL_API_IP}:8081/send_meme'
            payload = {
                'chat_id': chat_id,
                'image_url': file_url
            }

            # Отправка
            response = requests.post(url, data=payload)
            if s3_storage.exists(saved_path): s3_storage.delete(saved_path)
        
            if response.status_code == 200:
                return JsonResponse({'success': True})
            else:
                print(f"Error: {response.json().get('message')}")
                return JsonResponse({'success': False})

        except Exception as e:
            if s3_storage.exists(saved_path): s3_storage.delete(saved_path)
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Файл не получен'}, status=400)

@csrf_exempt
def save_meme_to_profile(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        username = request.user.username
        filename = f"memes/profiles/{username}/{uuid.uuid4().hex}.png"
        
        try:
            # Сохраняем в объектное хранилище
            saved_path = s3_storage.save(filename, ContentFile(uploaded_file.read()))# File(uploaded_file))
            file_url = s3_storage.url(saved_path)

            # Сохраняем в БД
            meme = Meme.objects.create(
                image_url = file_url,
                user=request.user
            )
            meme.save()

            return JsonResponse({'success': True})

        except Exception as e:
            if s3_storage.exists(saved_path): s3_storage.delete(saved_path)
            return JsonResponse({'success': False, 'error': str(e)})
        
    return JsonResponse({'success': False})

@csrf_exempt
def send_telegram_code(request):
    if request.method == "POST":
        register_data = request.session.get("register_data")

        if not register_data:
            return JsonResponse({"success": False, "error": "Нет данных для регистрации"}, status=400)

        username = register_data.get("username")
        unique_token = register_data.get("unique_token")

        if not username or not unique_token:
            return JsonResponse({"success": False, "error": "Недостаточно данных"}, status=400)

        # Теперь передаём и токен
        success = send_code_to_user(username, unique_token)
        return JsonResponse({"success": success})

    return JsonResponse({"success": False}, status=400)

def send_code_to_user(username, unique_token):
    url = f'http://{EXTERNAL_API_IP}:8081/send_code'
    payload = {
        'username': username,
        'token': unique_token
    }

    try:
        response = requests.post(url, json=payload)
        print("BOT response:", response.status_code, response.text)
        return response.status_code == 200
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

@csrf_exempt
def check_password_reset_flag(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        token_str = data.get("access_token")
        if not token_str:
            return JsonResponse({"error": "No token provided"}, status=400)

        # Расшифровываем токен и получаем пользователя
        token = AccessToken(token_str)
        user_id = token['user_id']
        user = User.objects.get(id=user_id)

        return JsonResponse({"should_change_password": user.force_password_reset})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)