import sqlite3

DATABASE = 'optica.db'

def init_db(main_admin_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, last_date TEXT, full_name TEXT, phone TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date_time TEXT UNIQUE, reminded INTEGER DEFAULT 0)')
        cursor.execute('CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, status TEXT, phone_link TEXT, user_id_link INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)')
        
        # Авто-миграция (добавление колонок без удаления базы)
        try: cursor.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
        except: pass
        try: cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
        except: pass
        try: cursor.execute('ALTER TABLE orders ADD COLUMN user_id_link INTEGER')
        except: pass
        
        cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (main_admin_id,))
        conn.commit()

def add_user(user_id, name):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id, full_name) VALUES (?, ?)", (user_id, name))

def update_user_phone(uid, p):
    with sqlite3.connect(DATABASE) as conn: 
        conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p, uid))

def get_user_data(uid):
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute("SELECT full_name, phone FROM users WHERE user_id = ?", (uid,)).fetchone()

def is_admin(user_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone()
        return res is not None

def add_admin(user_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))

def get_booked_slots(date_str):
    with sqlite3.connect(DATABASE) as conn:
        rows = conn.execute("SELECT date_time FROM appointments WHERE date_time LIKE ?", (f"{date_str} в %",)).fetchall()
        return [r[0].split(" в ")[1] for r in rows]

def create_appointment(uid, dt):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("INSERT INTO appointments (user_id, date_time) VALUES (?, ?)", (uid, dt))
            return True
    except: return False

def delete_appointment(dt):
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.execute("DELETE FROM appointments WHERE date_time = ?", (dt,))
        return cur.rowcount > 0

def update_order(order_id, status, phone=None):
    with sqlite3.connect(DATABASE) as conn:
        target_uid = None
        if phone:
            res = conn.execute("SELECT user_id FROM users WHERE phone = ?", (phone,)).fetchone()
            if res: target_uid = res[0]
        conn.execute("INSERT OR REPLACE INTO orders (order_id, status, phone_link, user_id_link) VALUES (?, ?, ?, ?)", 
                     (order_id, status, phone, target_uid))
        return target_uid

def get_user_orders(user_id):
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute("""
            SELECT order_id, status FROM orders 
            WHERE user_id_link = ? OR phone_link = (SELECT phone FROM users WHERE user_id = ?)
        """, (user_id, user_id)).fetchall()

def get_order_status(order_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return res[0] if res else None

def set_user_last_date(user_id, d):
    with sqlite3.connect(DATABASE) as conn: 
        conn.execute("UPDATE users SET last_date = ? WHERE user_id = ?", (d, user_id))

def get_user_last_date(user_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT last_date FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res[0] if res else None
