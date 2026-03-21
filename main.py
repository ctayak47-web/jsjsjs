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
port = int(os.environ.get("PORT", 8080))

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"bot is alive")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return

def run_web_server():
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

def load_db():
    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_db(data):
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

# инициализация базы
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
                    
                    # настройка в лс
                    if "message" in up and up["message"]["chat"]["type"] == "private":
                        msg = up["message"]
                        cid = msg["chat"]["id"]
                        text = msg.get("text", "")
                        if "|" in text:
                            try:
                                target_id, t_txt, t_lnk = text.split("|")
                                db[str(target_id.strip())] = {"t": t_txt.strip(), "l": t_lnk.strip()}
                                save_db(db)
                                request("sendMessage", {"chat_id": cid, "text": "done"})
                            except:
                                request("sendMessage", {"chat_id": cid, "text": "error"})
                        else:
                            request("sendMessage", {"chat_id": cid, "text": "айди|текст|ссылка"})

                    # обработка каналов
                    elif "channel_post" in up:
                        post = up["channel_post"]
                        chid = str(post["chat"]["id"])
                        mid = post["message_id"]
                        
                        if chid in db:
                            conf = db[chid]
                            # проверяем текст или описание (caption) для медиа
                            is_cap = "caption" in post
                            orig = post.get("caption") if is_cap else post.get("text")
                            
                            if orig and f"href='{conf['l']}'" not in orig:
                                link_html = f"<a href='{conf['l']}'>{conf['t']}</a>"
                                new_text = f"{orig}\n\n{link_html}"
                                
                                met = "editMessageCaption" if is_cap else "editMessageText"
                                par = {
                                    "chat_id": chid,
                                    "message_id": mid,
                                    "parse_mode": "html",
                                    "disable_web_page_preview": True
                                }
                                if is_cap: par["caption"] = new_text
                                else: par["text"] = new_text
                                
                                request(met, par)
            time.sleep(1)
        except:
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    run_bot()
