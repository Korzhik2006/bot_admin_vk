import os, time, re, sqlite3, vk_api
from datetime import datetime, timedelta
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from apscheduler.schedulers.background import BackgroundScheduler

import database, keyboards, setup_wizard

# Запуск мастера, если нет конфига
setup_wizard.run_wizard()

from config import TOKEN, ADMIN_ID, SALON_NAME

# Инициализация
database.init_db(ADMIN_ID)
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(uid, text, kb=None):
    params = {'user_id': uid, 'message': text, 'random_id': get_random_id()}
    if kb: params['keyboard'] = kb
    try: vk.messages.send(**params)
    except: pass

def get_name(uid):
    try:
        u = vk.users.get(user_ids=uid)[0]
        return f"{u['first_name']} {u['last_name']}"
    except: return "Клиент"

def check_reminders():
    # Напоминание за 2 часа
    rem = (datetime.now() + timedelta(hours=2)).strftime("%d.%m в %H:%M")
    with sqlite3.connect(database.DATABASE) as conn:
        users = conn.execute("SELECT user_id, date_time FROM appointments WHERE date_time = ? AND reminded = 0", (rem,)).fetchall()
        for u_id, dt in users:
            send_msg(u_id, f"🔔 Напоминание! Вы записаны в {SALON_NAME} через 2 часа ({dt}).")
            conn.execute("UPDATE appointments SET reminded = 1 WHERE user_id = ? AND date_time = ?", (u_id, dt))

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

print(f"🚀 Бот '{SALON_NAME}' запущен!")

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                uid, msg = event.user_id, event.text.strip()
                msg_l, is_adm = msg.lower(), database.is_admin(uid)
                full_name = get_name(uid)
                database.add_user(uid, full_name)

                # --- КЛИЕНТСКАЯ ЧАСТЬ ---
                if msg_l in ["начать", "привет", "меню", "назад", "в главное меню"]:
                    send_msg(uid, f"Здравствуйте, {full_name}! Вас приветствует {SALON_NAME}.", keyboards.main_menu(is_adm))
                
                elif msg_l == "админ-панель" and is_adm:
                    send_msg(uid, "Управление салоном:", keyboards.admin_menu())

                elif msg_l == "личный кабинет":
                    name_db, phone_db = database.get_user_data(uid)
                    d_phone = phone_db if phone_db else "не привязан"
                    send_msg(uid, f"👤 Профиль: {name_db}\n📞 Тел: {d_phone}\n\nДля привязки: Мой телефон 8XXXXXXXXXX")

                elif msg_l == "о салоне":
                    send_msg(uid, f"👓 {SALON_NAME}\n📍 Измайловский пр., 7\n⏰ 10:00-20:00")

                elif msg_l == "мои заказы":
                    orders = database.get_user_orders(uid)
                    text = "📦 Ваши заказы:\n" + "\n".join([f"№{o}: {s}" for o, s in orders]) if orders else "Заказов не найдено."
                    send_msg(uid, text)

                # --- ЛОГИКА ЗАПИСИ ---
                elif msg_l == "записаться на прием" or msg_l == "⬅️ предыдущие даты":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(0))
                elif msg_l == "следующие даты ➡️":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(1))

                elif msg_l.startswith("дата: "):
                    d = msg.replace("Дата: ", "").replace("дата: ", "")
                    database.set_user_last_date(uid, d)
                    send_msg(uid, f"Время на {d}:", keyboards.time_slots(database.get_booked_slots(d), d))

                elif re.match(r'^\d{2}:\d{2}$', msg):
                    d = database.get_user_last_date(uid)
                    if d:
                        if database.create_appointment(uid, f"{d} в {msg}"):
                            send_msg(uid, f"✅ Вы записаны на {d} в {msg}!")
                            send_msg(ADMIN_ID, f"🔔 Новая запись: {d} в {msg}\n👤 {full_name}")
                        else: send_msg(uid, "❌ Это время уже занято.")
                    else: send_msg(uid, "❌ Сначала выберите дату.")

                # --- АДМИН-ПАНЕЛЬ ---
                elif is_adm and msg_l == "список клиентов":
                    clients = database.get_all_clients()
                    res = "👥 Клиенты:\n" + "\n".join([f"• {n} | {p if p else 'нет тел.'} | ID: {i}" for i, n, p, lv in clients])
                    res += "\n\n🔍 Для деталей: Инфо [ID]"
                    send_msg(uid, res)

                elif is_adm and msg_l.startswith("инфо "):
                    target = msg.split()[-1]
                    data = database.get_client_full_card(target)
                    if data:
                        u = data['profile']
                        apps = "\n".join([f"📅 {a[0]}" for a in data['apps']]) or "Нет"
                        orders = "\n".join([f"📦 №{o[0]}: {o[1]}" for o in data['orders']]) or "Нет"
                        send_msg(uid, f"👤 {u[1]}\n📞 {u[2]}\n🆔 {u[0]}\n\nВизиты:\n{apps}\n\nЗаказы:\n{orders}")
                    else: send_msg(uid, "❌ Не найден.")

                elif is_adm and msg_l == "все заказы":
                    orders = database.get_all_orders()
                    res = "\n".join([f"📦 №{o} | {s} | {n}" for o, s, n in orders]) if orders else "Заказов нет."
                    send_msg(uid, f"📋 Список всех заказов:\n{res}")

                elif is_adm and msg_l == "список записей":
                    apps = database.get_all_appointments()
                    res = "\n".join([f"• {dt}: {name}" for dt, name in apps]) if apps else "Записей нет."
                    send_msg(uid, f"📅 Записи:\n{res}")

                elif is_adm and msg_l.startswith("заказ "):
                    p = msg.split()
                    if len(p) >= 3:
                        order_id, status = p[1], " ".join(p[2:])
                        target = database.update_order(order_id, status)
                        send_msg(uid, f"✅ Обновлено.")
                        if "готов" in status.lower() and target:
                            send_msg(target, f"👓 Заказ №{order_id} готов!")

                # --- ОБЩЕЕ ---
                elif msg_l.startswith("мой телефон"):
                    ph = re.sub(r"\D", "", msg)
                    if len(ph) == 11:
                        database.update_user_phone(uid, ph)
                        send_msg(uid, f"✅ Телефон {ph} привязан!")
                    else: send_msg(uid, "❌ Введите 11 цифр.")

                else:
                    send_msg(uid, "Воспользуйтесь меню:", keyboards.main_menu(is_adm))

    except Exception as e:
        print(f"⚠️ Сбой: {e}")
        time.sleep(5)