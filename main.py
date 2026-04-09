import os, time, re, sqlite3, vk_api
from dotenv import load_dotenv
from datetime import datetime, timedelta
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from apscheduler.schedulers.background import BackgroundScheduler

import database, keyboards

#load_dotenv()

# Вместо import config используем os.getenv
# Это позволит брать данные из Docker или системы
TOKEN = os.getenv('TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))
SALON_NAME = os.getenv('SALON_NAME', 'Мой Салон')

# Проверка, что важные данные на месте
if not TOKEN or not ADMIN_ID:
    print("Ошибка: VK_TOKEN или ADMIN_ID не установлены в переменных окружения!")
    exit(1)

# Инициализация
database.init_db(ADMIN_ID)
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def send_msg(uid, text, kb=None):
    params = {'user_id': uid, 'message': text, 'random_id': get_random_id()}
    if kb: params['keyboard'] = kb
    try: 
        vk.messages.send(**params)
    except Exception as e:
        print(f"Ошибка отправки сообщения пользователю {uid}: {e}")

def get_name(uid):
    try:
        u = vk.users.get(user_ids=uid)[0]
        return f"{u['first_name']} {u['last_name']}"
    except: return "Клиент"

def check_reminders():
    target_time = (datetime.now() + timedelta(hours=2)).strftime("%d.%m в %H:%M")
    pending = database.get_pending_reminders(target_time)
    for u_id, dt in pending:
        send_msg(u_id, f"🔔 Напоминание! Вы записаны в {SALON_NAME} на {dt} (через 2 часа).")
        database.mark_reminded(u_id, dt)

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, 'interval', minutes=1)
scheduler.start()

print(f"🚀 Бот '{SALON_NAME}' запущен!")

# --- ТЕКСТЫ ПОМОЩИ ---
CLIENT_HELP_TEXT = """
✨ **Разделы для клиентов:**

*   **Записаться на прием**: Выберите удобную дату и время для визита в салон.
*   **Мои заказы**: Проверьте статус изготовления ваших очков или линз.
*   **Личный кабинет**: Здесь вы можете привязать свой номер телефона. Для этого напишите: `Мой телефон 8XXXXXXXXXX` (например, `Мой телефон 89123456789`). Это позволит нам сообщать вам о готовности заказов.
*   **О салоне**: Адрес и часы работы нашего салона.
*   **Помощь**: Информация по использованию бота.

Если у вас остались вопросы, обратитесь к администратору!
"""

ADMIN_HELP_TEXT = """
⚙️ **Команды админ-панели:**

*   **Админ-панель**: Открывает главное меню администратора.
*   **Список записей**: Показывает все предстоящие записи клиентов.
*   **Все заказы**: Показывает все заказы в системе, их статусы и связанные имена клиентов.
*   **Список клиентов**: Показывает ID, имена и телефоны всех зарегистрированных клиентов.
*   **Инфо [ID/Телефон]**: Введите `Инфо 12345` (по ID клиента) или `Инфо 89123456789` (по номеру телефона) чтобы получить полную карточку клиента: последние визиты и заказы.
*   **Заказ [номер_заказа] [статус] [телефон_клиента (необязательно)]**: Обновите статус заказа. Пример: `Заказ 500 Готов к выдаче 89991234567`. Если телефон клиента привязан, бот отправит ему уведомление.
*   **В главное меню**: Возвращает в основное меню бота.
"""
# --- КОНЕЦ ТЕКСТОВ ПОМОЩИ ---


while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                uid, msg = event.user_id, event.text.strip()
                msg_l, is_adm = msg.lower(), database.is_admin(uid)

                # 1. СТАРТ И ГЛАВНОЕ МЕНЮ
                if msg_l in ["начать", "привет", "меню", "в главное меню"]:
                    full_name = get_name(uid)
                    database.add_user(uid, full_name)
                    send_msg(uid, f"Здравствуйте, {full_name}! Вас приветствует {SALON_NAME}.", keyboards.main_menu(is_adm))
                    continue
                
                # 2. КЛИЕНТСКИЕ РАЗДЕЛЫ
                elif msg_l == "админ-панель" and is_adm:
                    send_msg(uid, "Управление салоном:", keyboards.admin_menu())

                elif msg_l == "личный кабинет":
                    name_db, phone_db = database.get_user_data(uid)
                    d_phone = phone_db if phone_db else "не привязан"
                    send_msg(uid, f"👤 Профиль: {name_db}\n📞 Тел: {d_phone}\n\nДля привязки напишите: Мой телефон 8XXXXXXXXXX")

                elif msg_l == "о салоне":
                    send_msg(uid, f"👓 {SALON_NAME}\n📍 Измайловский пр., 7\n⏰ 10:00-20:00")

                elif msg_l == "мои заказы":
                    orders = database.get_user_orders(uid)
                    text = "📦 Ваши заказы:\n" + "\n".join([f"№{o}: {s}" for o, s in orders]) if orders else "Заказов не найдено."
                    send_msg(uid, text)
                
                # 3. ЛОГИКА ПОМОЩИ (НОВЫЙ БЛОК)
                elif msg_l == "помощь":
                    send_msg(uid, "Выберите раздел помощи:", keyboards.help_menu(is_adm))
                
                elif msg_l == "помощь для клиента":
                    send_msg(uid, CLIENT_HELP_TEXT, keyboards.back_to_main_menu_keyboard())
                
                elif msg_l == "помощь для админа" and is_adm:
                    send_msg(uid, ADMIN_HELP_TEXT, keyboards.back_to_main_menu_keyboard())
                
                elif msg_l == "назад к помощи":
                    send_msg(uid, "Выберите раздел помощи:", keyboards.help_menu(is_adm))

                # 4. ЛОГИКА ЗАПИСИ
                elif msg_l == "записаться на прием":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(0))

                elif msg_l == "⬅️ предыдущие даты":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(0))

                elif msg_l == "следующие даты ➡️":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(1))

                elif msg_l.startswith("дата: "):
                    d = msg.replace("Дата: ", "").replace("дата: ", "")
                    try:
                        day, month = map(int, d.split('.'))
                        now = datetime.now()
                        if month < now.month or (month == now.month and day < now.day):
                            send_msg(uid, "❌ Нельзя записаться на прошедшую дату.")
                            continue
                    except: pass

                    database.set_user_last_date(uid, d)
                    booked = database.get_booked_slots(d)
                    send_msg(uid, f"Свободное время на {d}:", keyboards.time_slots(booked, d))

                elif "занято" in msg_l:
                     send_msg(uid, "❌ Это время уже занято. Выберите другое из списка.")

                elif re.match(r'^\d{2}:\d{2}$', msg):
                    d = database.get_user_last_date(uid)
                    if not d:
                        send_msg(uid, "❌ Сначала выберите дату (нажмите 'Записаться на прием').")
                        continue
                    
                    if database.create_appointment(uid, f"{d} в {msg}"):
                        send_msg(uid, f"✅ Успешно! Ждем вас {d} в {msg}.", keyboards.main_menu(is_adm))
                        send_msg(ADMIN_ID, f"🔔 Новая запись: {d} в {msg}\n👤 {get_name(uid)} (ID: {uid})")
                    else:
                        send_msg(uid, "❌ Ошибка: это время уже занято или вы уже записаны.")

                # 5. АДМИН-ПАНЕЛЬ
                elif is_adm and msg_l == "список клиентов":
                    clients = database.get_all_clients()
                    res = "👥 Клиенты:\n" + "\n".join([f"• {n} | {p if p else 'нет тел.'} | ID: {i}" for i, n, p, lv in clients])
                    send_msg(uid, res)

                elif is_adm and msg_l.startswith("инфо "):
                    target = msg.split()[-1]
                    data = database.get_client_full_card(target)
                    if data:
                        u = data['profile']
                        apps = "\n".join([f"📅 {a[0]}" for a in data['apps']]) or "Нет"
                        orders = "\n".join([f"📦 №{o[0]}: {o[1]}" for o in data['orders']]) or "Нет"
                        send_msg(uid, f"👤 {u[1]}\n📞 {u[2] if u[2] else 'не указан'}\n🆔 {u[0]}\n\nВизиты:\n{apps}\n\nЗаказы:\n{orders}")
                    else: send_msg(uid, "❌ Не найден.")

                elif is_adm and msg_l == "все заказы":
                    orders = database.get_all_orders()
                    res = "\n".join([f"📦 №{o} | {s} | {n}" for o, s, n in orders]) if orders else "Заказов нет."
                    send_msg(uid, f"📋 Список заказов:\n{res}")

                elif is_adm and msg_l == "список записей":
                    apps = database.get_all_appointments()
                    res = "\n".join([f"• {dt}: {name}" for dt, name in apps]) if apps else "Записей нет."
                    send_msg(uid, f"📅 Записи:\n{res}")

                elif is_adm and msg_l.startswith("заказ "):
                    p = msg.split()
                    # Заказ 12345 Готов к выдаче 89991112233
                    if len(p) >= 3:
                        order_id = p[1]
                        status_parts = []
                        phone_for_order = None

                        # Парсим статус и ищем телефон в конце
                        for i in range(2, len(p)):
                            part = p[i]
                            # Простая проверка на то, что часть похожа на телефон (8/7/+)
                            if (re.fullmatch(r"^(8|\+7)\d{10}$", part) or re.fullmatch(r"^\d{11}$", part)):
                                phone_for_order = re.sub(r"\D", "", part) # Нормализуем телефон
                                break # Прекращаем собирать статус, если нашли телефон
                            status_parts.append(part)
                        
                        status = " ".join(status_parts)
                        if not status: # Если статус пустой (например, только телефон был после номера заказа)
                             send_msg(uid, "❌ Укажите статус заказа.")
                             continue

                        target_user_id = database.update_order(order_id, status, phone_for_order)
                        send_msg(uid, f"✅ Статус заказа №{order_id} обновлен до '{status}'.")
                        
                        if "готов" in status.lower() and target_user_id:
                            send_msg(target_user_id, f"👓 Заказ №{order_id} готов! Вы можете его забрать.")
                    else:
                        send_msg(uid, "❌ Неверный формат команды. Используйте: Заказ [номер] [статус] [телефон (необязательно)]")

                # 6. ОБЩЕЕ
                elif msg_l.startswith("мой телефон"):
                    ph = re.sub(r"\D", "", msg)
                    if len(ph) == 11 and (ph.startswith('7') or ph.startswith('8')):
                        database.update_user_phone(uid, ph)
                        send_msg(uid, f"✅ Телефон {ph} привязан!")
                    else: send_msg(uid, "❌ Введите 11 цифр, начиная с 7 или 8.")

                elif msg_l == "назад":
                    send_msg(uid, f"Вы вернулись в главное меню, {get_name(uid)}.", keyboards.main_menu(is_adm))

                else:
                    if not is_adm:
                        send_msg(uid, "Пожалуйста, воспользуйтесь кнопками меню.", keyboards.main_menu(is_adm))

    except Exception as e:
        print(f"⚠️ Сбой в основном цикле: {e}")
        time.sleep(5)
