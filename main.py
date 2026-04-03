import vk_api, keyboards, database, re, time
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN, ADMIN_ID
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

database.init_db(ADMIN_ID)
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(uid, text, kb=None):
    try: vk.messages.send(user_id=uid, message=text, random_id=get_random_id(), keyboard=kb)
    except Exception as e: print(f"Ошибка связи: {e}")

def get_name(uid):
    try:
        u = vk.users.get(user_ids=uid)[0]
        return f"{u['first_name']} {u['last_name']}"
    except: return "Клиент"

def check_reminders():
    rem = (datetime.now() + timedelta(hours=2)).strftime("%d.%m в %H:%M")
    import sqlite3
    with sqlite3.connect(database.DATABASE) as conn:
        users = conn.execute("SELECT user_id, date_time FROM appointments WHERE date_time = ? AND reminded = 0", (rem,)).fetchall()
        for u_id, dt in users:
            send_msg(u_id, f"🔔 Напоминание! Вы записаны на прием через 2 часа ({dt}).")
            conn.execute("UPDATE appointments SET reminded = 1 WHERE user_id = ? AND date_time = ?", (u_id, dt))

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

print("🚀 Оптика Экспресс v2.0 запущена!")

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                uid, msg = event.user_id, event.text.strip()
                msg_l, is_adm = msg.lower(), database.is_admin(uid)
                full_name = get_name(uid)
                database.add_user(uid, full_name)

                if msg_l in ["начать", "привет", "меню", "назад", "в главное меню"]:
                    send_msg(uid, f"Здравствуйте, {full_name}!", keyboards.main_menu(is_adm))

                elif msg_l == "личный кабинет":
                    data = database.get_user_data(uid)
                    phone = data[1] if data[1] else "не привязан"
                    send_msg(uid, f"👤 Профиль: {data[0]}\n📞 Тел: {phone}\n\nЧтобы привязать телефон, напишите:\nМой телефон 8XXXXXXXXXX")

                elif msg_l == "о салоне":
                    send_msg(uid, "👓 Оптика Экспресс\n📍 Измайловский пр., 7\n⏰ 10:00-20:00\n✅ Проверка зрения\n✅ Очки за час")

                elif msg_l == "мои заказы":
                    orders = database.get_user_orders(uid)
                    text = "📦 Ваши заказы:\n" + "\n".join([f"№{o}: {s}" for o, s in orders]) if orders else "Заказов не найдено."
                    send_msg(uid, text)

                elif msg_l.startswith("мой телефон"):
                    ph = re.sub(r"\D", "", msg)
                    if len(ph) == 11:
                        database.update_user_phone(uid, ph)
                        send_msg(uid, f"✅ Телефон {ph} привязан!")
                    else: send_msg(uid, "❌ Введите 11 цифр.")

                elif msg_l == "записаться на прием" or msg_l == "⬅️ предыдущие даты":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(0))
                elif msg_l == "следующие даты ➡️":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(1))

                elif msg_l.startswith("дата: "):
                    d = msg.replace("Дата: ", "").replace("дата: ", "")
                    database.set_user_last_date(uid, d)
                    send_msg(uid, f"Время на {d}:", keyboards.time_slots(database.get_booked_slots(d)))

                elif re.match(r'^\d{2}:\d{2}$', msg):
                    d = database.get_user_last_date(uid)
                    if d and database.create_appointment(uid, f"{d} в {msg}"):
                        send_msg(uid, f"✅ Записано на {d} в {msg}!")
                        send_msg(ADMIN_ID, f"🔔 Запись: {d} в {msg} ({full_name})")
                    else: send_msg(uid, "❌ Это время уже занято.")

                elif is_adm and msg_l.startswith("заказ "):
                    p = msg.split()
                    if len(p) >= 3:
                        oid, status = p[1], p[2]
                        phone = p[3] if len(p) > 3 else None
                        target = database.update_order(oid, status, phone)
                        send_msg(uid, f"✅ Заказ {oid} обновлен.")
                        if "готов" in status.lower() and target:
                            send_msg(target, f"👓 {get_name(target)}, ваш заказ №{oid} готов!")

                elif msg.isdigit():
                    st = database.get_order_status(msg)
                    send_msg(uid, f"Статус заказа №{msg}: {st}" if st else "Заказ не найден.")

                else:
                    send_msg(uid, "Извините, я не понял запрос. Воспользуйтесь меню:", keyboards.main_menu(is_adm))

    except Exception as e:
        print(f"⚠️ Сбой: {e}. Перезапуск...")
        time.sleep(5)
