import os, pytest, json, database, keyboards
from datetime import datetime, timedelta
import sqlite3 # Добавлен для отладки

database.DATABASE = 'test_optica.db'

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists('test_optica.db'): os.remove('test_optica.db')
    database.init_db(350445907)
    yield

def test_user_and_phone():
    """Проверка регистрации и обновления телефона"""
    uid = 123
    database.add_user(uid, "Тестовый Юзер")
    name, phone = database.get_user_data(uid)
    assert name == "Тестовый Юзер"
    assert phone is None
    
    database.update_user_phone(uid, "79990001122")
    _, phone_after = database.get_user_data(uid)
    assert phone_after == "79990001122"

def test_order_crm_linking():
    """Проверка связки заказов с пользователями по телефону"""
    uid = 777
    phone = "71234567890"
    database.add_user(uid, "Борис")
    database.update_user_phone(uid, phone)
    
    target_uid = database.update_order("ORD-1", "Готов", phone)
    
    assert target_uid == uid
    
    user_orders = database.get_user_orders(uid)
    assert len(user_orders) == 1
    assert user_orders[0][0] == "ORD-1"

def test_appointment_logic():
    """Проверка записи: успех, дубликат, очистка даты"""
    uid = 100
    date_str = "20.10"
    time_str = "12:30"
    full_dt = f"{date_str} в {time_str}"
    
    database.add_user(uid, "Анна")
    database.set_user_last_date(uid, date_str)
    
    success = database.create_appointment(uid, full_dt)
    assert success is True
    
    success_duplicate = database.create_appointment(101, full_dt)
    assert success_duplicate is False
    
    assert database.get_user_last_date(uid) is None
    
    booked = database.get_booked_slots(date_str)
    assert time_str in booked

def test_reminders_query():
    """Проверка логики выборки для напоминаний"""
    uid = 55
    database.add_user(uid, "Виктор")
    target_dt = "15.05 в 10:00"
    database.create_appointment(uid, target_dt)
    
    pending = database.get_pending_reminders(target_dt)
    assert len(pending) == 1
    assert pending[0][0] == uid
    
    database.mark_reminded(uid, target_dt)
    pending_after = database.get_pending_reminders(target_dt)
    assert len(pending_after) == 0

def test_admin_reports():
    """Проверка админских функций получения данных"""
    uid = 1
    phone = "79001234567" # ИСПРАВЛЕНО: Теперь валидный 11-значный номер
    order_id = "T-1"
    
    database.add_user(uid, "Альберт")
    database.update_user_phone(uid, phone)
    database.create_appointment(uid, "10.10 в 10:00")
    database.update_order(order_id, "Ок", phone)
    
    # Список клиентов
    clients = database.get_all_clients()
    assert len(clients) >= 1
    
    # Полная карточка клиента
    card = database.get_client_full_card(uid)
    
    assert card['profile'][1] == "Альберт"
    assert len(card['apps']) == 1
    assert card['orders'][0][0] == order_id # Теперь это должно пройти

def test_keyboard_vk_limits():
    """Проверка, что клавиатуры не нарушают лимиты ВКонтакте"""
    kb_json = keyboards.date_selection(0)
    kb = json.loads(kb_json)
    
    for row in kb['buttons']:
        assert len(row) <= 5
    
    total_buttons = sum(len(row) for row in kb['buttons'])
    assert total_buttons <= 40

    booked = ["10:00", "10:30", "11:00"]
    kb_time_json = keyboards.time_slots(booked, "12.12")
    kb_time = json.loads(kb_time_json)
    
    for row in kb_time['buttons']:
        assert len(row) <= 5
