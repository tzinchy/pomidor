
import pytest
import requests

# Полный маппинг статусов
STATUS_MAPPING = {
    1: "Согласие",
    2: "Отказ",
    3: "Суд",
    4: "МФР Компенсация",
    5: "МФР Докупка",
    6: "Ожидание",
    7: "Ждёт одобрения",
    8: "Не подобрано",
    9: "МФР (вне района)",
    10: "МФР Компенсация (вне района)",
    11: "Свободная",
    16: "Подготовить смотровой",
    17: "Отказ (Выход из Суда)"
}

# Обратное маппирование
STATUS_NAME_TO_ID = {v: k for k, v in STATUS_MAPPING.items()}

# Проверенные тестовые данные
TEST_DATA = [
    {
        'affair_id': 1001,
        'offer_id': 4,
        'new_aparts':  [2004, 2005] 
    }
]

# Тест-кейсы
TEST_CASES = [
    # Ждет одобрение (7) + все статусы
    (7, 7, 7, 7, 7),   # Ждет одобрение + Ждет одобрение = Ждет одобрение, new_apart1=7, new_apart2=7
    (7, 2, 2, 7, 11),  # Ждет одобрение + Отказ = Отказ, new_apart1=7, new_apart2=11 (Свободная)
    (7, 1, 7, 7, 1),   # Ждет одобрение + Согласие = Ждет одобрение, new_apart1=7, new_apart2=1
    (7, 6, 7, 7, 6),   # Ждет одобрение + Ожидание = Ждет одобрение, new_apart1=7, new_apart2=6
    (7, 3, 7, 7, 3),   # Ждет одобрение + Суд = Ждет одобрение, new_apart1=7, new_apart2=3
    (7, 16, 7, 7, 16), # Ждет одобрение + Подготовить смотровой = Ждет одобрение, new_apart1=7, new_apart2=16
    (7, 4, 7, 7, 4),   # Ждет одобрение + МФР Компенсация = Ждет одобрение, new_apart1=7, new_apart2=4
    (7, 10, 7, 7, 10), # Ждет одобрение + МФР Компенсация (Вне района) = Ждет одобрение, new_apart1=7, new_apart2=10
    (7, 5, 7, 7, 5),   # Ждет одобрение + МФР Докупка = Ждет одобрение, new_apart1=7, new_apart2=5
    (7, 9, 7, 7, 9),   # Ждет одобрение + МФР (вне района) = Ждет одобрение, new_apart1=7, new_apart2=9
    
    # Отказ (2) + все статусы
    (2, 7, 2, 11, 7),  # Отказ + Ждет одобрение = Отказ, new_apart1=11, new_apart2=7
    (2, 2, 2, 11, 11), # Отказ + Отказ = Отказ, new_apart1=11, new_apart2=11
    (2, 1, 2, 11, 1),  # Отказ + Согласие = Отказ, new_apart1=11, new_apart2=1
    (2, 6, 2, 11, 6),  # Отказ + Ожидание = Отказ, new_apart1=11, new_apart2=6
    (2, 3, 2, 11, 3),  # Отказ + Суд = Отказ, new_apart1=11, new_apart2=3
    (2, 16, 2, 11, 16),# Отказ + Подготовить смотровой = Отказ, new_apart1=11, new_apart2=16
    (2, 4, 2, 11, 4),  # Отказ + МФР Компенсация = Отказ, new_apart1=11, new_apart2=4
    (2, 10, 2, 11, 10),# Отказ + МФР Компенсация (Вне района) = Отказ, new_apart1=11, new_apart2=10
    (2, 5, 2, 11, 5),  # Отказ + МФР Докупка = Отказ, new_apart1=11, new_apart2=5
    (2, 9, 2, 11, 9),  # Отказ + МФР (вне района) = Отказ, new_apart1=11, new_apart2=9
    
    # Согласие (1) + все статусы
    (1, 7, 7, 1, 7),   # Согласие + Ждет одобрение = Ждет одобрение, new_apart1=1, new_apart2=7
    (1, 2, 2, 1, 11),  # Согласие + Отказ = Отказ, new_apart1=1, new_apart2=11
    (1, 1, 1, 1, 1),   # Согласие + Согласие = Согласие, new_apart1=1, new_apart2=1
    (1, 6, 6, 1, 6),   # Согласие + Ожидание = Ожидание, new_apart1=1, new_apart2=6
    (1, 3, 3, 1, 3),   # Согласие + Суд = Суд, new_apart1=1, new_apart2=3
    (1, 16, 16, 1, 16),# Согласие + Подготовить смотровой = Подготовить смотровой, new_apart1=1, new_apart2=16
    (1, 4, 4, 1, 4),   # Согласие + МФР Компенсация = МФР Компенсация, new_apart1=1, new_apart2=4
    (1, 10, 10, 1, 10),# Согласие + МФР Компенсация (Вне района) = МФР Компенсация (Вне района), new_apart1=1, new_apart2=10
    (1, 5, 5, 1, 5),   # Согласие + МФР Докупка = МФР Докупка, new_apart1=1, new_apart2=5
    (1, 9, 9, 1, 9),   # Согласие + МФР (вне района) = МФР (вне района), new_apart1=1, new_apart2=9
    
    # Ожидание (6) + все статусы
    (6, 7, 7, 6, 7),   # Ожидание + Ждет одобрение = Ждет одобрение, new_apart1=6, new_apart2=7
    (6, 2, 2, 6, 11),  # Ожидание + Отказ = Отказ, new_apart1=6, new_apart2=11
    (6, 1, 6, 6, 1),   # Ожидание + Согласие = Ожидание, new_apart1=6, new_apart2=1
    (6, 6, 6, 6, 6),   # Ожидание + Ожидание = Ожидание, new_apart1=6, new_apart2=6
    (6, 3, 6, 6, 3),   # Ожидание + Суд = Ожидание, new_apart1=6, new_apart2=3
    (6, 16, 16, 6, 16),# Ожидание + Подготовить смотровой = Подготовить смотровой, new_apart1=6, new_apart2=16
    (6, 4, 6, 6, 4),   # Ожидание + МФР Компенсация = Ожидание, new_apart1=6, new_apart2=4
    (6, 10, 6, 6, 10), # Ожидание + МФР Компенсация (Вне района) = Ожидание, new_apart1=6, new_apart2=10
    (6, 5, 6, 6, 5),   # Ожидание + МФР Докупка = Ожидание, new_apart1=6, new_apart2=5
    (6, 9, 6, 6, 9),   # Ожидание + МФР (вне района) = Ожидание, new_apart1=6, new_apart2=9
    
    # Суд (3) + все статусы
    (3, 7, 7, 3, 7),   # Суд + Ждет одобрение = Ждет одобрение, new_apart1=3, new_apart2=7
    (3, 2, 2, 3, 11),  # Суд + Отказ = Отказ, new_apart1=3, new_apart2=11
    (3, 1, 3, 3, 1),   # Суд + Согласие = Суд, new_apart1=3, new_apart2=1
    (3, 6, 6, 3, 6),   # Суд + Ожидание = Ожидание, new_apart1=3, new_apart2=6
    (3, 3, 3, 3, 3),   # Суд + Суд = Суд, new_apart1=3, new_apart2=3
    (3, 16, 16, 3, 16),# Суд + Подготовить смотровой = Подготовить смотровой, new_apart1=3, new_apart2=16
    (3, 4, 3, 3, 4),   # Суд + МФР Компенсация = Суд, new_apart1=3, new_apart2=4
    (3, 10, 3, 3, 10), # Суд + МФР Компенсация (Вне района) = Суд, new_apart1=3, new_apart2=10
    (3, 5, 3, 3, 5),   # Суд + МФР Докупка = Суд, new_apart1=3, new_apart2=5
    (3, 9, 3, 3, 9),   # Суд + МФР (вне района) = Суд, new_apart1=3, new_apart2=9
    
    # Подготовить смотровой (16) + все статусы
    (16, 7, 7, 16, 7),   # Подготовить смотровой + Ждет одобрение = Ждет одобрение, new_apart1=16, new_apart2=7
    (16, 2, 2, 16, 11),  # Подготовить смотровой + Отказ = Отказ, new_apart1=16, new_apart2=11
    (16, 1, 16, 16, 1),  # Подготовить смотровой + Согласие = Подготовить смотровой, new_apart1=16, new_apart2=1
    (16, 6, 16, 16, 6),  # Подготовить смотровой + Ожидание = Подготовить смотровой, new_apart1=16, new_apart2=6
    (16, 3, 16, 16, 3),  # Подготовить смотровой + Суд = Подготовить смотровой, new_apart1=16, new_apart2=3
    (16, 16, 16, 16, 16),# Подготовить смотровой + Подготовить смотровой = Подготовить смотровой, new_apart1=16, new_apart2=16
    (16, 4, 16, 16, 4),  # Подготовить смотровой + МФР Компенсация = Подготовить смотровой, new_apart1=16, new_apart2=4
    (16, 10, 16, 16, 10),# Подготовить смотровой + МФР Компенсация (Вне района) = Подготовить смотровой, new_apart1=16, new_apart2=10
    (16, 5, 16, 16, 5),  # Подготовить смотровой + МФР Докупка = Подготовить смотровой, new_apart1=16, new_apart2=5
    (16, 9, 16, 16, 9),  # Подготовить смотровой + МФР (вне района) = Подготовить смотровой, new_apart1=16, new_apart2=9
    
    # МФР Компенсация (4) + все статусы
    (4, 7, 7, 4, 7),   # МФР Компенсация + Ждет одобрение = Ждет одобрение, new_apart1=4, new_apart2=7
    (4, 2, 2, 4, 11),  # МФР Компенсация + Отказ = Отказ, new_apart1=4, new_apart2=11
    (4, 1, 4, 4, 1),   # МФР Компенсация + Согласие = МФР Компенсация, new_apart1=4, new_apart2=1
    (4, 6, 6, 4, 6),   # МФР Компенсация + Ожидание = Ожидание, new_apart1=4, new_apart2=6
    (4, 3, 3, 4, 3),   # МФР Компенсация + Суд = Суд, new_apart1=4, new_apart2=3
    (4, 16, 16, 4, 16),# МФР Компенсация + Подготовить смотровой = Подготовить смотровой, new_apart1=4, new_apart2=16
    (4, 4, 4, 4, 4),   # МФР Компенсация + МФР Компенсация = МФР Компенсация, new_apart1=4, new_apart2=4
    (4, 5, 4, 4, 5),   # МФР Компенсация + МФР Докупка = МФР Компенсация, new_apart1=4, new_apart2=5
    
    # МФР Компенсация (Вне района) (10) + все статусы
    (10, 7, 7, 10, 7),   # МФР Компенсация (Вне района) + Ждет одобрение = Ждет одобрение, new_apart1=10, new_apart2=7
    (10, 2, 2, 10, 11),  # МФР Компенсация (Вне района) + Отказ = Отказ, new_apart1=10, new_apart2=11
    (10, 1, 10, 10, 1),  # МФР Компенсация (Вне района) + Согласие = МФР Компенсация (Вне района), new_apart1=10, new_apart2=1
    (10, 6, 6, 10, 6),   # МФР Компенсация (Вне района) + Ожидание = Ожидание, new_apart1=10, new_apart2=6
    (10, 3, 3, 10, 3),   # МФР Компенсация (Вне района) + Суд = Суд, new_apart1=10, new_apart2=3
    (10, 16, 16, 10, 16),# МФР Компенсация (Вне района) + Подготовить смотровой = Подготовить смотровой, new_apart1=10, new_apart2=16
    (10, 10, 4, 10, 10), # МФР Компенсация (Вне района) + МФР Компенсация (Вне района) = МФР Компенсация, new_apart1=10, new_apart2=10
    (10, 5, 10, 10, 5),  # МФР Компенсация (Вне района) + МФР Докупка = МФР Компенсация (Вне района), new_apart1=10, new_apart2=5
    
    # МФР Докупка (5) + все статусы
    (5, 7, 7, 5, 7),   # МФР Докупка + Ждет одобрение = Ждет одобрение, new_apart1=5, new_apart2=7
    (5, 2, 2, 5, 11),  # МФР Докупка + Отказ = Отказ, new_apart1=5, new_apart2=11
    (5, 1, 5, 5, 1),   # МФР Докупка + Согласие = МФР Докупка, new_apart1=5, new_apart2=1
    (5, 6, 6, 5, 6),   # МФР Докупка + Ожидание = Ожидание, new_apart1=5, new_apart2=6
    (5, 3, 3, 5, 3),   # МФР Докупка + Суд = Суд, new_apart1=5, new_apart2=3
    (5, 16, 16, 5, 16),# МФР Докупка + Подготовить смотровой = Подготовить смотровой, new_apart1=5, new_apart2=16
    (5, 10, 10, 5, 10),# МФР Докупка + МФР Компенсация (Вне района) = МФР Компенсация (Вне района), new_apart1=5, new_apart2=10
    (5, 5, 5, 5, 5),   # МФР Докупка + МФР Докупка = МФР Докупка, new_apart1=5, new_apart2=5
    (5, 4, 4, 5, 4),   # МФР Докупка + МФР Компенсация = МФР Компенсация, new_apart1=5, new_apart2=4
    (5, 9, 9, 5, 9),   # МФР Докупка + МФР (вне района) = МФР (вне района), new_apart1=5, new_apart2=9
    
    # МФР (вне района) (9) + все статусы
    (9, 7, 7, 9, 7),   # МФР (вне района) + Ждет одобрение = Ждет одобрение, new_apart1=9, new_apart2=7
    (9, 2, 2, 9, 11),  # МФР (вне района) + Отказ = Отказ, new_apart1=9, new_apart2=11
    (9, 1, 9, 9, 1),   # МФР (вне района) + Согласие = МФР (вне района), new_apart1=9, new_apart2=1
    (9, 6, 6, 9, 6),   # МФР (вне района) + Ожидание = Ожидание, new_apart1=9, new_apart2=6
    (9, 3, 3, 9, 3),   # МФР (вне района) + Суд = Суд, new_apart1=9, new_apart2=3
    (9, 16, 16, 9, 16),# МФР (вне района) + Подготовить смотровой = Подготовить смотровой, new_apart1=9, new_apart2=16
    (9, 9, 9, 9, 9),   # МФР (вне района) + МФР (вне района) = МФР (вне района), new_apart1=9, new_apart2=9
    (9, 5, 9, 9, 5),   # МФР (вне района) + МФР Докупка = МФР (вне района), new_apart1=9, new_apart2=5
]

@pytest.mark.parametrize('status1,status2,expected_old,expected_new1,expected_new2', TEST_CASES)
@pytest.mark.parametrize('test_data', TEST_DATA)
def test_apartment_status_changes(status1, status2, expected_old, expected_new1, expected_new2, test_data):
    """Тестирование изменения статусов квартир"""
    affair_id = test_data['affair_id']
    offer_id = test_data['offer_id']
    
    # Выбираем квартиры для теста
    new_aparts = test_data['new_aparts'] # Берем первые 2 квартиры
    
    # 1. Устанавливаем статусы для квартир
    
    # Для NewApartment 1
    url1 = f"http://127.0.0.1:8000/tables/apartment/{affair_id}/{new_aparts[0]}/change_status?apart_type=OldApart"
    res1 = requests.post(url1, json={'new_status': STATUS_MAPPING[status1]})
    assert res1.status_code == 200, f"Ошибка установки статуса для {new_aparts[0]}: {res1.text}"
    
    if len(new_aparts) > 1:
        url2 = f"http://127.0.0.1:8000/tables/apartment/{affair_id}/{new_aparts[1]}/change_status?apart_type=OldApart"
        res2 = requests.post(url2, json={'new_status': STATUS_MAPPING[status2]})
        assert res2.status_code == 200, f"Ошибка установки статуса для {new_aparts[1]}: {res2.text}"
    
    new1_url = f"http://127.0.0.1:8000/tables/apartment/{new_aparts[0]}?apart_type=NewApartment"
    new1_res = requests.get(new1_url)
    assert new1_res.status_code == 200
    
    new1_data = new1_res.json()
    assert new1_data['status_id'] == expected_new1
    
    # Для второй квартиры (если есть)
    if len(new_aparts) > 1:
        new2_url = f"http://127.0.0.1:8000/tables/apartment/{new_aparts[1]}?apart_type=NewApartment"
        new2_res = requests.get(new2_url)
        assert new2_res.status_code == 200
        
        new2_data = new2_res.json()
        assert new2_data['status_id'] == expected_new2
