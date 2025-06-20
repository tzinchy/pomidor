import pytest
import requests

# Test dataset with specific offer_id and new_aparts relationships
TEST_DATA = [
    {
        'affair_id': 711392,
        'offer_id': 14025,
        'new_aparts': [8425283, 8668862]
    },
    {
        'affair_id': 711172,
        'offer_id': 534,
        'new_aparts': [8425283, 8668862]
    }
]

# Status mapping
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
    16: "Подготовить смотровой"
}

# Reverse mapping for status names to IDs
STATUS_NAME_TO_ID = {v: k for k, v in STATUS_MAPPING.items()}

# All test cases
ALL_TEST_CASES = [
    # Ждёт одобрения (7) combinations
    (7, 7, 7), (7, 2, 2), (7, 1, 7), (7, 6, 7), (7, 3, 7), 
    (7, 16, 7), (7, 4, 7), (7, 5, 7),
    
    # Отказ (2) combinations
    (2, 7, 2), (2, 2, 2), (2, 1, 2), (2, 6, 2), (2, 3, 2), 
    (2, 16, 2), (2, 4, 2), (2, 5, 2),
    
    # Согласие (1) combinations
    (1, 7, 7), (1, 2, 2), (1, 1, 1), (1, 6, 6), (1, 3, 3), 
    (1, 16, 16), (1, 4, 4), (1, 5, 5),
    
    # Ожидание (6) combinations
    (6, 7, 7), (6, 2, 2), (6, 1, 6), (6, 6, 6), (6, 3, 6), 
    (6, 16, 16), (6, 4, 6), (6, 5, 6),
    
    # Суд (3) combinations
    (3, 7, 7), (3, 2, 2), (3, 1, 3), (3, 6, 6), (3, 3, 3), 
    (3, 16, 16), (3, 4, 3), (3, 5, 3),
    
    # Подготовить смотровой (16) combinations
    (16, 7, 7), (16, 2, 2), (16, 1, 16), (16, 6, 16), (16, 3, 16), 
    (16, 16, 16), (16, 4, 16), (16, 5, 16),
    
    # МФР Компенсация (4) combinations
    (4, 7, 7), (4, 2, 2), (4, 1, 4), (4, 6, 6), (4, 3, 3), 
    (4, 16, 16), (4, 4, 4), (4, 5, 4),
    
    # МФР Докупка (5) combinations
    (5, 7, 7), (5, 2, 2), (5, 1, 5), (5, 6, 6), (5, 3, 3), 
    (5, 16, 16), (5, 5, 5), (5, 4, 4)
]

def set_apartment_status(affair_id, apart_id, apart_type, status_name):
    """Helper function to set apartment status"""
    url = f'http://127.0.0.1:8000/tables/apartment/{affair_id}/{apart_id}/change_status?apart_type={apart_type}'
    response = requests.post(url, data={'new_status': status_name})
    return response

def get_apartment_status(affair_id, apart_id, apart_type):
    """Helper function to get apartment status"""
    url = f'http://127.0.0.1:8000/tables/apartment/{affair_id}/{apart_id}?apart_type={apart_type}'
    response = requests.get(url)
    return response.json()

def get_old_apartment_status(affair_id, offer_id):
    """Helper function to get old apartment status"""
    url = f'http://127.0.0.1:8000/tables/apartment/{affair_id}?apart_type=OldApart'
    response = requests.get(url)
    data = response.json()
    
    # Old apartment status is directly in the response
    return data.get('status_id')

def get_new_apartment_status(affair_id, offer_id, new_apart_id):
    """Helper function to get new apartment status from old apartment response"""
    url = f'http://127.0.0.1:8000/tables/apartment/{affair_id}?apart_type=OldApart'
    response = requests.get(url)
    data = response.json()
    
    # Find the status in offers for the specific new apartment
    for offer_key, offers in data.get('offers', {}).items():
        if int(offer_key) == offer_id:
            for affair_key, offer_data in offers.items():
                if int(affair_key) == affair_id and str(new_apart_id) in offer_data.get('new_apart_id', ''):
                    return STATUS_NAME_TO_ID[offer_data['status']]
    
    raise ValueError(f"Could not find status for offer_id={offer_id}, affair_id={affair_id}, new_apart_id={new_apart_id}")

@pytest.mark.parametrize('test_data', TEST_DATA)
@pytest.mark.parametrize('status1,status2,expected_status', ALL_TEST_CASES)
def test_apartment_status_changes(test_data, status1, status2, expected_status):
    affair_id = test_data['affair_id']
    offer_id = test_data['offer_id']
    new_apart1, new_apart2 = test_data['new_aparts']
    
    # Set initial statuses for new apartments
    set_apartment_status(affair_id, new_apart1, 'NewApartment', STATUS_MAPPING[status1])
    set_apartment_status(affair_id, new_apart2, 'NewApartment', STATUS_MAPPING[status2])
    
    # Get the old apartment status (directly from its status_id)
    old_apart_status = get_old_apartment_status(affair_id, offer_id)
    
    # Verify old apartment status matches expected
    assert old_apart_status == expected_status, (
        f"For status combination {STATUS_MAPPING[status1]}+{STATUS_MAPPING[status2]}, "
        f"expected status_id {expected_status} but got {old_apart_status}"
    )
    
    # Verify new apartment statuses in the old apartment's offers
    new_apart1_status = get_new_apartment_status(affair_id, offer_id, new_apart1)
    assert new_apart1_status == status1, (
        f"New apartment 1 status changed from {status1} to {new_apart1_status}"
    )
    
    new_apart2_status = get_new_apartment_status(affair_id, offer_id, new_apart2)
    assert new_apart2_status == status2, (
        f"New apartment 2 status changed from {status2} to {new_apart2_status}"
    )