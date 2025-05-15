import docker
import os
import requests
import time
import logging
import re
import threading

from collections import defaultdict
from datetime import datetime, timedelta
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
S3_HEALTH_URL = os.getenv("S3_HEALTH_URL")

# Для мониторинга контейнеров
CONTAINERS = ["telegram_bot", "telegram_bot_api", "django_app", "postgres_db"]
DOCKER_SOCKET_PATH = "/var/run/docker.sock"
client = docker.DockerClient(base_url='unix:///var/run/docker.sock')

# Для мониторинга входа
LOG_FILE = '/app/logs/auth.log'
FAILED_ATTEMPTS_THRESHOLD = 3
RESET_INTERVAL_MINUTES = 1

# Формат строки в логе
log_pattern = re.compile(r"Authentication failed for (\w+) from (\d+\.\d+\.\d+\.\d+)")

# Хранилище попыток входа
failed_attempts = {}

def check_container_health(container_name):
    try:
        container = client.containers.get(container_name)
        health = container.attrs['State'].get('Health')
        return health.get('Status') == "healthy"
    except Exception as e:
        return False

def check_s3():
    try:
        response = requests.head(S3_HEALTH_URL, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print("Failed to send Telegram alert:", e)

def monitor_containers():
    if not os.path.exists(DOCKER_SOCKET_PATH):
        print(f"Docker socket not found at {DOCKER_SOCKET_PATH}")
        send_telegram_alert("❌ Docker socket не найден. Мониторинг не запущен.")
        return

    while True:
        problems = []

        for container in CONTAINERS:
            if not check_container_health(container):
                problems.append(f"❌ Контейнер <b>{container}</b> не работает корректно")

        if not check_s3():
            problems.append("❌ S3-хранилище недоступно")

        if problems:
            message = "⚠️ <b>Обнаружены проблемы с компонентами системы:</b>\n" + "\n".join(problems)
            send_telegram_alert(message)

        time.sleep(30)

def monitor_log():
    try:
        with open(LOG_FILE, "r") as f:
            f.seek(0, 2)  # Переходим в конец файла
            send_telegram_alert("Начало мониторинга")

            while True:
                line = f.readline()
                if not line:
                    time.sleep(1)
                    continue

                match = log_pattern.search(line)
                if match:
                    username, ip = match.groups()
                    now = datetime.now()

                    if ip not in failed_attempts:
                        failed_attempts[ip] = []

                    # Удалить устаревшие записи
                    failed_attempts[ip] = [ts for ts in failed_attempts[ip] if now - ts < timedelta(minutes=RESET_INTERVAL_MINUTES)]
                    failed_attempts[ip].append(now)

                    count = len(failed_attempts[ip])
                    if count >= FAILED_ATTEMPTS_THRESHOLD:
                        message = f"🚨 {count} неудачные попытки входа для пользователя <b>{username}</b> с IP <b>{ip}</b>"
                        send_telegram_alert(message)
                time.sleep(0.1)
    except FileNotFoundError:
        send_telegram_alert(f"❌ Файл логов не найден: {LOG_FILE}")

if __name__ == "__main__":
    # Создаем два потока
    t1 = threading.Thread(target=monitor_log, daemon=True)
    t2 = threading.Thread(target=monitor_containers, daemon=True)

    t1.start()
    t2.start()

    # Чтобы не завершался главный поток
    t1.join()
    t2.join()