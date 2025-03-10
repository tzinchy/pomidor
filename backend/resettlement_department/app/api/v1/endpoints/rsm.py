from RSM.RSM import get_kpu, get_kurs_living_space
from service.apartment_insert import insert_data_to_old, new_apart_insert
from fastapi import APIRouter
from datetime import datetime, time, timedelta
import openpyxl
from io import BytesIO
from depends import history_service
from schema.history import EnvStatResponse
from typing import List

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

@router.patch('/get_new_apart')
def from_rsm_get_new_apart() -> dict:
    layout_id = 21744
    df = get_kurs_living_space([999, 99999999], layout_id)
    if df.empty:
        return {"status": "error", "message": "Нет данных для вставки"}

    # Сохраняем DataFrame в Excel
    output = BytesIO()
    #df.to_excel('test.xlsx', index=False, engine='openpyxl')
    output.seek(0)

    result = new_apart_insert(df)

    return {"status": "success", "inserted": result}


@router.get('/update_info_stat', response_model=List[EnvStatResponse])
async def get_update_info():
    result = await history_service.get_env_history()

    response = [
        EnvStatResponse(id=item[0], name=item[1], timestamp=item[2], is_active=item[3])
        for item in result
    ]
    return response