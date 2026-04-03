import sqlite3

DATABASE = 'optica.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, last_date TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date_time TEXT UNIQUE)')
        cursor.execute('CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, status TEXT)')
        conn.commit()

def add_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

def set_user_last_date(user_id, date_str):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("UPDATE users SET last_date = ? WHERE user_id = ?", (date_str, user_id))

def get_user_last_date(user_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT last_date FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res[0] if res else None

def create_appointment(user_id, date_time_str):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("INSERT INTO appointments (user_id, date_time) VALUES (?, ?)", (user_id, date_time_str))
            return True
    except sqlite3.IntegrityError:
        return False

def update_order_status(order_id, status):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT OR REPLACE INTO orders (order_id, status) VALUES (?, ?)", (order_id, status))

def get_order_status(order_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return res[0] if res else None
