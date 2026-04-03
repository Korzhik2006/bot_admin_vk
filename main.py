import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import TOKEN, ADMIN_ID
import keyboards
import database

# Стартуем
database.init_db()
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(user_id, text, kb=None):
    vk.messages.send(user_id=user_id, message=text, random_id=0, keyboard=kb)

print("Бот Оптика Экспресс запущен...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        msg = event.text
        user_id = event.user_id
        database.add_user(user_id)

        if msg.lower() in ["привет", "начать", "меню", "назад"]:
            send_msg(user_id, "Оптика Экспресс приветствует вас! Выберите действие:", keyboards.main_menu())

        elif msg == "О салоне":
            info = ("👓 Оптика Экспресс\n"
                    "📍 Адрес: Санкт-Петербург, Измайловский пр., д. 7\n"
                    "⏰ Время работы: 10:00 - 20:00\n"
                    "✅ Проверка зрения и изготовление очков любой сложности.")
            send_msg(user_id, info)

        elif msg == "Записаться на прием":
            send_msg(user_id, "Выберите удобное время на сегодня:", keyboards.time_slots())

        elif "Запись на" in msg:
            time_val = msg.replace("Запись на ", "")
            if database.create_appointment(user_id, time_val):
                send_msg(user_id, f"✅ Вы успешно записаны на {time_val}!\nЖдем вас по адресу: Измайловский пр., д. 7")
                # Уведомление админу
                send_msg(ADMIN_ID, f"🔔 Новая запись! User ID: {user_id} на {time_val}")
            else:
                send_msg(user_id, "❌ Извините, это время уже занято. Выберите другое.", keyboards.time_slots())

        elif msg == "Статус заказа":
            send_msg(user_id, "Введите номер вашего заказа (например: 1234):")
