import json
import requests
import logging
import pyotp

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from users.forms import LoginForm, RegisterForm, TelegramCodeForm
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

            # TODO нужно заменить пароль в открытом виде на хэшированный
            user = User.objects.create(
                username=username,
                password=password,
                unique_token=pyotp.random_base32()
            )
            user.save()

            return render(
                request, 'users/verify_code.html', 
                {'username': username, "form": TelegramCodeForm(request.POST)}
            )


            return redirect(f'/login/?username={username}')
            # else:
            #   return render(request, "users/register.html", {"form": form, "error": "Неверный логин или пароль!"})
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
            }, status=200)
        else:
            return JsonResponse({
                "success": False,
                "error": "Invalid verification code"
            }, status=400)

    return JsonResponse({"success": False}, status=400)

def login(request):
    username = request.GET.get("username", "")
    form = LoginForm(initial={'username': username})

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # TODO нужно написать функцию (где она будет располагаться мне без разницы) и поставить вместо условия ниже
            #         #  имя функции (предлагаю user_is_valid) на рассмотрение разработчика
            #         #  принимает два аргумента: юзернейм и пароль (либо уже хэшированный, либо хэшированный внутри (лучше первый вариант)
            #         #  проверяет есть ли такой юзер+пароль(или его хэш) в бд
            #         #  возвращает bool: True если есть, False если нет
            #
            # После успешной проверки вызвать send_code_to_user(username=username) для отправки кода

            if username == "admin" and password == "password123":
                # (задача Вейдер!!) добавить сюда редирект на главную страницу, когда она будет готова
                return HttpResponse("Вы успешно вошли!")

            return render(request, "users/login.html", {"form": form, "error": "Неверный логин или пароль!"})

        return render(request, "users/login.html", {"form": form})

    else:
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})

# def check_telegram_user(request):
#     username = request.GET.get("username", "")
#     # TODO создать функцию и поставить вместо check_if_user_exists
#     #  она принимает на вход юзернейм и проверяет есть ли пользователь В ТГ!!! с таким ником
#     #  если есть то возвращает True если нет то False
#     #  хардкод ниже уберите, строку с функцией раскомментируйте
#     #  потом зайдите в register.html 35 строка: "*ссылка*" заменить на актуальную ссылку

#     user_exists = True
#     # user_exists = check_if_user_exists(username)
#     return JsonResponse({"exists": user_exists})

@csrf_exempt
def send_telegram_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username", "")
        success = send_code_to_user(username)
        return JsonResponse({"success": success})

    return JsonResponse({"success": False}, status=400)


def send_code_to_user(username):
    url = 'http://192.168.0.102:8081/send_code'
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