import vk_api, keyboards, database, re
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN, ADMIN_ID
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3

database.init_db()
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(user_id, text, kb=None):
    vk.messages.send(user_id=user_id, message=text, random_id=get_random_id(), keyboard=kb)

# --- ФОНОВАЯ ЗАДАЧА: НАПОМИНАНИЯ ---
def check_reminders():
    now = datetime.now()
    reminder_time = now + timedelta(hours=2)
    time_str = reminder_time.strftime("%d.%m в %H:%M")
    
    with sqlite3.connect(database.DATABASE) as conn:
        # Ищем записи на это время, которым еще не напоминали
        users_to_remind = conn.execute(
            "SELECT user_id, date_time FROM appointments WHERE date_time = ? AND reminded = 0", 
            (time_str,)
        ).fetchall()
        
        for u_id, dt in users_to_remind:
            try:
                send_msg(u_id, f"🔔 Напоминание! Вы записаны в Оптику Экспресс через 2 часа ({dt}). Ждем вас!")
                conn.execute("UPDATE appointments SET reminded = 1 WHERE user_id = ? AND date_time = ?", (u_id, dt))
            except: pass

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

print("Бот и планировщик запущены!")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id, msg = event.user_id, event.text.strip()
        msg_l = msg.lower()
        is_admin = (user_id == ADMIN_ID)
        database.add_user(user_id)

        if msg_l in ["начать", "привет", "меню", "назад", "в главное меню"]:
            send_msg(user_id, "Главное меню:", keyboards.main_menu(is_admin))

        elif msg_l == "о салоне":
            send_msg(user_id, "👓 Оптика Экспресс\n📍 Измайловский пр., д. 7\n⏰ 10:00 - 20:00", keyboards.main_menu(is_admin))

        # АДМИН-ПАНЕЛЬ
        elif msg_l == "админ-панель" and is_admin:
            send_msg(user_id, "Добро пожаловать, Шеф. Что проверить?", keyboards.admin_menu())

        elif msg_l == "список записей" and is_admin:
            apps = database.get_all_appointments()
            text = "📅 Предстоящие записи:\n" + "\n".join([f"• {a[0]} (id{a[1]})" for a in apps]) if apps else "Записей нет."
            send_msg(user_id, text, keyboards.admin_menu())

        elif msg_l == "все заказы" and is_admin:
            orders = database.get_all_orders()
            text = "📦 Текущие заказы:\n" + "\n".join([f"• №{o[0]}: {o[1]}" for o in orders]) if orders else "Заказов нет."
            send_msg(user_id, text, keyboards.admin_menu())

        # ЗАПИСЬ
        elif msg_l == "записаться на прием":
            send_msg(user_id, "Выберите дату:", keyboards.date_selection())

        elif msg_l.startswith("дата: "):
            date_val = msg.split(": ")[1]
            database.set_user_last_date(user_id, date_val)
            booked = database.get_booked_slots(date_val)
            send_msg(user_id, f"Время на {date_val}:", keyboards.time_slots(booked))

        elif re.match(r'^\d{2}:\d{2}$', msg):
            saved_date = database.get_user_last_date(user_id)
            if saved_date:
                full_dt = f"{saved_date} в {msg}"
                if database.create_appointment(user_id, full_dt):
                    send_msg(user_id, f"✅ Записано: {full_dt}!", keyboards.main_menu(is_admin))
                    send_msg(ADMIN_ID, f"🔔 Новая запись: {full_dt} (id{user_id})")
                else: send_msg(user_id, "❌ Занято!", keyboards.main_menu(is_admin))

        # ЗАКАЗЫ (СТАТУС)
        elif msg_l == "статус заказа":
            send_msg(user_id, "Введите номер заказа:")

        elif msg_l.startswith("заказ ") and is_admin:
            try:
                p = msg.split(); database.update_order_status(p[1], " ".join(p[2:]))
                send_msg(ADMIN_ID, f"✅ Статус заказа №{p[1]} обновлен.")
            except: send_msg(ADMIN_ID, "Ошибка формата.")

        elif msg.isdigit():
            st = database.get_order_status(msg)
            send_msg(user_id, f"📦 Заказ №{msg}\nСтатус: {st}" if st else "🔍 Не найден.", keyboards.main_menu(is_admin))
