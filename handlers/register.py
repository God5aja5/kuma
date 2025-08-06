import db, telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🔍 Phone",      callback_data="menu_phone"),
        InlineKeyboardButton("🆔 Aadhaar",    callback_data="menu_aadhaar"),
        InlineKeyboardButton("🚗 Vehicle",    callback_data="menu_vehicle"),
        InlineKeyboardButton("🍚 Ration",     callback_data="menu_ration"),
        InlineKeyboardButton("💳 Redeem Key", callback_data="redeem"),
        InlineKeyboardButton("👤 Profile",    callback_data="profile")
    )
    return kb

def register(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda c: c.data == "register")
    def reg(c):
        bot.answer_callback_query(c.id, "✅ Registered!")
        bot.edit_message_text("⚡ *Welcome to OSINT Pro*", c.message.chat.id, c.message.message_id,
                              parse_mode="Markdown", reply_markup=main_menu())

    @bot.callback_query_handler(func=lambda c: c.data == "main_menu")
    def back(c):
        bot.edit_message_text("⚡ *Main Menu*", c.message.chat.id, c.message.message_id,
                              parse_mode="Markdown", reply_markup=main_menu())

    @bot.callback_query_handler(func=lambda c: c.data == "profile")
    def profile(c):
        uid = c.from_user.id
        u = db.get_user(uid)
        credits = db.get_credits(uid)
        history = len(db.get_history(uid))
        txt = (
            f"👤 *Profile*\n"
            f"┌─\n"
            f"│ ID: `{uid}`\n"
            f"│ Name: `{u[2]}`\n"
            f"│ Credits: `{credits}`\n"
            f"│ Searches: `{history}`\n"
            f"└─"
        )
        bot.send_message(uid, txt, parse_mode="Markdown",
                         reply_markup=InlineKeyboardMarkup().add(
                             InlineKeyboardButton("🔙 Back", callback_data="main_menu")))
