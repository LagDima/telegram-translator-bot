from http.server import BaseHTTPRequestHandler
import json, requests

BOT_TOKEN = "8858772185:AAGRTCwpkqzMdnqfBZhdch3wAUPWmeEnT8Y"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except: pass

def translate_text(text):
    try:
        r = requests.get("https://translate.googleapis.com/translate_a/single",
                         params={'client':'gtx','sl':'auto','tl':'ru','dt':'t','q':text}, timeout=5)
        if r.status_code == 200:
            return ''.join(part[0] for part in r.json()[0] if part[0])
        return "Ошибка перевода"
    except Exception as e:
        return f"Ошибка: {e}"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        if 'message' in data:
            chat = data['message']['chat']['id']
            text = data['message'].get('text', '')
            if text == '/start':
                send_message(chat, "✍️ Отправьте текст для перевода на русский")
            else:
                result = translate_text(text)
                send_message(chat, f"📝 Перевод:\n{result}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')
