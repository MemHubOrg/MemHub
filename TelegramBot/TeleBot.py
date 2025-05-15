import pyotp
import telebot
import os

from DataBase import DB


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
            chat_id = str(message.chat.id)

            if not username:
                self.bot.reply_to(message, "У вас не установлен username в Telegram.")
                return

            try:
                self.db.create_user_with_chat_id(username=username, chat_id=chat_id)
                self.bot.reply_to(message, f"Привет, {username}! Ваш chat ID: {chat_id}")
            except Exception as e:
                self.bot.reply_to(message, f"Ошибка: {e}")

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
    
    def send_sticker(self, chat_id: str, sticker):
        return self.bot.send_sticker(chat_id=chat_id, sticker=sticker)

    def generate_code(self, secret: str) -> str:
        totp = pyotp.TOTP(secret, interval=300)
        return totp.now()

    def start(self) -> None:
        self.bot.polling(none_stop=True)