import logging
import threading
from config.config import bot
import bot.handlers as _handlers
from config.logging_config import setup_logging
from monitor.monitor import Monitor
from storage.database import init_db, update_db

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    init_db()
    update_db()

    monitor = Monitor()
    monitor_thread = threading.Thread(target=monitor.run, daemon=True)
    monitor_thread.start()

    logger.info("Starting Telegram Bottas...")
    bot.infinity_polling()

if __name__ == "__main__":
    main()