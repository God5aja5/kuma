import sqlite3, threading, uuid, json
from config import DB_FILE

lock = threading.Lock()

def init():
    with lock, sqlite3.connect(DB_FILE) as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS credits(
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 5
        );
        CREATE TABLE IF NOT EXISTS keys(
            key TEXT PRIMARY KEY,
            credits INTEGER,
            max_uses INTEGER,
            used INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            query TEXT,
            type TEXT,
            result TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

# ---------- users ----------
def user_add(uid, un, fn):
    with lock, sqlite3.connect(DB_FILE) as c:
        c.execute("INSERT OR IGNORE INTO users(user_id,username,full_name) VALUES(?,?,?)",
                  (uid, un, fn))
        c.execute("INSERT OR IGNORE INTO credits(user_id) VALUES(?)", (uid,))

def get_user(uid):
    with lock, sqlite3.connect(DB_FILE) as c:
        return c.execute("SELECT * FROM users WHERE user_id=?", (uid,)).fetchone()

def all_users():
    with lock, sqlite3.connect(DB_FILE) as c:
        return [r[0] for r in c.execute("SELECT user_id FROM users").fetchall()]

# ---------- credits ----------
def get_credits(uid):
    with lock, sqlite3.connect(DB_FILE) as c:
        return c.execute("SELECT balance FROM credits WHERE user_id=?", (uid,)).fetchone()[0]

def add_credits(uid, amt):
    with lock, sqlite3.connect(DB_FILE) as c:
        c.execute("UPDATE credits SET balance=balance+? WHERE user_id=?", (amt, uid))

# ---------- keys ----------
def gen_key(credits, max_uses=1):
    k = str(uuid.uuid4()).replace("-","").upper()[:12]
    with lock, sqlite3.connect(DB_FILE) as c:
        c.execute("INSERT INTO keys(key,credits,max_uses) VALUES(?,?,?)", (k, credits, max_uses))
    return k

def redeem_key(uid, key):
    with lock, sqlite3.connect(DB_FILE) as c:
        row = c.execute("SELECT credits,max_uses,used FROM keys WHERE key=?", (key,)).fetchone()
        if not row:               return "❌ Invalid key"
        credits, max_uses, used = row
        if used >= max_uses:      return "❌ Key already exhausted"
        c.execute("UPDATE keys SET used=used+1 WHERE key=?", (key,))
        c.execute("UPDATE credits SET balance=balance+? WHERE user_id=?", (credits, uid))
        return f"🎉 Key redeemed! +{credits} credits"

# ---------- history ----------
def log_search(uid, qry, typ, res):
    with lock, sqlite3.connect(DB_FILE) as c:
        c.execute("INSERT INTO history(user_id,query,type,result) VALUES(?,?,?,?)",
                  (uid, qry, typ, json.dumps(res, ensure_ascii=False)))

def get_history(uid):
    with lock, sqlite3.connect(DB_FILE) as c:
        return c.execute("SELECT query,type,ts FROM history WHERE user_id=? ORDER BY ts DESC",
                         (uid,)).fetchall()

def total_searches():
    with lock, sqlite3.connect(DB_FILE) as c:
        return c.execute("SELECT COUNT(*) FROM history").fetchone()[0]