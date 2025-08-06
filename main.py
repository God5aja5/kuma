import telebot, db
from config import BOT_TOKEN
from handlers import start, register, search, keys, admin, plans

db.init()
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

start.register(bot)
register.register(bot)
search.register(bot)
keys.register(bot)
admin.register(bot)
plans.register(bot)

print("✅ OSINT Pro v2 running…")
bot.infinity_polling()