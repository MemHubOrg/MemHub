import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt

from users.forms import LoginForm, RegisterForm
from users.models import User


def index(request):
    return render(request, 'users/index.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            telegram_code = form.cleaned_data['telegram_code']
            # TODO нужно написать функцию (без разницы где она будет) и заменить ей registration_valid
            #  функция принимает юзернейм и ХЭШИРОВАННЫЙ ПАРОЛЬ и пытается зарегать его
            #  возвращает bool: True если всё ок False если не ок
            #  код ниже раскомментировать, по усмотрению разработчиков можно менять
            # hashed_password = make_password(password)
            # if (registration_valid(username, hashed_password)):
            #     user = User.objects.create(username=username, password=hashed_password)
            return redirect(f'/login/?username={username}')
            # else:
            #   return render(request, "users/register.html", {"form": form, "error": "Неверный логин или пароль!"})
        else:
            return render(request, "users/register.html", {"form": form})

    else:
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

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
            if username == "admin" and password == "password123":
                # (задача Вейдер!!) добавить сюда редирект на главную страницу, когда она будет готова
                return HttpResponse("Вы успешно вошли!")

            return render(request, "users/login.html", {"form": form, "error": "Неверный логин или пароль!"})

        return render(request, "users/login.html", {"form": form})

    else:
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})

def check_telegram_user(request):
    username = request.GET.get("username", "")
    # TODO создать функцию и поставить вместо check_if_user_exists
    #  она принимает на вход юзернейм и проверяет есть ли пользователь В ТГ!!! с таким ником
    #  если есть то возвращает True если нет то False
    #  хардкод ниже уберите, строку с функцией раскомментируйте
    #  потом зайдите в register.html 35 строка: "*ссылка*" заменить на актуальную ссылку

    user_exists = True
    # user_exists = check_if_user_exists(username)
    return JsonResponse({"exists": user_exists})

@csrf_exempt
def send_telegram_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username", "")
        # TODO создать функцию и поставить вместо send_code_to_user
        #  она принимает на вход юзернейм и говорит боту отправить юзеру код
        #  если всё норм отправилось то возвращает True если нет то False
        #  хардкод ниже уберите, строку с функцией раскомментируйте

        success = True
        # success = send_code_to_user(username)
        return JsonResponse({"success": success})

    return JsonResponse({"success": False}, status=400)