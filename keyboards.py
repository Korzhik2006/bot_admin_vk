from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime, timedelta

def main_menu(is_admin=False):
    kb = VkKeyboard(one_time=False)
    kb.add_button("Записаться на прием", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Статус заказа", color=VkKeyboardColor.SECONDARY)
    kb.add_button("О салоне", color=VkKeyboardColor.SECONDARY)
    # Если зашел админ, добавляем кнопку панели
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

def date_selection():
    kb = VkKeyboard(one_time=True)
    # Выводим ближайшие 9 дней (сетка 3х3)
    for i in range(9):
        day = (datetime.now() + timedelta(days=i)).strftime("%d.%m")
        kb.add_button(f"Дата: {day}", color=VkKeyboardColor.PRIMARY)
        # Каждые 3 кнопки делаем новую строку
        if (i + 1) % 3 == 0 and i < 8:
            kb.add_line()
    
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def time_slots(booked_times):
    kb = VkKeyboard(one_time=True)
    
    # Определяем диапазон времени
    start_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("19:30", "%H:%M")
    current = start_time
    
    count = 0
    while current <= end_time:
        t_str = current.strftime("%H:%M")
        
        # Проверяем, занято ли время (booked_times приходит из БД)
        if t_str in booked_times:
            # Белая кнопка для занятого времени
            kb.add_button(f"({t_str})", color=VkKeyboardColor.SECONDARY)
        else:
            # Синяя кнопка для свободного времени
            kb.add_button(t_str, color=VkKeyboardColor.PRIMARY)
        
        count += 1
        
        # Переносим строку через каждые 4 кнопки
        if count % 4 == 0 and current < end_time:
            kb.add_line()
            
        # ИСПРАВЛЕНО: аргумент 'minutes' вместо 'minutes_delta'
        current += timedelta(minutes=30)
    
    # Кнопку "Назад" выносим на отдельную строку в самом конце
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    
    return kb.get_keyboard()
