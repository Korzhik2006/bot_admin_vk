import sqlite3

def init_db():
    conn = sqlite3.connect('optica.db')
    cursor = conn.cursor()
    # Таблица юзеров
    cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, phone TEXT)')
    # Таблица записей (с уникальным временем, чтобы нельзя было записать двоих на одно время)
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       user_id INTEGER, date_time TEXT UNIQUE)''')
    # Таблица заказов
    cursor.execute('CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, user_id INTEGER, status TEXT)')
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect('optica.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def create_appointment(user_id, date_time):
    conn = sqlite3.connect('optica.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO appointments (user_id, date_time) VALUES (?, ?)", (user_id, date_time))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Время уже занято
    finally:
        conn.close()
