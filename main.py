import telebot, db
from config import BOT_TOKEN
from handlers import start, register, search, keys, admin, plans

# Initialize DB and bot
db.init()
bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# Register bot handlers
start.register(bot)
register.register(bot)
search.register(bot)
keys.register(bot)
admin.register(bot)
plans.register(bot)

print("✅ OSINT Pro v2 running…")

# --- Flask Web App ---
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OSINT Pro Status</title>
        <style>
            body {
                background-color: #000;
                color: #00ff00;
                font-family: monospace;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            h1 {
                font-size: 2em;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>✅ OSINT Pro Bot is running…</h1>
    </body>
    </html>
    """

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Run Flask in background
threading.Thread(target=run_flask).start()

# Start bot
bot.infinity_polling()
