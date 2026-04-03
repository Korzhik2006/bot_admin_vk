import os, pytest, json, database, keyboards

database.DATABASE = 'test_optica.db'

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists('test_optica.db'): os.remove('test_optica.db')
    database.init_db(350445907)
    yield

def test_full_flow():
    # 1. Регистрация и привязка телефона
    database.add_user(111, "Иван Иванов")
    database.update_user_phone(111, "89991112233")
    
    # 2. Создание заказа админом (CRM связка)
    target = database.update_order("500", "В работе", "89991112233")
    assert target == 111
    
    # 3. Проверка заказов
    orders = database.get_all_orders()
    assert orders[0][0] == "500"
    assert orders[0][2] == "Иван Иванов"
    
    # 4. Проверка записей
    database.create_appointment(111, "01.01 в 12:00")
    booked = database.get_booked_slots("01.01")
    assert "12:00" in booked
    
    # 5. Лимиты ВК
    kb = json.loads(keyboards.date_selection(0))
    assert len(kb['buttons']) <= 10
    for r in kb['buttons']: assert len(r) <= 5
