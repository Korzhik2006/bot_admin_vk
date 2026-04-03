import os, pytest, json, database, keyboards
from datetime import datetime, timedelta

database.DATABASE = 'test_optica.db'

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists('test_optica.db'): os.remove('test_optica.db')
    database.init_db(350445907)
    yield

def test_db_logic():
    database.add_user(111, "Иван Иванов")
    database.update_user_phone(111, "79990001122")
    # Проверка записи
    assert database.create_appointment(111, "05.04 в 12:00") is True
    assert "12:00" in database.get_booked_slots("05.04")
    # Проверка CRM
    target_uid = database.update_order("101", "Готов", "79990001122")
    assert target_uid == 111

def validate_vk_kb(kb_json):
    kb = json.loads(kb_json)
    rows = kb.get('buttons', [])
    assert len(rows) <= 10
    for row in rows: assert len(row) <= 5

def test_keyboards_limits():
    validate_vk_kb(keyboards.main_menu(True))
    validate_vk_kb(keyboards.date_selection(0))
    validate_vk_kb(keyboards.time_slots(["10:00"]))

def test_admin_and_delete():
    database.add_admin(111)
    assert database.is_admin(111) is True
    database.create_appointment(111, "05.04 в 15:00")
    assert database.delete_appointment("05.04 в 15:00") is True
