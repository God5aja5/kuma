import telebot, db, sqlite3, time, html
from config import ADMIN_IDS
from export_json import export_user_data

def register(bot: telebot.TeleBot):
    @bot.message_handler(commands=["addcr"])
    def addcr(m):
        if m.from_user.id not in ADMIN_IDS: return
        try:
            _, uid, amt = m.text.split()
            db.add_credits(int(uid), int(amt))
            bot.reply_to(m, f"✅ Added {amt} credits to {uid}")
            bot.send_message(int(uid), f"🎉 *Congratulations!* You received `{amt}` credits!", parse_mode="Markdown")
        except:
            bot.reply_to(m, "Usage: /addcr <user_id> <amount>")

    @bot.message_handler(commands=["broadcast"])
    def broadcast(m):
        if m.from_user.id not in ADMIN_IDS: return
        if not m.reply_to_message or not m.reply_to_message.text:
            return bot.reply_to(m, "Reply to a text message to broadcast.")
        text = html.escape(m.reply_to_message.text)
        users = db.all_users()
        ok = 0
        for uid in users:
            try:
                bot.send_message(uid, text, parse_mode="HTML")
                ok += 1
            except: pass
            time.sleep(0.05)
        bot.reply_to(m, f"📣 Sent to {ok}/{len(users)} users.")

    @bot.message_handler(commands=["status"])
    def status(m):
        if m.from_user.id not in ADMIN_IDS: return
        users = len(db.all_users())
        searches = db.total_searches()
        bar = "█" * min(20, searches // 100) + "░" * max(0, 20 - searches // 100)
        bot.reply_to(
            m,
            f"📊 *Status*\n"
            f"┌─\n"
            f"│ Total Users: `{users}`\n"
            f"│ Total Searches: `{searches}`\n"
            f"│ Progress: `{bar}`\n"
            f"└─",
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["info"])
    def info(m):
        uid = m.from_user.id
        u = db.get_user(uid)
        credits = db.get_credits(uid)
        searches = len(db.get_history(uid))
        bot.reply_to(
            m,
            f"👤 *Your Info*\n"
            f"┌─\n"
            f"│ ID: `{uid}`\n"
            f"│ Name: `{u[2]}`\n"
            f"│ Credits: `{credits}`\n"
            f"│ Searches: `{searches}`\n"
            f"└─",
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["fetch"])
    def fetch_data(m):
        if m.from_user.id not in ADMIN_IDS: return
        try:
            path = export_user_data()
            with open(path, "rb") as f:
                bot.send_document(m.chat.id, f, caption="📦 Full user data exported.")
        except Exception as e:
            bot.reply_to(m, f"❌ Export failed: {e}")
