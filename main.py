import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN, ADMIN_ID
import keyboards, database

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

        # 2. Запись
        elif msg_l == "записаться на прием":
            send_msg(user_id, "Выберите время на сегодня:", keyboards.time_slots())

        elif "запись на" in msg_l:
            time_val = msg_l.replace("запись на ", "")
            if database.create_appointment(user_id, time_val):
                send_msg(user_id, f"✅ Вы записаны на {time_val}!", keyboards.main_menu())
                if ADMIN_ID:
                    send_msg(ADMIN_ID, f"🔔 Новая запись: ://vk.com{user_id} на {time_val}")
            else:
                send_msg(user_id, "❌ Это время уже занято.", keyboards.time_slots())

        # 3. Статусы заказов
        elif msg_l == "статус заказа":
            send_msg(user_id, "Введите номер вашего заказа (цифрами):")

        # Админ-команда: "заказ 1234 готов"
        elif msg_l.startswith("заказ ") and user_id == ADMIN_ID:
            try:
                parts = msg.split() # ['заказ', '1234', 'готов']
                database.update_order_status(parts[1], " ".join(parts[2:]))
                send_msg(ADMIN_ID, f"✅ Статус заказа {parts[1]} обновлен.")
            except:
                send_msg(ADMIN_ID, "Ошибка! Формат: заказ [номер] [статус]")

        # Поиск заказа по цифрам
        elif msg.isdigit():
            status = database.get_order_status(msg)
            text = f"📦 Заказ №{msg}\nСтатус: {status}" if status else f"🔍 Заказ №{msg} не найден."
            send_msg(user_id, text, keyboards.main_menu())

        else:
            send_msg(user_id, "Используйте кнопки меню.", keyboards.main_menu())
