from flask import Flask, request
import requests
import json
from deep_translator import GoogleTranslator

app = Flask(__name__)

BOT_TOKEN = "8858772185:AAGRTCwpkqzMdnqfBZhdch3wAUPWmeEnT8Y"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

LANGUAGES = {
    "ru": "🇷🇺 Русский", "en": "🇬🇧 English", "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français", "es": "🇪🇸 Español", "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語", "ko": "🇰🇷 한국어", "it": "🇮🇹 Italiano",
    "tr": "🇹🇷 Türkçe", "pl": "🇵🇱 Polski",
}
DEFAULT_LANG = "ru"
user_languages = {}

def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(f"{TG_API}/sendMessage", json=payload)

def send_action(chat_id, action):
    requests.post(f"{TG_API}/sendChatAction", json={"chat_id": chat_id, "action": action})

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200

    # Обработка нажатий на кнопки
    if "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        user_id = query["from"]["id"]
        data = query["data"]

        if data == "choose_lang":
            kb = {"inline_keyboard": []}
            row = []
            for i, (code, name) in enumerate(LANGUAGES.items()):
                row.append({"text": name, "callback_data": f"set_lang_{code}"})
                if (i+1) % 2 == 0:
                    kb["inline_keyboard"].append(row)
                    row = []
            if row:
                kb["inline_keyboard"].append(row)
            kb["inline_keyboard"].append([{"text": "🔙 Назад", "callback_data": "back"}])
            send_message(chat_id, "🌐 *Выберите язык для перевода:*", kb)

        elif data.startswith("set_lang_"):
            lang = data.replace("set_lang_", "")
            user_languages[user_id] = lang
            kb = {"inline_keyboard": [[{"text": "🌐 Сменить язык", "callback_data": "choose_lang"}]]}
            send_message(chat_id, f"✅ *Язык перевода изменён на:* {LANGUAGES.get(lang, lang)}\n\n✍️ Теперь отправь мне текст!", kb)

        elif data == "back":
            cur = user_languages.get(user_id, DEFAULT_LANG)
            kb = {"inline_keyboard": [[{"text": "🌐 Выбрать язык", "callback_data": "choose_lang"}]]}
            send_message(chat_id, f"🏠 *Главное меню*\n\n🌍 Текущий язык: {LANGUAGES.get(cur, cur)}\n\n📤 Отправь текст для перевода!", kb)
        return "OK", 200

    # Обработка обычных сообщений
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_id = update["message"]["from"]["id"]
        text = update["message"]["text"]

        if text == "/start":
            user_languages[user_id] = DEFAULT_LANG
            kb = {"inline_keyboard": [[{"text": "🌐 Выбрать язык", "callback_data": "choose_lang"}]]}
            send_message(chat_id, "✍️ *Привет! Я переводчик статей.*\n\n1️⃣ Отправь текст\n2️⃣ Нажми кнопку выбора языка\n3️⃣ Получи перевод!\n\n" + f"🌍 *Текущий язык:* {LANGUAGES.get(DEFAULT_LANG, DEFAULT_LANG)}", kb)
            return "OK", 200

        target = user_languages.get(user_id, DEFAULT_LANG)
        send_action(chat_id, "typing")
        try:
            translated = GoogleTranslator(source='auto', target=target).translate(text)
            kb = {"inline_keyboard": [[{"text": "🌐 Сменить язык", "callback_data": "choose_lang"}]]}
            response = f"🔹 *Исходный язык:* автоматически\n🔸 *Перевод на:* {LANGUAGES.get(target, target)}\n\n📝 *Результат:*\n{translated}"
            send_message(chat_id, response, kb)
        except Exception as e:
            send_message(chat_id, f"❌ *Ошибка перевода:* {str(e)[:100]}")
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running", 200
