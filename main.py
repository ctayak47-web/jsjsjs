import requests
import time
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# конфигурация
token = os.environ.get("BOT_TOKEN", "7726206815:AAFT-IsYCyhoHNSVbCr3MlXvIw77dHnciY0")
api_url = f"https://api.telegram.org/bot{token}/"
db_file = "db.json"
port = int(os.environ.get("PORT", 8080)) # порт для render

# веб-сервер для "оживки" на хостинге
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"bot is alive")

def run_web_server():
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# логика бота
def load_db():
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

db = load_db()

def request(method, params):
    try:
        res = requests.post(api_url + method, data=params, timeout=20)
        return res.json()
    except:
        return None

def run_bot():
    global db
    offset = None
    while True:
        try:
            updates = request("getUpdates", {"offset": offset, "timeout": 20, "allowed_updates": ["message", "channel_post"]})
            if updates and "result" in updates:
                for up in updates["result"]:
                    offset = up["update_id"] + 1
                    
                    if "message" in up and up["message"]["chat"]["type"] == "private":
                        msg = up["message"]
                        chat_id = msg["chat"]["id"]
                        text = msg.get("text", "")
                        if "|" in text:
                            try:
                                cid, txt, lnk = text.split("|")
                                db[str(cid.strip())] = {"t": txt.strip(), "l": lnk.strip()}
                                save_db(db)
                                request("sendMessage", {"chat_id": chat_id, "text": "done"})
                            except:
                                request("sendMessage", {"chat_id": chat_id, "text": "error"})
                        else:
                            request("sendMessage", {"chat_id": chat_id, "text": "айди|текст|ссылка"})

                    elif "channel_post" in up:
                        post = up["channel_post"]
                        chid = str(post["chat"]["id"])
                        if chid in db:
                            conf = db[chid]
                            orig = post.get("text") or post.get("caption")
                            if orig and f"href='{conf['l']}'" not in orig:
                                link_text = f"<a href='{conf['l']}'>{conf['t']}</a>"
                                new = f"{orig}\n\n{link_text}"
                                met = "editMessageCaption" if "caption" in post else "editMessageText"
                                par = {"chat_id": chid, "message_id": post["message_id"], "parse_mode": "html", "disable_web_page_preview": True}
                                if "caption" in post: par["caption"] = new
                                else: par["text"] = new
                                request(met, par)
            time.sleep(1)
        except:
            time.sleep(5)

if __name__ == "__main__":
    # запуск веб-сервера в фоне
    threading.Thread(target=run_web_server, daemon=True).start()
    # запуск бота
    run_bot()
