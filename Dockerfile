# Используем официальный образ Python в качестве базового
FROM python:3.9-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы с зависимостями
COPY requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт для веб-сервера
EXPOSE 8000

# Команда для запуска приложения
#CMD ["python", "manage.py", "runserver", "192.168.0.3:8000"]
CMD ["python", "manage.py", "runserver", "192.168.0.153:8000"]
