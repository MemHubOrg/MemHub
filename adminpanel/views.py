import logging
import uuid

from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage as s3_storage

from .models import Admin
from urllib.parse import urlparse
from .forms import AdminLoginForm
from backend.models import Template


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

@csrf_exempt
def manage_templates(request):
    if request.method == 'POST':
        try:
            # Удаление шаблона
            if 'delete_id' in request.POST:
                template = get_object_or_404(Template, id=request.POST.get('delete_id'))

                # Получение относительного пути
                parsed_url = urlparse(template.image_url)
                file_key = parsed_url.path.lstrip('/').removeprefix('memhub.bucket/')

                # Удаление из S3
                if s3_storage.exists(file_key):
                    s3_storage.delete(file_key)

                # Удаление из БД
                template.delete()

            # Добавление нового шаблона
            elif 'new_file' in request.FILES:
                uploaded_file = request.FILES['new_file']
                filename = f"templates/{uuid.uuid4().hex}.png"

                # Сохраняем файл в S3
                saved_path = s3_storage.save(filename, ContentFile(uploaded_file.read()))
                file_url = s3_storage.url(saved_path)

                # Сохраняем в БД
                Template.objects.create(image_url=file_url, tags=[])

            # Редактирование тегов шаблона
            elif 'edit_id' in request.POST and 'edit_tags' in request.POST:
                template = get_object_or_404(Template, id=request.POST['edit_id'])
                new_tags = [tag.strip() for tag in request.POST['edit_tags'].split(',') if tag.strip()]
                template.tags = new_tags
                template.save()

        except Exception as e:
            print(f"Ошибка в manage_templates: {e}")

        return redirect('manage_templates')

    # GET-запрос — отобразить список шаблонов
    templates = Template.objects.all().order_by('id')
    return render(request, 'adminpanel/manage_templates.html', {'templates': templates})