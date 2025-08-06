# handlers/plans.py

import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def register(bot: telebot.TeleBot):
    @bot.message_handler(commands=["plans"])
    def send_plans(m: Message):
        text = (
            "🤖 *WELCOME TO OSINT PRO PLANS*\n\n"
            "💠 Unlock full OSINT power instantly\n"
            "🔍 _Every search costs just_ *5 credits* (= ₹3)\n\n"
            "📦 *PLANS*\n"
            "━━━━━━━━━━━━━━━\n"
            "🔹 ₹60     → 💳 100 Credits\n"
            "🔹 ₹150    → 💳 250 Credits\n"
            "🔹 ₹300    → 💳 500 Credits\n"
            "🔹 ₹450    → 💳 750 Credits\n"
            "🔹 ₹600    → 💳 1000 Credits *(Max Pack)*\n\n"
            "💡 _Example:_\n"
            "5 Credits = 1 Search\n"
            "100 Credits = 20 Searches\n"
            "1000 Credits = 200 Searches 🔥\n\n"
            "📩 *To Buy Credits:* Contact admin below\n\n"
            "🚀 Full UI | 💯 Premium Tools | 🔐 Instant Activation\n\n"
            "🛡️ *Secure. Private. Powerful.*\n"
            "_OSINT PRO — Trusted by Cyber Hunters._"
        )

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("📩 Contact Admin", url="https://t.me/SILENT_IS_HERE"))

        bot.send_message(m.chat.id, text, parse_mode="Markdown", reply_markup=kb)