import telebot, db
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.register import main_menu

def register(bot: telebot.TeleBot):
    @bot.message_handler(commands=["start"])
    def start(m):
        uid = m.from_user.id
        un  = m.from_user.username
        fn  = m.from_user.full_name

        if db.get_user(uid):
            return bot.send_message(uid, "⚡ *Welcome back!*", parse_mode="Markdown", reply_markup=main_menu())
        
        db.user_add(uid, un, fn)
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Register & Unlock", callback_data="register")
        )
        bot.send_message(uid, "🔐 *Welcome to OSINT Pro*\nTap below to register.",
                         parse_mode="Markdown", reply_markup=kb)