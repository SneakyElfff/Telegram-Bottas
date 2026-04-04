import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.config import bot
from storage.database import add_subscriber, remove_subscriber, set_timezone

logger = logging.getLogger(__name__)

@bot.message_handler(commands=["start", "subscribe"])
def handle_subscribe(message):
    if add_subscriber(message.chat.id):
        bot.reply_to(message, "Subscribed to FIA Press Conference alerts!")
        logger.info(f"New subscriber: {message.chat.id}")
    else:
        bot.reply_to(message, "You are already subscribed.")

@bot.message_handler(commands=["unsubscribe"])
def handle_unsubscribe(message):
    if remove_subscriber(message.chat.id):
        bot.reply_to(message, "Unsubscribed from FIA Press Conference alerts.")
        logger.info(f"Unsubscribed: {message.chat.id}")
    else:
        bot.reply_to(message, "You were not subscribed.")

@bot.message_handler(commands=["timezone"])
def handle_timezone(message):
    markup = InlineKeyboardMarkup(row_width=4)

    buttons = []
    for i in range(-12, 15, 1):
        text = "UTC" + ("+" if i>=0 else "") + str(i)
        btn = InlineKeyboardButton(text, callback_data=f"set_tz:{text}")
        buttons.append(btn)

    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        "Please, choose your preferred timezone for F1 press schedule.",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_tz:"))
def handle_timezone_callback(call):
    timezone = call.data.split(":", 1)[1]

    if set_timezone(call.message.chat.id, timezone):
        bot.answer_callback_query(call.id, f"Timezone set to {timezone}.")

        bot.edit_message_text(
            f"Your timezone is now **{timezone}**.\n"
            "All future press conference notifications will use this timezone.",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

        logger.info(f"Timezone set to {timezone} for {call.message.chat.id}.")
    else:
        bot.answer_callback_query(call.id, "Timezone not set.")