import logging
import threading
from config.config import bot
import bot.handlers as _handlers
from monitor.monitor import Monitor
from storage.database import init_db
logging.basicConfig(level=logging.INFO)

def main():
    init_db()

    monitor = Monitor()
    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()

    logging.info("Starting Telegram Bottas...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()