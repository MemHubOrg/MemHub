from django.http import HttpResponse
from django.shortcuts import render

from django.contrib.auth.hashers import make_password

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
            # TODO нужно написать функцию (без разницы где она будет) и заменить ей registration_valid
            #  функция принимает юзернейм и ХЭШИРОВАННЫЙ ПАРОЛЬ и пытается зарегать его
            #  возвращает bool: True если всё ок False если не ок
            #  ВНИМАНИЕ!! ЛОГИКИ КОДА ОТ ТГ БОТА ЕЩЁ НЕТ!!!
            # hashed_password = make_password(password)
            # if (registration_valid(username, hashed_password)):
            #     user = User.objects.create(username=username, password=hashed_password)
            #     return render(request, "users/login.html")
            # else:
            #   return render(request, "users/register.html", {"form": form, "error": "Неверный логин или пароль!"})
        else:
            return render(request, "users/register.html", {"form": form})

    else:
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            if username == "admin" and password == "password123":
                return HttpResponse("Вы успешно вошли!")
            else:
                return render(request, "users/login.html", {"form": form, "error": "Неверный логин или пароль!"})
        else:
            return render(request, "users/login.html", {"form": form})

    else:
        form = LoginForm()
        return render(request, "users/login.html", {"form": form})


# def login(request):
#
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         print(f"Получен логин: {username}, пароль: {password}")
#
#         # TODO нужно написать функцию (где она будет располагаться мне без разницы) и поставить вместо условия ниже
#         #  имя функции (предлагаю user_is_valid) на рассмотрение разработчика
#         #  принимает два аргумента: юзернейм и пароль (либо уже хэшированный, либо хэшированный внутри (лучше первый вариант)
#         #  проверяет есть ли такой юзер+пароль(или его хэш) в бд
#         #  возвращает bool: True если есть, False если нет
#         if username == "admin" and password == "password123":
#             # (задача Вейдер!!) добавить сюда редирект на главную страницу, когда она будет готова
#             print("Вход успешен!")
#             return HttpResponse("Вы успешно вошли!")
#         else:
#             error = "Неверный логин или пароль!"
#
#             # принты временные, для удобства отладки
#             print("Ошибка:", error)
#             return render(request, "users/login.html", {"error": error})