from http.server import BaseHTTPRequestHandler
import json
import requests

BOT_TOKEN = "8858772185:AAGRTCwpkqzMdnqfBZhdch3wAUPWmeEnT8Y"

def send_message(chat_id, text):
    """Отправляет сообщение, разбивая длинный текст на части по 4096 символов"""
    MAX_LEN = 4096
    for i in range(0, len(text), MAX_LEN):
        chunk = text[i:i+MAX_LEN]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": chunk, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print("Send error:", e)

def translate_text(text):
    """Перевод текста через Google Translate (без ограничения на длину)"""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'auto',
            'tl': 'ru',
            'dt': 't',
            'q': text
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            translated = ''.join(part[0] for part in result[0] if part[0])
            return translated
        else:
            return f"Ошибка перевода (код {resp.status_code})"
    except Exception as e:
        return f"Ошибка: {str(e)[:100]}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            if text == '/start':
                send_message(chat_id, "✍️ *Привет!*\nОтправь мне любой текст (хоть целую статью), я переведу на русский. Длинные переводы пришлю несколькими сообщениями.")
            else:
                translated = translate_text(text)
                send_message(chat_id, f"📝 *Перевод:*\n{translated}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running. Use Telegram to send messages.')
