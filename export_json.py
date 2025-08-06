import sqlite3, os, json, shutil, zipfile
from config import DB_FILE

def export_user_data():
    base_dir = "Database"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    users = cursor.execute("SELECT user_id, username, full_name FROM users").fetchall()
    for user_id, username, full_name in users:
        folder_name = f"{user_id}_{username or 'no_username'}"
        user_dir = os.path.join(base_dir, folder_name)
        os.makedirs(user_dir, exist_ok=True)
        total = cursor.execute("SELECT COUNT(*) FROM history WHERE user_id=?", (user_id,)).fetchone()[0]
        info = {
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "total_searches": total
        }
        with open(os.path.join(user_dir, "info.json"), "w", encoding="utf-8") as f:
            json.dump(info, f, indent=4, ensure_ascii=False)
        credits = cursor.execute("SELECT balance FROM credits WHERE user_id=?", (user_id,)).fetchone()
        with open(os.path.join(user_dir, "credits.json"), "w", encoding="utf-8") as f:
            json.dump({"credits": credits[0] if credits else 0}, f, indent=4)
        history = cursor.execute("SELECT query, type, ts FROM history WHERE user_id=? ORDER BY ts DESC", (user_id,)).fetchall()
        history_data = []
        for q, t, ts in history:
            history_data.append({
                "query": q,
                "type": t,
                "timestamp": ts
            })
        with open(os.path.join(user_dir, "history.json"), "w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=4, ensure_ascii=False)
    conn.close()
    zip_path = "Database.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(base_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, base_dir)
                zipf.write(file_path, arcname)
    return zip_path