from flask import Flask, request, jsonify
from TeleBot import Bot
import pyotp

app = Flask(__name__)

# Инициализация бота
TOKEN = '7728653033:AAGLTd8eFy8XR8CNEHaHiR0O0ZJU4o-hMfI'
bot = Bot(token=TOKEN)


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