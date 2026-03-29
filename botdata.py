import requests
import time
import sqlite3
import os
import numpy as np
import threading
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional, Any

# Конфигурация
TOKEN = "8336344569:AAHhN67bsk8tbUpyJ1MMtgh72f-I1f2rKRk"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
ADMIN_ID = 8292372344
PORT = int(os.environ.get('PORT', 8080))

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация базы данных
db_conn = sqlite3.connect('users.db', check_same_thread=False)
db_cursor = db_conn.cursor()
db_cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        registration_date TEXT,
        calculated_timestamp INTEGER
    )
''')
db_conn.commit()

# Опорные точки для интерполяции
MILESTONES = {
    2768409: 1383264000000,
    7679610: 1388448000000,
    11538514: 1391212000000,
    15835244: 1392940000000,
    23646077: 1393459000000,
    38015510: 1393632000000,
    44634663: 1399334000000,
    46145305: 1400198000000,
    54845238: 1411257000000,
    63263518: 1414454000000,
    101260938: 1425600000000,
    101323197: 1426204000000,
    103151531: 1433376000000,
    103258382: 1432771000000,
    109393468: 1439078000000,
    111220210: 1429574000000,
    112594714: 1439683000000,
    116812045: 1437696000000,
    122600695: 1437782000000,
    124872445: 1439856000000,
    125828524: 1444003000000,
    130029930: 1441324000000,
    133909606: 1444176000000,
    143445125: 1448928000000,
    148670295: 1452211000000,
    152079341: 1453420000000,
    157242073: 1446768000000,
    171295414: 1457481000000,
    181783990: 1460246000000,
    222021233: 1465344000000,
    225034354: 1466208000000,
    278941742: 1473465000000,
    285253072: 1476835000000,
    294851037: 1479600000000,
    297621225: 1481846000000,
    328594461: 1482969000000,
    337808429: 1487707000000,
    341546272: 1487782000000,
    352940995: 1487894000000,
    369669043: 1490918000000,
    400169472: 1501459000000,
    805158066: 1563208000000,
    1974255900: 1634000000000,
    5520018289: 1721847912670,
    6000000000: 1738368000000,
    7000000000: 1746057600000,
    8000000000: 1754006400000,
    8300000000: 1759276800000,
    8600000000: 1767225600000,
    9000000000: 1774915200000
}

def get_current_date():
    return datetime.now()

class RegistrationAnalyzer:
    def __init__(self, milestones: Dict[int, int]):
        self.milestones = milestones
        self._prepare_interpolator()
    
    def _prepare_interpolator(self):
        ids = sorted(self.milestones.keys())
        timestamps = [self.milestones[i] for i in ids]
        self.ids_array = np.array(ids)
        self.ts_array = np.array(timestamps)
    
    def calculate_timestamp(self, user_id: int) -> int:
        if user_id <= self.ids_array[0]:
            return int(self.ts_array[0])
        
        if user_id >= self.ids_array[-1]:
            return int(self._extrapolate(user_id))
        
        timestamp = np.interp(user_id, self.ids_array, self.ts_array)
        return int(timestamp)
    
    def _extrapolate(self, user_id: int) -> float:
        last_5_ids = self.ids_array[-5:]
        last_5_ts = self.ts_array[-5:]
        coeffs = np.polyfit(last_5_ids, last_5_ts, 2)
        return np.polyval(coeffs, user_id)
    
    def calculate_age(self, reg_date: datetime) -> Tuple[int, int, int]:
        current = get_current_date()
        years = current.year - reg_date.year
        months = current.month - reg_date.month
        days = current.day - reg_date.day
        
        if days < 0:
            months -= 1
            prev_month = current.replace(day=1) - timedelta(days=1)
            days += prev_month.day
        
        if months < 0:
            years -= 1
            months += 12
        
        return years, months, days
    
    def get_precision(self, user_id: int) -> str:
        if user_id in self.milestones:
            return "эталонная точность"
        elif user_id <= self.ids_array[-1]:
            return "интерполяция"
        else:
            return "экстраполяция"
    
    def generate_report(self, user_id: int, reg_date: datetime, timestamp: int, username: str = None) -> str:
        years, months, days = self.calculate_age(reg_date)
        precision = self.get_precision(user_id)
        current = get_current_date()
        
        report = f"""РЕГИСТРАЦИОННЫЙ АНАЛИЗ - ID {user_id}
{'USERNAME: @' + username if username else ''}

дата регистрации: {reg_date.strftime('%d.%m.%Y %H:%M:%S')}
unix timestamp (мс): {timestamp}
возраст аккаунта: {years} лет, {months} мес, {days} дн

метод расчета: линейная интерполяция (numpy)
опорных точек: {len(self.milestones)}
точность: {precision}

анализ завершен: {current.strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report
    
    def generate_html_report(self, user_id: int, reg_date: datetime, timestamp: int, username: str = None) -> str:
        years, months, days = self.calculate_age(reg_date)
        precision = self.get_precision(user_id)
        current = get_current_date()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>report - {user_id}</title>
    <style>
        body {{
            background: #0a0e0a;
            color: #0f0;
            font-family: 'Courier New', monospace;
            padding: 30px;
            margin: 0;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #0f0;
            padding: 20px;
        }}
        .header {{
            border-bottom: 1px solid #0f0;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .field {{
            margin: 12px 0;
        }}
        .label {{
            color: #0a0;
            display: inline-block;
            width: 200px;
        }}
        .value {{
            color: #0f0;
        }}
        .footer {{
            border-top: 1px solid #0f0;
            margin-top: 20px;
            padding-top: 10px;
            font-size: 11px;
            color: #0a0;
        }}
        .precision {{
            color: #ff0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <strong>REGISTRATION ANALYSIS REPORT</strong>
        </div>
        
        <div class="field">
            <span class="label">id:</span>
            <span class="value">{user_id}</span>
        </div>
        {f'<div class="field"><span class="label">username:</span><span class="value">@{username}</span></div>' if username else ''}
        <div class="field">
            <span class="label">registration date:</span>
            <span class="value">{reg_date.strftime('%d.%m.%Y %H:%M:%S')}</span>
        </div>
        <div class="field">
            <span class="label">unix timestamp (ms):</span>
            <span class="value">{timestamp}</span>
        </div>
        <div class="field">
            <span class="label">account age:</span>
            <span class="value">{years} years, {months} months, {days} days</span>
        </div>
        <div class="field">
            <span class="label">interpolation method:</span>
            <span class="value">linear (numpy)</span>
        </div>
        <div class="field">
            <span class="label">reference points:</span>
            <span class="value">{len(self.milestones)}</span>
        </div>
        <div class="field">
            <span class="label">precision:</span>
            <span class="value precision">{precision}</span>
        </div>
        
        <div class="footer">
            completed: {current.strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
        return html

class TelegramBot:
    def __init__(self, token: str, admin_id: int):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.admin_id = admin_id
        self.analyzer = RegistrationAnalyzer(MILESTONES)
        self.user_states = {}
        self.user_data = {}
        self.user_messages = {}
        self.offset = 0
        os.makedirs('reports', exist_ok=True)
    
    def _make_request(self, method: str, params: Dict = None, files: Dict = None, retry_count: int = 3) -> Optional[Dict]:
        for attempt in range(retry_count):
            try:
                url = f"{self.base_url}/{method}"
                if files:
                    response = requests.post(url, data=params, files=files, timeout=15)
                else:
                    response = requests.post(url, json=params, timeout=15)
                
                if response.status_code == 429:
                    retry_after = response.json().get('parameters', {}).get('retry_after', 5)
                    logger.warning(f"rate limit, waiting {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                if response.status_code == 403:
                    logger.error(f"access denied: {method}")
                    return None
                
                return response.json()
                
            except requests.exceptions.Timeout:
                logger.warning(f"timeout attempt {attempt + 1}/{retry_count}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                continue
            except Exception as e:
                logger.error(f"api error: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                continue
        
        return None
    
    def send_message(self, chat_id: int, text: str, reply_markup: Dict = None) -> Optional[Dict]:
        params = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            params["reply_markup"] = reply_markup
        return self._make_request("sendMessage", params)
    
    def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: Dict = None) -> Optional[Dict]:
        params = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            params["reply_markup"] = reply_markup
        return self._make_request("editMessageText", params)
    
    def delete_message(self, chat_id: int, message_id: int) -> Optional[Dict]:
        return self._make_request("deleteMessage", {"chat_id": chat_id, "message_id": message_id})
    
    def answer_callback(self, callback_id: str, text: str = None) -> Optional[Dict]:
        params = {"callback_query_id": callback_id}
        if text:
            params["text"] = text
        return self._make_request("answerCallbackQuery", params)
    
    def get_main_keyboard(self, is_admin: bool = False) -> Dict:
        keyboard = [
            [{"text": "свой id + регистрация", "callback_data": "my_id_reg"}],
            [{"text": "по id", "callback_data": "method_id"}],
            [{"text": "переслать сообщение", "callback_data": "method_forward"}]
        ]
        
        if is_admin:
            keyboard.append([{"text": "админ-панель", "callback_data": "admin_panel"}])
        
        return {"inline_keyboard": keyboard}
    
    def get_result_keyboard(self) -> Dict:
        return {
            "inline_keyboard": [
                [{"text": "скачать txt", "callback_data": "download_txt"}, {"text": "скачать html", "callback_data": "download_html"}],
                [{"text": "назад", "callback_data": "back"}]
            ]
        }
    
    def get_admin_keyboard(self) -> Dict:
        return {
            "inline_keyboard": [
                [{"text": "статистика", "callback_data": "admin_stats"}],
                [{"text": "рассылка", "callback_data": "admin_broadcast"}],
                [{"text": "назад", "callback_data": "back"}]
            ]
        }
    
    def get_back_keyboard(self) -> Dict:
        return {"inline_keyboard": [[{"text": "назад", "callback_data": "back"}]]}
    
    def register_user(self, user_id: int, username: str = None, reg_date: str = None, timestamp: int = None):
        try:
            db_cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, registration_date, calculated_timestamp) VALUES (?, ?, ?, ?)",
                (user_id, username, reg_date, timestamp)
            )
            db_conn.commit()
        except Exception as e:
            logger.error(f"db error: {e}")
    
    def get_stats(self) -> int:
        try:
            db_cursor.execute("SELECT COUNT(*) FROM users")
            return db_cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"stats error: {e}")
            return 0
    
    def broadcast(self, message: str) -> int:
        try:
            db_cursor.execute("SELECT user_id FROM users")
            users = db_cursor.fetchall()
            count = 0
            
            for user in users:
                try:
                    self.send_message(user[0], message)
                    count += 1
                    time.sleep(0.05)
                except Exception as e:
                    logger.error(f"broadcast error: {e}")
            
            return count
        except Exception as e:
            logger.error(f"broadcast error: {e}")
            return 0
    
    def analyze_and_display(self, chat_id: int, target_id: int, username: str = None) -> Tuple[str, datetime, int]:
        timestamp = self.analyzer.calculate_timestamp(target_id)
        reg_date = datetime.fromtimestamp(timestamp / 1000)
        years, months, days = self.analyzer.calculate_age(reg_date)
        precision = self.analyzer.get_precision(target_id)
        
        result_text = f"id: {target_id}\n"
        if username:
            result_text += f"username: @{username}\n"
        result_text += f"\nдата регистрации: {reg_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
        result_text += f"возраст: {years} лет, {months} мес, {days} дн\n"
        result_text += f"точность: {precision}"
        
        return result_text, reg_date, timestamp
    
    def process_updates(self):
        while True:
            try:
                params = {"offset": self.offset, "timeout": 30}
                response = self._make_request("getUpdates", params)
                
                if response and response.get("ok"):
                    for update in response.get("result", []):
                        if "message" in update:
                            self.handle_message(update["message"])
                        elif "callback_query" in update:
                            self.handle_callback(update["callback_query"])
                        
                        self.offset = update["update_id"] + 1
                
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"updates error: {e}")
                time.sleep(5)
    
    def handle_message(self, message: Dict):
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username")
        
        if "text" in message and message["text"] == "/start":
            self.delete_message(chat_id, message["message_id"])
            resp = self.send_message(chat_id, "выберите действие:", 
                                    self.get_main_keyboard(user_id == self.admin_id))
            if resp and resp.get("result"):
                self.user_messages[chat_id] = resp["result"]["message_id"]
            return
        
        if "text" in message and chat_id in self.user_states:
            state = self.user_states[chat_id]
            text = message["text"].strip()
            self.delete_message(chat_id, message["message_id"])
            
            if state == "waiting_id":
                try:
                    target_id = int(text)
                    result_text, reg_date, timestamp = self.analyze_and_display(chat_id, target_id)
                    
                    self.user_data[chat_id] = {
                        "result_text": result_text,
                        "target_id": target_id,
                        "reg_date": reg_date,
                        "timestamp": timestamp,
                        "username": None
                    }
                    
                    self.edit_message(chat_id, self.user_messages[chat_id], result_text, self.get_result_keyboard())
                    self.user_states[chat_id] = None
                    
                except ValueError:
                    self.edit_message(chat_id, self.user_messages[chat_id], 
                                    "ошибка: введите числовой id", 
                                    self.get_back_keyboard())
            
            elif state == "waiting_broadcast":
                sent_count = self.broadcast(text)
                self.edit_message(chat_id, self.user_messages[chat_id], 
                                f"рассылка завершена\nотправлено: {sent_count} пользователей", 
                                self.get_back_keyboard())
                self.user_states[chat_id] = None
        
        if "forward_from" in message and chat_id in self.user_states and self.user_states[chat_id] == "waiting_forward":
            forward_from = message["forward_from"]
            target_id = forward_from["id"]
            username_forward = forward_from.get("username")
            
            self.delete_message(chat_id, message["message_id"])
            
            result_text, reg_date, timestamp = self.analyze_and_display(chat_id, target_id, username_forward)
            
            self.user_data[chat_id] = {
                "result_text": result_text,
                "target_id": target_id,
                "reg_date": reg_date,
                "timestamp": timestamp,
                "username": username_forward
            }
            
            self.edit_message(chat_id, self.user_messages[chat_id], result_text, self.get_result_keyboard())
            self.user_states[chat_id] = None
    
    def handle_callback(self, callback: Dict):
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        data = callback["data"]
        callback_id = callback["id"]
        user_id = callback["from"]["id"]
        username = callback["from"].get("username")
        
        if data == "my_id_reg":
            target_id = chat_id
            result_text, reg_date, timestamp = self.analyze_and_display(chat_id, target_id, username)
            
            self.register_user(target_id, username, reg_date.strftime('%d.%m.%Y %H:%M:%S'), timestamp)
            
            self.user_data[chat_id] = {
                "result_text": result_text,
                "target_id": target_id,
                "reg_date": reg_date,
                "timestamp": timestamp,
                "username": username
            }
            
            self.edit_message(chat_id, message_id, result_text, self.get_result_keyboard())
        
        elif data == "method_id":
            self.edit_message(chat_id, message_id, "введите id аккаунта:", self.get_back_keyboard())
            self.user_states[chat_id] = "waiting_id"
        
        elif data == "method_forward":
            self.edit_message(chat_id, message_id, "перешлите сообщение от пользователя:", self.get_back_keyboard())
            self.user_states[chat_id] = "waiting_forward"
        
        elif data == "download_txt":
            if chat_id in self.user_data and "target_id" in self.user_data[chat_id]:
                target_id = self.user_data[chat_id]["target_id"]
                reg_date = self.user_data[chat_id]["reg_date"]
                timestamp = self.user_data[chat_id]["timestamp"]
                username = self.user_data[chat_id].get("username")
                
                report_content = self.analyzer.generate_report(target_id, reg_date, timestamp, username)
                
                filename = f"reports/report_{target_id}_{int(time.time())}.txt"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(report_content)
                    
                    with open(filename, 'rb') as f:
                        self._make_request("sendDocument", 
                                          {"chat_id": chat_id}, 
                                          {"document": (f"report_{target_id}.txt", f)})
                    
                    self.answer_callback(callback_id, "txt отчет отправлен")
                    
                except Exception as e:
                    logger.error(f"download error: {e}")
                    self.answer_callback(callback_id, "ошибка")
                
                finally:
                    try:
                        if os.path.exists(filename):
                            os.remove(filename)
                    except:
                        pass
            else:
                self.answer_callback(callback_id, "нет данных")
        
        elif data == "download_html":
            if chat_id in self.user_data and "target_id" in self.user_data[chat_id]:
                target_id = self.user_data[chat_id]["target_id"]
                reg_date = self.user_data[chat_id]["reg_date"]
                timestamp = self.user_data[chat_id]["timestamp"]
                username = self.user_data[chat_id].get("username")
                
                html_content = self.analyzer.generate_html_report(target_id, reg_date, timestamp, username)
                
                filename = f"reports/report_{target_id}_{int(time.time())}.html"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    with open(filename, 'rb') as f:
                        self._make_request("sendDocument", 
                                          {"chat_id": chat_id}, 
                                          {"document": (f"report_{target_id}.html", f)})
                    
                    self.answer_callback(callback_id, "html отчет отправлен")
                    
                except Exception as e:
                    logger.error(f"download error: {e}")
                    self.answer_callback(callback_id, "ошибка")
                
                finally:
                    try:
                        if os.path.exists(filename):
                            os.remove(filename)
                    except:
                        pass
            else:
                self.answer_callback(callback_id, "нет данных")
        
        elif data == "admin_panel":
            if user_id == self.admin_id:
                self.edit_message(chat_id, message_id, "админ-панель", self.get_admin_keyboard())
            else:
                self.answer_callback(callback_id, "доступ запрещен")
        
        elif data == "admin_stats":
            if user_id == self.admin_id:
                stats = self.get_stats()
                self.edit_message(chat_id, message_id, f"статистика\n\nпользователей: {stats}", self.get_back_keyboard())
            else:
                self.answer_callback(callback_id, "доступ запрещен")
        
        elif data == "admin_broadcast":
            if user_id == self.admin_id:
                self.edit_message(chat_id, message_id, "введите текст рассылки:", self.get_back_keyboard())
                self.user_states[chat_id] = "waiting_broadcast"
            else:
                self.answer_callback(callback_id, "доступ запрещен")
        
        elif data == "back":
            self.edit_message(chat_id, message_id, "выберите действие:", 
                            self.get_main_keyboard(user_id == self.admin_id))
            self.user_states[chat_id] = None
        
        self.answer_callback(callback_id)

# Flask веб-сервер для поддержания активности
app = Flask(__name__)
bot = None

@app.route('/')
def index():
    return jsonify({"status": "active", "message": "bot is running", "time": datetime.now().isoformat()}), 200

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

def run_bot():
    global bot
    bot = TelegramBot(TOKEN, ADMIN_ID)
    bot.process_updates()

def run_web():
    app.run(host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    logger.info(f"запуск бота на порту {PORT}")
    
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    run_web()
