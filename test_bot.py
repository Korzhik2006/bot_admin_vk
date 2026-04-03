import os, pytest, json, database, keyboards

database.DATABASE = 'test_optica.db'

@pytest.fixture(autouse=True)
def setup_db():
    if os.path.exists('test_optica.db'): os.remove('test_optica.db')
    database.init_db(350445907)
    yield

def test_full_crm_cycle():
    # 1. Регистрация и телефон
    database.add_user(111, "Иван Тест")
    database.update_user_phone(111, "89991234455")
    # 2. Привязка заказа через телефон
    target = database.update_order("777", "В работе", "89991234455")
    assert target == 111
    # 3. Проверка заказов пользователя
    orders = database.get_user_orders(111)
    assert len(orders) == 1
    # 4. Запись
    assert database.create_appointment(111, "01.01 в 10:00") is True
    assert "10:00" in database.get_booked_slots("01.01")
    # 5. Лимиты ВК
    kb = json.loads(keyboards.date_selection(0))
    assert len(kb['buttons']) <= 10
    for r in kb['buttons']: assert len(r) <= 5
