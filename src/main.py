# ... (начало файла без изменений до момента обработки событий)

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                uid, msg = event.user_id, event.text.strip()
                msg_l, is_adm = msg.lower(), database.is_admin(uid)

                # РЕГИСТРАЦИЯ: при первом входе или по команде
                if msg_l in ["начать", "привет", "меню", "назад", "в главное меню"]:
                    full_name = get_name(uid)
                    database.add_user(uid, full_name)
                    send_msg(uid, f"Здравствуйте, {full_name}! Вас приветствует {SALON_NAME}.", keyboards.main_menu(is_adm))
                    continue
                
                # --- КЛИЕНТСКАЯ ЧАСТЬ ---
                if msg_l == "админ-панель" and is_adm:
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

                # --- ЛОГИКА ЗАПИСИ ---
                elif msg_l == "записаться на прием":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(0))
                
                elif msg_l == "⬅️ предыдущие даты":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(0))

                elif msg_l == "следующие даты ➡️":
                    send_msg(uid, "Выберите дату:", keyboards.date_selection(1))

                elif msg_l.startswith("дата: "):
                    d = msg.replace("Дата: ", "").replace("дата: ", "")
                    # Проверка на прошедшую дату
                    try:
                        day, month = map(int, d.split('.'))
                        now = datetime.now()
                        # Упрощенная проверка (в рамках текущего года)
                        if month < now.month or (month == now.month and day < now.day):
                            send_msg(uid, "❌ Нельзя записаться на прошедшую дату.")
                            continue
                    except: pass

                    database.set_user_last_date(uid, d)
                    booked = database.get_booked_slots(d)
                    send_msg(uid, f"Свободное время на {d}:", keyboards.time_slots(booked, d))

                # Обработка клика на занятое время
                elif "занято" in msg_l:
                     send_msg(uid, "❌ Это время уже занято. Выберите другое из списка.")

                # Исправленный блок записи на время (отступы!)
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

                # --- АДМИН-ПАНЕЛЬ И ПРОЧЕЕ ---
                # ... (остальной код без изменений)