import logging
from config.config import bot
from storage.database import add_subscriber, remove_subscriber

@bot.message_handler(commands=["start", "subscribe"])
def handle_subscribe(message):
    if add_subscriber(message.chat.id):
        bot.reply_to(message, "Subscribed to FIA Press Conference alerts!")
        logging.info(f"New subscriber: {message.chat.id}")
    else:
        bot.reply_to(message, "You are already subscribed.")

@bot.message_handler(commands=["unsubscribe"])
def handle_unsubscribe(message):
    if remove_subscriber(message.chat.id):
        bot.reply_to(message, "Unsubscribed from FIA Press Conference alerts.")
        logging.info(f"Unsubscribed: {message.chat.id}")
    else:
        bot.reply_to(message, "You were not subscribed.")