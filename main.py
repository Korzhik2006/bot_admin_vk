import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN, ADMIN_ID
import keyboards
import database

# Инициализация
database.init_db()
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(user_id, text, kb=None):
    params = {
        'user_id': user_id,
        'message': text,
        'random_id': get_random_id()
    }
    if kb:
        params['keyboard'] = kb
    vk.messages.send(**params)

print("Бот Оптика Экспресс запущен и готов к работе!")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        msg = event.text.strip()
        msg_l = msg.lower()

        # Регистрация в БД
        database.add_user(user_id)

        # Логика команд
        if msg_l in ["начать", "привет", "меню", "назад"]:
            send_msg(user_id, "Оптика Экспресс приветствует вас! Выберите нужное действие в меню:", keyboards.main_menu())

        elif msg_l == "о салоне":
            info = ("👓 Оптика Экспресс\n"
                    "📍 Адрес: Санкт-Петербург, Измайловский пр., д. 7\n"
                    "⏰ Время работы: Пн-Вс 10:00 - 20:00\n"
                    "🚇 Метро: Технологический институт\n\n"
                    "Мы предлагаем профессиональную проверку зрения и подбор очков.")
            send_msg(user_id, info, keyboards.main_menu())

        elif msg_l == "записаться на прием":
            send_msg(user_id, "Выберите свободное время для записи на сегодня:", keyboards.time_slots())

        elif "запись на" in msg_l:
            time_val = msg_l.replace("запись на ", "").strip()
            
            if database.create_appointment(user_id, time_val):
                # Подтверждение клиенту
                send_msg(user_id, f"✅ Вы записаны на {time_val}!\nАдрес: Измайловский пр., д. 7. Ждем вас!", keyboards.main_menu())
                # Уведомление админу
                try:
                    admin_text = f"🔔 Новая запись!\nПользователь: ://vk.com{user_id}\nВремя: {time_val}"
                    send_msg(ADMIN_ID, admin_text)
                except Exception as e:
                    print(f"Ошибка уведомления админа: {e}")
            else:
                send_msg(user_id, f"❌ Время {time_val} уже занято другими клиентами. Выберите другое.", keyboards.time_slots())

        elif msg_l == "статус заказа":
            send_msg(user_id, "Для проверки статуса введите номер вашего заказа (только цифры):")

        # Если пришло сообщение, не попавшее в фильтры (например, номер заказа)
        elif msg.isdigit():
            # Здесь будет поиск заказа в БД (добавим в следующем шаге)
            send_msg(user_id, f"Вы ввели номер заказа: {msg}. Поиск в базе пока настраивается...", keyboards.main_menu())

        else:
            send_msg(user_id, "Извините, я не понимаю эту команду. Пожалуйста, воспользуйтесь кнопками меню.", keyboards.main_menu())
