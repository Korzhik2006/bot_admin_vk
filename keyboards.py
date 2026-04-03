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

def admin_menu():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Список записей", color=VkKeyboardColor.PRIMARY)
    kb.add_button("Все заказы", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("В главное меню", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

def date_selection(page=0):
    kb = VkKeyboard(one_time=True)
    start_idx = page * 12
    for i in range(start_idx, start_idx + 12):
        day = (datetime.now() + timedelta(days=i)).strftime("%d.%m")
        kb.add_button(f"Дата: {day}", color=VkKeyboardColor.PRIMARY)
        if (i + 1) % 3 == 0: kb.add_line()
    
    if page == 0: kb.add_button("Следующие даты ➡️", color=VkKeyboardColor.SECONDARY)
    else: kb.add_button("⬅️ Предыдущие даты", color=VkKeyboardColor.SECONDARY)
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def time_slots(booked):
    kb = VkKeyboard(one_time=True)
    curr, end = datetime.strptime("10:00", "%H:%M"), datetime.strptime("19:30", "%H:%M")
    count = 0
    while curr <= end:
        t = curr.strftime("%H:%M")
        color = VkKeyboardColor.SECONDARY if t in booked else VkKeyboardColor.PRIMARY
        label = f"({t})" if t in booked else t
        kb.add_button(label, color=color)
        count += 1
        if count % 4 == 0 and curr < end: kb.add_line()
        curr += timedelta(minutes=30)
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()
