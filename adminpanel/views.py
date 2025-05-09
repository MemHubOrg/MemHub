from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Admin
from .forms import AdminLoginForm
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse

from backend.models import Template
from django.views.decorators.csrf import csrf_exempt
import json

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data['login']
            password_input = form.cleaned_data['password']

            try:
                admin = Admin.objects.get(login=login_input)
                if check_password(password_input, admin.password):
                    request.session['admin_id'] = admin.id  # кастомная сессия
                    return redirect('/adminpanel/dashboard/')  # или куда нужно
                else:
                    form.add_error(None, "Неверный пароль")
            except Admin.DoesNotExist:
                form.add_error(None, "Администратор не найден")
    else:
        form = AdminLoginForm()

    return render(request, 'adminpanel/login.html', {'form': form})


def adminpanel_index(request):
    # Если админ авторизован — редиректим в дашборд (или куда хочешь)
    if request.session.get("admin_id"):
        return redirect("admin_dashboard")

    # Иначе на страницу входа
    return redirect("admin_login")


def admin_dashboard(request):
    # if not request.session.get("admin_id"):
    #     return redirect("admin_login")
    return render(request, 'adminpanel/dashboard.html')

# @csrf_exempt
# def manage_templates(request):
#     if request.method == 'POST':
#         if 'delete_id' in request.POST:
#             Template.objects.filter(id=request.POST['delete_id']).delete()
#         elif 'add_url' in request.POST:
#             Template.objects.create(image_url=request.POST['add_url'], tags=[])
#         elif 'edit_id' in request.POST:
#             template = Template.objects.get(id=request.POST['edit_id'])
#             new_tags = [tag.strip() for tag in request.POST['edit_tags'].split(',') if tag.strip()]
#             template.tags = new_tags
#             template.save()
#         return redirect('manage_templates')
#
#     templates = Template.objects.all().order_by('id')
#     return render(request, 'adminpanel/manage_templates.html', {'templates': templates})