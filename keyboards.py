from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime, timedelta

def main_menu():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Записаться на прием", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Статус заказа", color=VkKeyboardColor.SECONDARY)
    kb.add_button("О салоне", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

def date_selection():
    kb = VkKeyboard(one_time=True)
    today = datetime.now().strftime("%d.%m")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m")
    kb.add_button(f"Дата: {today}", color=VkKeyboardColor.PRIMARY)
    kb.add_button(f"Дата: {tomorrow}", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()

def time_slots(booked_times):
    kb = VkKeyboard(one_time=True)
    start = datetime.strptime("10:00", "%H:%M")
    end = datetime.strptime("19:30", "%H:%M")
    current = start
    count = 0
    
    while current <= end:
        time_str = current.strftime("%H:%M")
        
        if time_str in booked_times:
            # Если время занято — кнопка белая (SECONDARY) и текст с пометкой
            kb.add_button(f"({time_str})", color=VkKeyboardColor.SECONDARY)
        else:
            # Если свободно — синяя (PRIMARY)
            kb.add_button(time_str, color=VkKeyboardColor.PRIMARY)
            
        count += 1
        if count % 4 == 0 and current < end:
            kb.add_line()
        current += timedelta(minutes=30)
        
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()
