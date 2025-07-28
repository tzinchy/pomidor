import pytest
import requests


@pytest.mark.parametrize('apart_type', ['OldApart', 'NewApartment'])
def test_district_building_flow(apart_type):
    # Шаг 1: Получаем районы
    districts_response = requests.get(f'http://localhost:8000/tables/district?apart_type={apart_type}')
    districts = districts_response.json()
    
    # Шаг 2: Для каждого района получаем здания
    for district in districts:
        buildings_response = requests.get(f'http://localhost:8000/tables/municipal_district?district={district}&apart_type={apart_type}')
        assert buildings_response.status_code == 200
        buildings = buildings_response.json()
        
        # Шаг 3: Проверяем каждое здание
        for building in buildings:
            assert isinstance(building, str)