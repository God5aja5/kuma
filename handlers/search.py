import telebot, utils, db, re, json, os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_IDS

def register(bot: telebot.TeleBot):
    @bot.callback_query_handler(func=lambda c: c.data.startswith("menu_"))
    def ask(c):
        typ = c.data.split("_")[1]
        bot.send_message(c.message.chat.id, f"📩 Send the **{typ.upper()}** number:", parse_mode="Markdown")
        bot.register_next_step_handler_by_chat_id(c.message.chat.id, do_search, typ)

    def do_search(m, typ):
        num = m.text.strip()
        uid = m.from_user.id
        if uid not in ADMIN_IDS and db.get_credits(uid) < 5:
            return bot.reply_to(m, "❌ *Insufficient credits*\nBuy from /plans", parse_mode="Markdown")

        prog = bot.send_message(m.chat.id, "⏳ *Searching…*", parse_mode="Markdown")

        try:
            url_map = {
                "phone": f"https://glonova.in/ia/kak.php/?num={num}",
                "aadhaar": f"https://millionmack.com/adhar.php?term={num}",
                "vehicle": f"https://api-vehicle-osint.vercel.app/?rc={num}",
                "ration": f"https://appi.ytcampss.store/Osint/ration.php?id={num}"
            }
            raw = utils.fetch(url_map[typ])
            if not raw:
                out = "`NOT FOUND`"
            else:
                out = {
                    "phone": utils.fmt_phone(raw, num),
                    "aadhaar": utils.fmt_aadhar(raw, num),
                    "vehicle": utils.fmt_vehicle(raw),
                    "ration": utils.fmt_ration(raw)
                }[typ]
        except Exception as e:
            out = f"`ERROR: {e}`"

        if uid not in ADMIN_IDS:
            db.add_credits(uid, -5)
        db.log_search(uid, num, typ, out)

        bot.edit_message_text(out, prog.chat.id, prog.message_id, parse_mode="Markdown")

        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("📄 Get Report – 1 Credit", callback_data=f"report_{typ}_{num}")
        )
        bot.send_message(m.chat.id, "📥 Want a shareable report?", reply_markup=kb)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("report_"))
    def report(c):
        uid = c.from_user.id
        _, typ, query = c.data.split("_", 2)
        if db.get_credits(uid) < 1:
            bot.answer_callback_query(c.id, "❌ Not enough credits\nBuy from /plans", show_alert=True)
            return
        bot.answer_callback_query(c.id, "🔓 Creating report…")

        template_map = {
            "phone": "number.html",
            "aadhaar": "uid.html",
            "vehicle": "vehicle.html",
            "ration": "ration.html"
        }
        template_path = f"reports/{template_map[typ]}"
        if not os.path.exists(template_path):
            bot.send_message(uid, "⚠️ Template missing.")
            return
        html = open(template_path).read()

        try:
            raw = utils.fetch({
                "phone": f"https://glonova.in/ia/kak.php/?num={query}",
                "aadhaar": f"https://millionmack.com/adhar.php?term={query}",
                "vehicle": f"https://api-vehicle-osint.vercel.app/?rc={query}",
                "ration": f"https://appi.ytcampss.store/Osint/ration.php?id={query}"
            }[typ])

            data = {}
            if typ == "vehicle":
                d = json.loads(raw)
                org = utils.organize_address(d.get("address"))
                data = {
                    "RC_NUMBER": d.get("rc_number", "N/A"),
                    "OWNER_NAME": d.get("owner_name", "N/A"),
                    "FATHER_NAME": d.get("father_name") or "N/A",
                    "MODEL_NAME": d.get("model_name", "N/A"),
                    "VEHICLE_CLASS": d.get("vehicle_class", "N/A"),
                    "FUEL_TYPE": d.get("fuel_type", "N/A"),
                    "REG_DATE": d.get("registration_date", "N/A"),
                    "ADDRESS": org["full"],
                    "CITY": org["city"],
                    "STATE": org["state"],
                    "PIN": org["pin"]
                }
            elif typ == "phone":
                d = json.loads(raw)
                res = d.get("results", [])
                addr = next((r.split(": ")[1].replace("!", ", ") for r in res if "🏘️" in r), "")
                org = utils.organize_address(addr)
                data = {
                    "NUMBER": query,
                    "NAME": next((r.split(": ")[1] for r in res if "👤Full Name" in r), "N/A"),
                    "FATHER": next((r.split(": ")[1] for r in res if "👨" in r), "N/A"),
                    "AADHAR": next((r.split(": ")[1] for r in res if "🃏" in r), "N/A"),
                    "ADDRESS": org["full"],
                    "CITY": org["city"],
                    "STATE": org["state"],
                    "PIN": org["pin"]
                }
            elif typ == "aadhaar":
                rows = json.loads(raw)
                e = rows[0] if rows else {}
                addr = e.get("address", "").replace("!", ", ").strip(", ")
                org = utils.organize_address(addr)
                data = {
                    "UID": query,
                    "NAME": e.get("name", "N/A"),
                    "FATHER": e.get("father_name", "N/A"),
                    "PHONE": e.get("mobile", "N/A"),
                    "CIRCLE": e.get("circle", "N/A"),
                    "ADDRESS": org["full"],
                    "CITY": org["city"],
                    "STATE": org["state"],
                    "PIN": org["pin"]
                }
            elif typ == "ration":
                d = json.loads(raw)["pd"]
                addr = d.get("address", "")
                org = utils.organize_address(addr)
                members = "".join(
                    [f"<li>{m['memberName']} ({m['releationship_name']})</li>" for m in d.get("memberDetailsList", [])]
                )
                data = {
                    "RATION_NO": query,
                    "STATE": d.get("homeStateName", "N/A"),
                    "DISTRICT": d.get("homeDistName", "N/A"),
                    "SCHEME": d.get("schemeName", "N/A"),
                    "ADDRESS": org["full"],
                    "CITY": org["city"],
                    "STATE2": org["state"],
                    "PIN": org["pin"],
                    "MEMBERS": f"<ul>{members}</ul>" if members else "N/A"
                }

            for k, v in data.items():
                html = html.replace("{{" + k + "}}", str(v))

        except Exception as e:
            html = html.replace("{{ERROR}}", str(e))

        url = utils.update_gist(f"{typ.upper()} Report – {query}", html)
        if not url:
            bot.send_message(uid, "⚠️ Failed to create report.")
            return

        db.add_credits(uid, -1)
        tot = db.get_credits(uid)
        bot.send_message(
            uid,
            f"✅ Report ready! [🔗 View Report]({url})\n"
            f"💰 Remaining credits: `{tot}`\n"
            "— 𝑩𝒚 𝑮𝒉𝒐𝒔𝒕 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓𝒔",
            parse_mode="Markdown"
        )