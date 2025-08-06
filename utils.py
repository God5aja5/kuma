import requests, json, re, os, uuid
from config import GITHUB_TOKEN, GITHUB_USER

# ---------- fetch ----------
def fetch(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200 and r.text.strip() and "error" not in r.text.lower():
                return r.text
        except: pass
    return None

# ---------- Gist ----------
def gist_id():
    gid_file = "gist.id"
    if os.path.exists(gid_file):
        with open(gid_file) as f:
            return f.read().strip()

    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "description": "OSINT Bot Reports – permanent",
        "public": True,
        "files": {"README.md": {"content": "OSINT Bot live reports"}}
    }
    r = requests.post("https://api.github.com/gists", headers=headers, json=payload)
    if r.status_code != 201:
        return None
    gid = r.json()["id"]
    with open(gid_file, "w") as f:
        f.write(gid)
    return gid

def update_gist(title: str, html: str) -> str:
    gid = gist_id()
    if not gid:
        return None
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {"files": {title.replace(" ", "_") + ".html": {"content": html}}}
    r = requests.patch(f"https://api.github.com/gists/{gid}", headers=headers, json=payload)
    if r.status_code == 200:
        return f"https://gistcdn.githack.com/{GITHUB_USER}/{gid}/raw/{title.replace(' ','_')}.html"
    return None

# ---------- address helper ----------
def organize_address(raw):
    if not raw: return {"city": "N/A", "state": "N/A", "pin": "N/A", "full": "N/A"}
    addr = raw.strip()
    pin = re.search(r'\b\d{6}\b', addr) or re.search(r'\b\d{5}\b', addr)
    pin = pin.group() if pin else "N/A"
    parts = list(filter(None, map(str.strip, addr.split(','))))
    city = parts[-2] if len(parts) >= 2 else "N/A"
    state = parts[-1] if parts else "N/A"
    return {"city": city, "state": state, "pin": pin, "full": addr}

# ---------- formatters ----------

def fmt_phone(raw1, num):
    try:
        d1 = json.loads(raw1)
        res = d1.get("results", [])
        name = next((r.split(": ")[1] for r in res if "👤Full Name" in r), "N/A")
        fath = next((r.split(": ")[1] for r in res if "👨" in r), "N/A")
        aad = next((r.split(": ")[1] for r in res if "🃏" in r), "N/A")
        phones = [r.split(": ")[1] for r in res if r.startswith("📞")]
        addr = [r.split(": ")[1].replace("!", ", ") for r in res if r.startswith("🏘️")]
        reg = next((r.split(": ")[1] for r in res if "🗺️" in r), "N/A")
        org = organize_address(addr[0]) if addr else {"city": "N/A", "state": "N/A", "pin": "N/A", "full": "N/A"}
        txt = (
            "╔═══════════════════════════════ **PHONE** ═══════════════════════════════╗\n"
            f"║ 📱 **Number** : `{num}`\n"
            f"║ 👤 **Name**   : `{name}`\n"
            f"║ 👨 **Father** : `{fath}`\n"
            f"║ 🆔 **Aadhar** : `{aad}`\n"
            f"║ 🌍 **Region** : `{reg}`\n"
            "╠══════════════════════════ **Organized Address** ═══════════════════════════╣\n"
            f"║ 🏙️ **City**   : `{org['city']}`\n"
            f"║ 🏛️ **State**  : `{org['state']}`\n"
            f"║ 📍 **Pin**    : `{org['pin']}`\n"
            f"║ 📜 **Full**   : `{org['full']}`\n"
            "╚═════════════════════════════════════════════════════════════════════════════╝\n"
            "— 𝑩𝒚 𝑮𝒉𝒐𝒔𝒕 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓𝒔"
        )
        if phones:
            txt = txt.replace("╚════════════════", "╠══════════════") + \
                  "\n📞 **Phones:**\n" + "\n".join([f"`{p}`" for p in phones]) + \
                  "\n╚═════════════════════════════════════════════════════════════════════════════╝\n— 𝑩𝒚 𝑮𝒉𝒐𝒔𝒕 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓𝒔"
        return txt
    except:
        return "`NOT FOUND`"

def fmt_aadhar(raw, aad):
    try:
        rows = json.loads(raw)
        if not rows: return "`NOT FOUND`"
        blocks = []
        for e in rows:
            addr = e.get("address", "").replace("!", ", ").strip(", ")
            org = organize_address(addr)
            blocks.append(
                "╔═══════════════════════════════ **AADHAAR** ═══════════════════════════════╗\n"
                f"║ 🆔 **UID**      : `{e['id_number']}`\n"
                f"║ 📞 **Phone**    : `{e['mobile']}`\n"
                f"║ 👤 **Name**     : `{e['name']}`\n"
                f"║ 👨 **Father**   : `{e['father_name']}`\n"
                f"║ 📡 **Circle**   : `{e['circle']}`\n"
                "╠══════════════════════════ **Organized Address** ═══════════════════════════╣\n"
                f"║ 🏙️ **City**   : `{org['city']}`\n"
                f"║ 🏛️ **State**  : `{org['state']}`\n"
                f"║ 📍 **Pin**    : `{org['pin']}`\n"
                f"║ 📜 **Full**   : `{org['full']}`\n"
                "╚═════════════════════════════════════════════════════════════════════════════╝\n"
                "— 𝑩𝒚 𝑮𝒉𝒐𝒔𝒕 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓𝒔"
            )
        return "\n".join(blocks)
    except: return "`NOT FOUND`"

def fmt_vehicle(raw):
    try:
        d = json.loads(raw)
        org = organize_address(d.get("address"))
        return (
            "╔═══════════════════════════════ **VEHICLE** ═══════════════════════════════╗\n"
            f"║ 🆔 **RC No**        : `{d['rc_number']}`\n"
            f"║ 👤 **Owner**        : `{d['owner_name']}`\n"
            f"║ 👨 **Father**       : `{d.get('father_name') or 'N/A'}`\n"
            f"║ 🔢 **Owner Serial** : `{d['owner_serial_no']}`\n"
            f"║ 🚙 **Model**        : `{d['model_name']}`\n"
            f"║ 🏭 **Maker Model**  : `{d['maker_model']}`\n"
            f"║ 🚗 **Class**        : `{d['vehicle_class']}`\n"
            f"║ ⛽ **Fuel**          : `{d['fuel_type']}`\n"
            f"║ 🌍 **Norms**        : `{d['fuel_norms']}`\n"
            f"║ 📅 **Reg Date**     : `{d['registration_date']}`\n"
            f"║ 🏢 **Insurance**    : `{d['insurance_company'].strip()}`\n"
            f"║ 📄 **Ins No**       : `{d.get('insurance_no') or 'N/A'}`\n"
            f"║ ⏳ **Ins Exp**      : `{d['insurance_expiry']}`\n"
            f"║ ✅ **Fitness Upto** : `{d['fitness_upto']}`\n"
            f"║ 💰 **Tax Upto**     : `{d.get('tax_upto') or 'N/A'}`\n"
            f"║ 🧪 **PUC No**       : `{d.get('puc_no') or 'N/A'}`\n"
            f"║ 🧪 **PUC Upto**     : `{d.get('puc_upto') or 'N/A'}`\n"
            f"║ 🏦 **Financier**    : `{d.get('financier_name') or 'N/A'}`\n"
            f"║ 🏢 **RTO**          : `{d['rto']}`\n"
            f"║ 📞 **Phone**        : `{d['phone']}`\n"
            f"║ 👑 **Owner Note**   : `{d['owner']}`\n"
            "╠══════════════════════════ **Organized Address** ═══════════════════════════╣\n"
            f"║ 🏙️ **City**   : `{org['city']}`\n"
            f"║ 🏛️ **State**  : `{org['state']}`\n"
            f"║ 📍 **Pin**    : `{org['pin']}`\n"
            f"║ 📜 **Full**   : `{org['full']}`\n"
            "╚═════════════════════════════════════════════════════════════════════════════╝\n"
            "— 𝑩𝒚 𝑮𝒉𝒐𝒔𝒕 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓𝒔"
        )
    except: return "`Vehicle unavailable`"

def fmt_ration(raw):
    try:
        d = json.loads(raw)["pd"]
        addr = d.get("address", "")
        org = organize_address(addr)
        members = "\n".join([f"• 👤 `{m['memberName']} ({m['releationship_name']})`" for m in d.get("memberDetailsList", [])])
        return (
            "╔═══════════════════════════════ **RATION CARD** ═══════════════════════════════╗\n"
            f"║ 🆔 **RC No**      : `{d['rcId']}`\n"
            f"║ 🏛️ **State**      : `{d['homeStateName']}`\n"
            f"║ 🏘️ **District**   : `{d['homeDistName']}`\n"
            f"║ 📋 **Scheme**     : `{d['schemeName']}`\n"
            f"║ 👥 **Members**    :\n{members}\n"
            "╠══════════════════════════ **Organized Address** ═══════════════════════════╣\n"
            f"║ 🏙️ **City**       : `{org['city']}`\n"
            f"║ 🏛️ **State**      : `{org['state']}`\n"
            f"║ 📍 **Pin**        : `{org['pin']}`\n"
            f"║ 📜 **Full**       : `{org['full']}`\n"
            "╚═══════════════════════════════════════════════════════════════════════════════╝\n"
            "— 𝑩𝒚 𝑮𝒉𝒐𝒔𝒕 𝑫𝒆𝒗𝒆𝒍𝒐𝒑𝒆𝒓𝒔"
        )
    except: return "`NOT FOUND`"
