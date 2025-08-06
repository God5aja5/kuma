import telebot, db
from config import ADMIN_IDS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda c: c.data == "redeem")
    def ask(c):
        bot.send_message(c.message.chat.id, "🔑 Send the key:")
        bot.register_next_step_handler_by_chat_id(c.message.chat.id, redeem)

    def redeem(m):
        msg = db.redeem_key(m.from_user.id, m.text.strip())
        bot.reply_to(m, msg, parse_mode="Markdown")
        if "✅" in msg:
            total = db.get_credits(m.from_user.id)
            bot.reply_to(m, f"🎉 *Congratulations!* Your balance is now `{total}` credits 🎊",
                         parse_mode="Markdown")

    @bot.message_handler(commands=["redeem"])
    def redeem_cmd(m):
        bot.send_message(m.chat.id, "🔑 Send the key:")
        bot.register_next_step_handler(m, redeem)

    @bot.message_handler(commands=["key"])
    def gen_cmd(m):
        if m.from_user.id not in ADMIN_IDS: return
        try:
            parts = m.text.split()
            credits = int(parts[1])
            uses = int(parts[2]) if len(parts) > 2 else 1
            key = db.gen_key(credits, uses)
            bot.reply_to(m, f"🎟️ Key: `{key}`\n💳 Credits: {credits}\n👥 Uses: {uses}",
                         parse_mode="Markdown")
        except:
            bot.reply_to(m, "Usage: /key <credits> [max_uses=1]")
