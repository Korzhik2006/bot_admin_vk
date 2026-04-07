import sqlite3, re # Добавил re для нормализации телефона
from datetime import datetime, timedelta # Хотя timedelta здесь не используется, но для полноты

DATABASE = 'optica.db'

def init_db(main_admin_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, last_date TEXT, full_name TEXT, phone TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, date_time TEXT UNIQUE, reminded INTEGER DEFAULT 0)')
        cursor.execute('CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, status TEXT, phone_link TEXT, user_id_link INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)')
        # Авто-миграции
        try: cursor.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
        except: pass
        try: cursor.execute('ALTER TABLE orders ADD COLUMN user_id_link INTEGER')
        except: pass
        cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (main_admin_id,))
        conn.commit()

def add_user(user_id, name):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("""
            INSERT INTO users (user_id, full_name) VALUES(?, ?)
            ON CONFLICT(user_id) DO UPDATE SET full_name=excluded.full_name
            WHERE full_name IS NULL OR full_name = 'Клиент'
        """, (user_id, name))
        conn.commit()

def update_user_phone(uid, p):
    with sqlite3.connect(DATABASE) as conn: 
        conn.execute("UPDATE users SET phone = ? WHERE user_id = ?", (p, uid))

def get_user_data(uid):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT full_name, phone FROM users WHERE user_id = ?", (uid,)).fetchone()
        return res if res else (None, None)

def is_admin(user_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)).fetchone()
        return res is not None

def get_booked_slots(date_str):
    with sqlite3.connect(DATABASE) as conn:
        rows = conn.execute("SELECT date_time FROM appointments WHERE date_time LIKE ?", (f"{date_str} в %",)).fetchall()
        return [row[0].split(" в ")[1] for row in rows]

def create_appointment(uid, dt):
    try:
        with sqlite3.connect(DATABASE) as conn:
            conn.execute("INSERT INTO appointments (user_id, date_time) VALUES (?, ?)", (uid, dt))
            conn.execute("UPDATE users SET last_date = NULL WHERE user_id = ?", (uid,))
            return True
    except sqlite3.IntegrityError:
        return False
    except:
        return False

def get_pending_reminders(time_limit_str):
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute("""
            SELECT user_id, date_time
            FROM appointments
            WHERE reminded = 0 AND date_time = ?
        """, (time_limit_str,)).fetchall()

def mark_reminded(uid, dt):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("UPDATE appointments SET reminded = 1 WHERE user_id = ? AND date_time = ?", (uid, dt))

def update_order(order_id, status, phone=None):
    with sqlite3.connect(DATABASE) as conn:
        target_uid = None
        normalized_phone = None

        if phone:
            normalized_phone = re.sub(r"\D", "", phone) # Нормализуем входящий телефон
            if len(normalized_phone) == 11 and (normalized_phone.startswith('7') or normalized_phone.startswith('8')):
                res = conn.execute("SELECT user_id FROM users WHERE phone = ?", (normalized_phone,)).fetchone()
                if res:
                    target_uid = res[0] # Если нашли пользователя по телефону, привязываем
            
        # Вставляем/обновляем заказ. phone_link будет либо нормализованным телефоном, либо None.
        # user_id_link будет либо найденным UID, либо None.
        conn.execute("INSERT OR REPLACE INTO orders (order_id, status, phone_link, user_id_link) VALUES (?, ?, ?, ?)", 
                     (order_id, status, normalized_phone, target_uid))
        return target_uid # Возвращаем найденный UID для уведомлений

def get_user_orders(user_id):
    with sqlite3.connect(DATABASE) as conn:
        # Получаем номер телефона пользователя, если он его привязал
        user_phone_res = conn.execute("SELECT phone FROM users WHERE user_id = ?", (user_id,)).fetchone()
        user_phone = user_phone_res[0] if user_phone_res else None

        # Строим запрос для поиска заказов
        query_parts = ["user_id_link = ?"] # Всегда ищем по прямой ссылке на user_id
        query_params = [user_id]

        if user_phone:
            # Если у пользователя есть привязанный телефон, ищем также по phone_link
            query_parts.append("phone_link = ?")
            query_params.append(user_phone)
        
        # Объединяем части запроса через OR
        final_query = "SELECT order_id, status FROM orders WHERE " + " OR ".join(query_parts)
        
        return conn.execute(final_query, tuple(query_params)).fetchall()

def get_order_status(order_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return res[0] if res else None

def get_all_appointments():
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute("SELECT a.date_time, u.full_name FROM appointments a JOIN users u ON a.user_id = u.user_id ORDER BY a.date_time").fetchall()

def get_all_orders():
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT o.order_id, o.status, u.full_name FROM orders o LEFT JOIN users u ON o.user_id_link = u.user_id").fetchall()
        return [(str(o), str(s) if s else "Без статуса", str(n) if n else "Неизвестен") for o, s, n in res]

# --- НОВЫЕ ФУНКЦИИ ДЛЯ АДМИНКИ ---
def get_all_clients():
    with sqlite3.connect(DATABASE) as conn:
        return conn.execute("""
            SELECT u.user_id, u.full_name, u.phone, MAX(a.date_time)
            FROM users u
            LEFT JOIN appointments a ON u.user_id = a.user_id
            GROUP BY u.user_id ORDER BY u.full_name
        """).fetchall()

def get_client_full_card(identifier):
    with sqlite3.connect(DATABASE) as conn:
        user = conn.execute("SELECT user_id, full_name, phone FROM users WHERE user_id = ? OR phone = ?", 
                            (identifier, identifier)).fetchone()
        if not user: return None
        uid = user[0]
        apps = conn.execute("SELECT date_time FROM appointments WHERE user_id = ? ORDER BY id DESC LIMIT 5", (uid,)).fetchall()
        orders = conn.execute("SELECT order_id, status FROM orders WHERE user_id_link = ?", (uid,)).fetchall()
        return {"profile": user, "apps": apps, "orders": orders}

def set_user_last_date(user_id, d):
    with sqlite3.connect(DATABASE) as conn: 
        conn.execute("UPDATE users SET last_date = ? WHERE user_id = ?", (d, user_id))

def get_user_last_date(user_id):
    with sqlite3.connect(DATABASE) as conn:
        res = conn.execute("SELECT last_date FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return res[0] if res else None

