import sqlite3

DATABASE = 'optica.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, phone TEXT)')
    # Таблица записей
    cursor.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date_time TEXT UNIQUE)')
    # Таблица заказов
    cursor.execute('CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, status TEXT)')
    conn.commit()
    conn.close()

def add_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

def create_appointment(user_id, date_time):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("INSERT INTO appointments (user_id, date_time) VALUES (?, ?)", (user_id, date_time))
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
