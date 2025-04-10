import pytest
import requests

@pytest.mark.parametrize("input_param,expected", [
    ('OldApart', {'apart_type': 'OldApart'}),
    ('NewApartment', {'apart_type': 'NewApartment'}),
])
def test_apart_type(input_param, expected):
    response = requests.get(f'http://localhost:8000/tables/apart_type?apart_type={input_param}')
    assert response.status_code == 200
    assert response.json() == expected