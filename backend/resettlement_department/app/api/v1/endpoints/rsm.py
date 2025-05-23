from datetime import datetime, time
from io import BytesIO
from pathlib import Path
from typing import List
from fastapi.concurrency import run_in_threadpool
import pandas as pd
from depends import env_service
from fastapi import APIRouter, File, HTTPException, UploadFile
from RSM.RSM import get_kpu_xlsx_df, get_orders_xlsx_df, get_resurs_xlsx_df
from schema.history import EnvStatResponse
from service.apartment_insert import insert_data_to_new_apart, insert_data_to_old_apart
from service.order_insert import insert_data_to_order_decisions
from datetime import timedelta

router = APIRouter(prefix="/rsm", tags=["RSM"])

@router.get("/update_info_stat", response_model=List[EnvStatResponse])
async def get_update_info():
    result = await env_service.get_env_history()

    response = [
        EnvStatResponse(id=item[0], name=item[1], timestamp=item[2], is_active=item[3])
        for item in result
    ]
    return response


@router.patch("/get_old_apart", description='Для обновления старых квартир с РСМ')
def from_rsm_get_old_apart() -> None:
    category = [70, 97]
    layout_id = 22223
    start_date = datetime(2017, 1, 1, 0, 0, 0)
    end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1) - timedelta(seconds=1)
    df = get_kpu_xlsx_df(start_date, end_date, category, layout_id)

    result = insert_data_to_old_apart(df)

    if isinstance(result, Exception):
        raise result
    return {result}


@router.patch("/get_new_apart", description='Для обновления ресурса с РСМ')
def from_rsm_get_new_apart():
    try:
        layout_id = 21744
        df = get_resurs_xlsx_df(layout_id)
        if df.empty:
            return {"status": "error", "message": "Нет данных для вставки"}
        
        output = BytesIO()
        output.seek(0)
        result = insert_data_to_new_apart(df)
        return {"status": "success", "inserted": result}
    except Exception as e: 
        return e

@router.post("/upload-file/", deprecated=True)
async def upload_file2(file: UploadFile = File(...)):
    """
    Загружает файл в таблицу old_apart.

    Эта функция не имеет практического применения
    и может быть удалена.
    """
    try:
        # Создаем папку если ее нет
        folders = [Path("manual_download")]

        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

        content = await file.read()

        # Сохраняем в manual_download
        manual_path = Path("manual_download") / file.filename
        with open(manual_path, "wb") as f:
            f.write(content)

        # Обработка данных
        old_apart = pd.read_excel(BytesIO(content))

        ds = insert_data_to_old_apart(old_apart)
        if isinstance(ds, Exception):
            raise ds
        return {"message": "Файл успешно загружен и обработан"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при обработке файла: {str(e)}"
        )
    finally:
        await file.close()


@router.patch("/get_orders")
async def from_rsm_get_orders():
    layout_id = 22262
    start_date = datetime(2017, 1, 1, 0, 0, 0)
    end_date = datetime.combine(datetime.now().date(), time(23, 59, 59))
    order_decisions = await run_in_threadpool(
        get_orders_xlsx_df, start_date, end_date, layout_id
        )
    #order_decisions.to_excel('order_data.xlsx')

    #order_decisions = pd.read_excel('/Users/macbook/work/backend/resettlement_department/app/orderdta.xlsx')
    #order_decisions.to_excel('orderdta.xlsx')
    if order_decisions.empty:
        return {"status": "error", "message": "Нет данных для вставки"}

    result = await run_in_threadpool(insert_data_to_order_decisions, order_decisions)
    
    return {"status": "success", "exit_code": result}

