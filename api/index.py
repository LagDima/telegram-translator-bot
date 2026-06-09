import json
import requests

BOT_TOKEN = "8858772185:AAGRTCwpkqzMdnqfBZhdch3wAUPWmeEnT8Y"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{TG_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print("Send error:", e)

def translate_text(text, target_lang='ru'):
    # Прямой запрос к Google Translate (без сторонних библиотек)
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': target_lang,
            'dt': 't',
            'q': text
        }
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            result = resp.json()
            # извлекаем перевод
            translated = ''.join(part[0] for part in result[0] if part[0])
            return translated
        else:
            return f"Ошибка перевода (код {resp.status_code})"
    except Exception as e:
        return f"Ошибка: {str(e)[:100]}"

def handler(request, response):
    """Точка входа для Vercel"""
    # Обрабатываем только POST-запросы от Telegram
    if request.method == 'POST':
        try:
            update = json.loads(request.body)
        except Exception as e:
            response.status_code = 400
            return response

        if 'message' in update:
            msg = update['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')

            if text == '/start':
                send_message(chat_id, "✍️ *Привет!*\nОтправь мне текст на любом языке, я переведу его на русский.")
            else:
                translated = translate_text(text)
                send_message(chat_id, f"📝 *Перевод:*\n{translated}")

        response.status_code = 200
        return response

    # GET-запрос для проверки работы
    response.status_code = 200
    response.body = "Bot is running"
    return response
