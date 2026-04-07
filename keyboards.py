from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime, timedelta

def main_menu(is_admin=False):
    kb = VkKeyboard(one_time=False)
    kb.add_button("Записаться на прием", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Мои заказы", color=VkKeyboardColor.PRIMARY)
    kb.add_button("Личный кабинет", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("О салоне", color=VkKeyboardColor.SECONDARY)
    if is_admin:
        kb.add_line()
        kb.add_button("Админ-панель", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def date_selection(page=0):
    kb = VkKeyboard(one_time=True)
    start_idx = page * 12
    # Добавим ограничение, чтобы не предлагать даты слишком далеко в будущем
    for i in range(start_idx, start_idx + 12):
        day_dt = datetime.now() + timedelta(days=i)
        day_str = day_dt.strftime("%d.%m")
        kb.add_button(f"Дата: {day_str}", color=VkKeyboardColor.PRIMARY)
        if (i + 1) % 3 == 0: kb.add_line()
    
    kb.add_line()
    # Улучшенная навигация
    if page > 0:
        kb.add_button("⬅️ Предыдущие даты", color=VkKeyboardColor.SECONDARY)
    if page < 2: # Ограничим выбор 3 страницами (~месяц)
        kb.add_button("Следующие даты ➡️", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def time_slots(booked, selected_date_str):
    kb = VkKeyboard(one_time=True)
    curr = datetime.strptime("10:00", "%H:%M")
    end = datetime.strptime("19:30", "%H:%M")
    now = datetime.now()

    is_today = selected_date_str == now.strftime("%d.%m")
    
    count = 0
    while curr <= end:
        t_str = curr.strftime("%H:%M")
        is_booked = t_str in booked
        # Добавляем 15 минут запаса, чтобы нельзя было записаться на "сейчас"
        is_past = is_today and (curr.hour < now.hour or (curr.hour == now.hour and curr.minute <= now.minute + 15))

        if not is_past:
            if is_booked:
                # Занятое время делаем NEGATIVE (красным), чтобы визуально отличалось
                kb.add_button(f"Занято ({t_str})", color=VkKeyboardColor.NEGATIVE)
            else:
                kb.add_button(t_str, color=VkKeyboardColor.PRIMARY)

            count += 1
            if count % 4 == 0: kb.add_line()
            
        curr += timedelta(minutes=30)
    
    if kb.lines and not kb.lines[-1]: kb.lines.pop()
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def admin_menu():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Список записей", color=VkKeyboardColor.PRIMARY)
    kb.add_button("Все заказы", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Список клиентов", color=VkKeyboardColor.PRIMARY)
    kb.add_button("В главное меню", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()
