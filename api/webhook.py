from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

BOT_TOKEN = "8858772185:AAGRTCwpkqzMdnqfBZhdch3wAUPWmeEnT8Y"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "zh": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "ko": "🇰🇷 한국어",
    "it": "🇮🇹 Italiano",
    "tr": "🇹🇷 Türkçe",
    "pl": "🇵🇱 Polski",
}

DEFAULT_LANG = "ru"
user_languages = {}

def send_message(chat_id, text, reply_markup=None):
    url = f"{TG_API}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)

def send_action(chat_id, action):
    url = f"{TG_API}/sendChatAction"
    requests.post(url, json={"chat_id": chat_id, "action": action})

def translate_text(text, target_lang):
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source='auto', target=target_lang)
    return translator.translate(text)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if not update:
        return "OK", 200
    
    if "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data = query["data"]
        user_id = query["from"]["id"]
        
        if data == "choose_lang":
            keyboard = {"inline_keyboard": []}
            row = []
            for i, (code, name) in enumerate(LANGUAGES.items()):
                row.append({"text": name, "callback_data": f"set_lang_{code}"})
                if (i + 1) % 2 == 0:
                    keyboard["inline_keyboard"].append(row)
                    row = []
            if row:
                keyboard["inline_keyboard"].append(row)
            keyboard["inline_keyboard"].append([{"text": "🔙 Назад", "callback_data": "back"}])
            send_message(chat_id, "🌐 *Выберите язык для перевода:*", keyboard)
            
        elif data.startswith("set_lang_"):
            lang_code = data.replace("set_lang_", "")
            user_languages[user_id] = lang_code
            keyboard = {"inline_keyboard": [[{"text": "🌐 Сменить язык", "callback_data": "choose_lang"}]]}
            send_message(chat_id, f"✅ *Язык перевода изменён на:* {LANGUAGES.get(lang_code, lang_code)}\n\n✍️ Теперь отправь мне текст для перевода!", keyboard)
            
        elif data == "back":
            current_lang = user_languages.get(user_id, DEFAULT_LANG)
            keyboard = {"inline_keyboard": [[{"text": "🌐 Выбрать язык", "callback_data": "choose_lang"}]]}
            send_message(chat_id, f"🏠 *Главное меню*\n\n🌍 Текущий язык перевода: {LANGUAGES.get(current_lang, current_lang)}\n\n📤 Отправь мне текст, и я переведу его на выбранный язык!", keyboard)
        
        return "OK", 200
    
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_id = update["message"]["from"]["id"]
        text = update["message"]["text"]
        
        if text == "/start":
            user_languages[user_id] = DEFAULT_LANG
            keyboard = {"inline_keyboard": [[{"text": "🌐 Выбрать язык", "callback_data": "choose_lang"}]]}
            send_message(chat_id, "✍️ *Привет! Я переводчик для иностранных статей.*\n\n📌 *Как пользоваться:*\n1️⃣ Отправь мне текст на любом языке\n2️⃣ Нажми на кнопку выбора языка внизу\n3️⃣ Получи готовый перевод!\n\n" + f"🌍 *Текущий язык перевода:* {LANGUAGES.get(DEFAULT_LANG, DEFAULT_LANG)}", keyboard)
            return "OK", 200
        
        target_lang = user_languages.get(user_id, DEFAULT_LANG)
        send_action(chat_id, "typing")
        
        try:
            translated = translate_text(text, target_lang)
            keyboard = {"inline_keyboard": [[{"text": "🌐 Сменить язык", "callback_data": "choose_lang"}]]}
            response = f"🔹 *Исходный язык:* автоматически\n🔸 *Перевод на:* {LANGUAGES.get(target_lang, target_lang)}\n\n📝 *Результат:*\n{translated}"
            send_message(chat_id, response, keyboard)
        except Exception as e:
            send_message(chat_id, f"❌ *Ошибка перевода:* {str(e)[:100]}\n\nПопробуйте снова.")
    
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "Telegram Bot is running!", 200