from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from datetime import datetime, timedelta

def main_menu():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Записаться на прием", color=VkKeyboardColor.PRIMARY)
    kb.add_line()
    kb.add_button("Статус заказа", color=VkKeyboardColor.SECONDARY)
    kb.add_button("О салоне", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()

def time_slots():
    kb = VkKeyboard(one_time=True)
    # Интервалы с 10:00 до 19:30 каждые 30 мин
    start_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("19:30", "%H:%M")
    
    current = start_time
    count = 0
    while current <= end_time:
        time_str = current.strftime("%H:%M")
        kb.add_button(f"Запись на {time_str}", color=VkKeyboardColor.POSITIVE)
        count += 1
        if count % 3 == 0: kb.add_line() # По 3 кнопки в ряд
        current += timedelta(minutes=30)
    
    kb.add_line()
    kb.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return kb.get_keyboard()
