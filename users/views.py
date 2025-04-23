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

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                return render(
                    request,
                    "users/register.html",
                    {"form": form, "error": "Пользователь с таким именем уже существует!"}
                )

            user = User.objects.create(
                username=username,
                password=make_password(password),
                unique_token=pyotp.random_base32()
            )
            user.save()

            return render(
                request, 'users/verify_code.html', 
                {'username': username, "form": TelegramCodeForm(request.POST)}
            )

        else:
            return render(request, "users/register.html", {"form": form})

    else:
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

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
            form = LoginForm()
            return JsonResponse({
                "success": True,
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
                    "users/register.html",
                    {"form": form, "error": "Пользователь с таким именем не найден! Пройдите регистрацию!"}
                )

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return render(request, "users/verify_code.html",
                              {'username': username,
                               "form": TelegramCodeForm(request.POST)})

            return render(request, "users/login.html", {"form": form, "error": "Неверный логин или пароль!"})

        return render(request, "users/login.html", {"form": form})

    else:
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})


@csrf_exempt
def send_telegram_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username", "")
        success = send_code_to_user(username)
        return JsonResponse({"success": success})

    return JsonResponse({"success": False}, status=400)

def send_code_to_user(username):
    url = 'http://109.68.215.67:8081/send_code'
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