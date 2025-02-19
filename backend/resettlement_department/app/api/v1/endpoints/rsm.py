from RSM.RSM import get_kpu
from service.apartment_insert import insert_data_to_old
from fastapi import APIRouter
from datetime import datetime, time, timedelta

router = APIRouter(prefix='/rsm', tags=['rsm']) 

@router.patch('/get_old_apart')
def from_rsm_get_old_apart() -> None:
    category = [70, 91]
    layout_id = 22223 
    start_date = datetime(2017, 1, 1, 0, 0, 0)
    end_date = datetime.combine(datetime.now().date(), time(23, 59, 59))
    print(start_date, end_date)
    result = insert_data_to_old(get_kpu(start_date, end_date, 1, category, layout_id))
    return {result}
'''
@router.get('/update_info')
def get_update_info() -> dict: 
'''
