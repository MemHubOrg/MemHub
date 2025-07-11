import requests
import logging

from PIL import Image
from io import BytesIO
from flask import Flask, request, jsonify
from TeleBot import Bot

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
# TOKEN = '7912191924:AAFX18u5GXj0vP1HWc0yk1Keoqx4O6XgeJ0'
TOKEN = '7728653033:AAGLTd8eFy8XR8CNEHaHiR0O0ZJU4o-hMfI'
# TOKEN = '7958894633:AAGtpGxa9CSIyGLOeobjdEwWhOcCQS7V0Qs'

bot = Bot(token=TOKEN)

@app.route('/send_meme', methods=['POST'])
def send_meme():
    try:
        chat_id = request.form.get('chat_id')
        image_url = request.form.get('image_url')

        if not chat_id or not image_url:
            return jsonify({'success': False, 'message': 'chat_id и image_url обязательны'}), 400

        # Скачиваем из S3
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))

        # Обрезаем и сжимаем до 512x512
        img = img.convert("RGBA")
        img.thumbnail((512, 512))

        # Сохраняем во временный буфер в webp
        buffer = BytesIO()
        img.save(buffer, format="WEBP")
        buffer.seek(0)

        # Отправка в Telegram
        response = bot.send_sticker(chat_id, buffer)

        if response:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': response.text}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/send_code', methods=['POST'])
def send_code():
    try:
        data = request.json
        username = data.get('username')
        token = data.get('token')

        chat_id = bot.db.get_data("chat_id", username)

        if not token or not chat_id:
            return jsonify({"status": "error", "message": "User not found"}), 404

        verification_code = bot.generate_code(token)
        bot.send_verification_code(chat_id, verification_code)

        return jsonify({"status": "success", "message": "Code sent"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)