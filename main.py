# -*- coding: utf-8 -*-
"""
main.py - Точка входа для Render.com (Web Service)

Поднимает:
  1. Flask-сервер (для UptimeRobot + PORT для Render)
  2. combined-бот (BOT_TOKEN) — сингулярное ядро + экономика
  3. regbot (BOT_TOKEN_DATA) — анализ даты регистрации
  4. profile-бот (BOT_TOKEN_PROFILE) — генератор мокапа профиля
  5. cumbot (BOT_TOKEN_CUM) — "кончаБот" со счётчиком кончи

Все боты запускаются в отдельных потоках и работают параллельно.
"""

import os
import threading
import logging

from flask import Flask, jsonify

from app import combined_bot
from app.regbot import bot as regbot_module
from app import profile_bot
from app import cumbot_runner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", static_url_path="")


@app.route("/")
def index():
    """Главная страница"""
    try:
        return app.send_static_file("index.html")
    except:
        return jsonify({"status": "online", "message": "Unified Telegram Bots"})


@app.route("/ping")
def ping():
    """Ping для UptimeRobot"""
    return jsonify({"status": "online"})


@app.route("/health")
def health():
    """Статус всех компонентов"""
    return jsonify({
        "status": "ok",
        "combined_bot": bool(os.environ.get("BOT_TOKEN")),
        "regbot": bool(os.environ.get("BOT_TOKEN_DATA")),
        "profile_bot": bool(os.environ.get("BOT_TOKEN_PROFILE")),
        "cumbot": bool(os.environ.get("BOT_TOKEN_CUM")),
    })


def _run_safely(fn, name: str):
    """Запустить функцию безопасно с логированием ошибок"""
    try:
        logger.info(f"[{name}] запускаю...")
        fn()
    except Exception as e:
        logger.error(f"[{name}] fatal error: {e}", exc_info=True)


def main():
    """Главная функция запуска"""
    
    # Инициализируем БД для КончаБота
    try:
        from app.cumbot import db as cumbot_db
        cumbot_db.init()
    except Exception as e:
        logger.warning(f"Ошибка при инициализации БД КончаБота: {e}")
    
    # Запускаем каждый бот в отдельном потоке
    threads = []
    
    # 1. Combined Bot (с сингулярностью и экономикой)
    if os.environ.get("BOT_TOKEN"):
        thread = threading.Thread(
            target=_run_safely,
            args=(combined_bot.run, "combined_bot"),
            daemon=True,
            name="combined_bot_thread"
        )
        thread.start()
        threads.append(thread)
        logger.info("✓ combined_bot запущен в отдельном потоке")
    
    # 2. RegBot (анализ даты регистрации)
    if os.environ.get("BOT_TOKEN_DATA"):
        thread = threading.Thread(
            target=_run_safely,
            args=(regbot_module.run, "regbot"),
            daemon=True,
            name="regbot_thread"
        )
        thread.start()
        threads.append(thread)
        logger.info("✓ regbot запущен в отдельном потоке")
    
    # 3. Profile Bot (генератор профиля)
    if os.environ.get("BOT_TOKEN_PROFILE"):
        profile_bot_instance = profile_bot.create_bot()
        if profile_bot_instance:
            def run_profile_bot():
                profile_bot.run(profile_bot_instance)
            
            thread = threading.Thread(
                target=_run_safely,
                args=(run_profile_bot, "profile_bot"),
                daemon=True,
                name="profile_bot_thread"
            )
            thread.start()
            threads.append(thread)
            logger.info("✓ profile_bot запущен в отдельном потоке")
    
    # 4. CumBot (кончаБот)
    if os.environ.get("BOT_TOKEN_CUM"):
        cumbot_instance = cumbot_runner.create_bot()
        if cumbot_instance:
            def run_cumbot():
                cumbot_runner.run(cumbot_instance)
            
            thread = threading.Thread(
                target=_run_safely,
                args=(run_cumbot, "cumbot"),
                daemon=True,
                name="cumbot_thread"
            )
            thread.start()
            threads.append(thread)
            logger.info("✓ cumbot запущен в отдельном потоке")
    
    logger.info(f"✓ Всего запущено ботов: {len(threads)}")
    logger.info("=" * 60)
    logger.info("Запускаю Flask веб-сервер для Render.com...")
    logger.info("=" * 60)
    
    # Запускаем Flask веб-сервер (главный поток)
    port = int(os.environ.get("PORT", 8080))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False,
        threaded=True
    )


if __name__ == "__main__":
    main()
