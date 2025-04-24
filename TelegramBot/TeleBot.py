import pyotp
import telebot
import os
from telebot import types
import logging

from DataBase import DB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Bot():
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.db = DB(
            db_name=os.getenv("POSTGRES_DB", "django_db"),
            db_user=os.getenv("POSTGRES_USER", "django_user"),
            db_password=os.getenv("POSTGRES_PASSWORD", "django_password"),
            db_host=os.getenv("DB_HOST", "db"),
            db_port=int(os.getenv("DB_PORT", "5431"))
        )

        self.setup_handlers()

    def setup_handlers(self) -> None:
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            username = message.from_user.username
            username_db = self.db.get_data("username", username)

            if username == username_db:
                self.db.update_data(data=message.chat.id, username=username)

            self.bot.reply_to(message, "Привет! Ваш chat ID: {}, username: {}".format(message.chat.id, username))

        @self.bot.message_handler(func=lambda message: True)
        def send_code(message):
            chat_id = str(message.chat.id)
            username = self.db.get_data("username", chat_id)
            secret = self.db.get_data("secret", username)

            if not secret or not chat_id:
                self.bot.reply_to(message, "Не удалось получить данные для вашего аккаунта.")
                return

            verification_code = self.generate_code(secret)
            self.send_verification_code(chat_id, verification_code)

    def send_verification_code(self, chat_id: str, code: str) -> None:
        self.bot.send_message(chat_id, f"Ваш код верификации: {code}")

    def generate_code(self, secret: str) -> str:
        totp = pyotp.TOTP(secret, interval=300)
        return totp.now()

    def start(self) -> None:
        self.bot.polling(none_stop=True)