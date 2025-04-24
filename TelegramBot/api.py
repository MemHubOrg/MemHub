from flask import Flask, request, jsonify
from TeleBot import Bot
import requests

app = Flask(__name__)

# Инициализация бота
TOKEN = '7728653033:AAGLTd8eFy8XR8CNEHaHiR0O0ZJU4o-hMfI'
TOKEN = '7958894633:AAGtpGxa9CSIyGLOeobjdEwWhOcCQS7V0Qs'
bot = Bot(token=TOKEN)

@app.route('/send_meme', methods=['POST'])
def send_meme():
    try:
        chat_id = request.form.get('chat_id')
        photo_file = request.files.get('file')

        if not chat_id or not photo_file:
            return jsonify({'success': False, 'message': 'chat_id и файл обязательны'}), 400

        # Отправка в Telegram
        url = f'https://api.telegram.org/bot{TOKEN}/sendPhoto'
        response = requests.post(url, data={
            'chat_id': chat_id,
            'caption': 'Вот твой мем!'
        }, files={
            'photo': (photo_file.filename, photo_file.stream, photo_file.mimetype)
        })

        if response.status_code == 200:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'message': response.text}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/send_code', methods=['POST'])
def send_code():
    try:
        data = request.json
        username = data.get('username')

        secret = bot.db.get_data("secret", username)
        chat_id = bot.db.get_data("chat_id", username)

        if not secret or not chat_id:
            return jsonify({"status": "error", "message": "User not found"}), 404

        verification_code = bot.generate_code(secret)
        bot.send_verification_code(chat_id, verification_code)

        return jsonify({"status": "success", "message": "Code sent"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)