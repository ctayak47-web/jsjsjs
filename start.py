import os
import asyncio
import threading
import uvicorn
from backend.main import app
from bot import start_bot

def run_bot():
    asyncio.run(start_bot())

def main():
    threading.Thread(target=run_bot, daemon=True).start()
    port=int(os.getenv("PORT","8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__=="__main__":
    main()
