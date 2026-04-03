import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN, ADMIN_ID
import keyboards, database
import re

database.init_db()
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(user_id, text, kb=None):
    vk.messages.send(user_id=user_id, message=text, random_id=get_random_id(), keyboard=kb)

print("Бот Оптика Экспресс запущен!")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id, msg = event.user_id, event.text.strip()
        msg_l = msg.lower()
        database.add_user(user_id)

        # 1. Навигация
        if msg_l in ["начать", "привет", "меню", "назад"]:
            send_msg(user_id, "Выберите действие в меню:", keyboards.main_menu())

        elif msg_l == "о салоне":
            info = "👓 Оптика Экспресс\n📍 Измайловский пр., д. 7\n⏰ 10:00 - 20:00"
            send_msg(user_id, info, keyboards.main_menu())

        # 2. Логика записи
        elif msg_l == "записаться на прием":
            send_msg(user_id, "На какой день вы хотите записаться?", keyboards.date_selection())

        elif msg_l.startswith("дата: "):
            date_val = msg.split(": ")[1]
            database.set_user_last_date(user_id, date_val) # Запоминаем дату в БД
            send_msg(user_id, f"Выберите время на {date_val}:", keyboards.time_slots())

        # Проверка: если ввели время (формат ЧЧ:ММ)
        elif re.match(r'^\d{2}:\d{2}$', msg):
            saved_date = database.get_user_last_date(user_id)
            if not saved_date:
                send_msg(user_id, "Сначала выберите дату!", keyboards.date_selection())
                continue
            
            full_date_time = f"{saved_date} в {msg}"
            if database.create_appointment(user_id, full_date_time):
                send_msg(user_id, f"✅ Записано: {full_date_time}!\nИзмайловский пр., д. 7", keyboards.main_menu())
                if ADMIN_ID:
                    send_msg(ADMIN_ID, f"🔔 Запись: ://vk.com{user_id} на {full_date_time}")
            else:
                send_msg(user_id, "❌ Это время уже занято.", keyboards.time_slots())

        # 3. Заказы
        elif msg_l == "статус заказа":
            send_msg(user_id, "Введите номер вашего заказа:")

        elif msg_l.startswith("заказ ") and user_id == ADMIN_ID:
            try:
                p = msg.split()
                database.update_order_status(p[1], " ".join(p[2:]))
                send_msg(ADMIN_ID, f"✅ Статус заказа №{p[1]} обновлен.")
            except: send_msg(ADMIN_ID, "Ошибка! Формат: заказ 1234 готово")

        elif msg.isdigit():
            status = database.get_order_status(msg)
            text = f"📦 Заказ №{msg}\nСтатус: {status}" if status else f"🔍 Заказ №{msg} не найден."
            send_msg(user_id, text, keyboards.main_menu())
        
        else:
            send_msg(user_id, "Используйте меню.", keyboards.main_menu())
