from datetime import datetime, time
from io import BytesIO
from pathlib import Path
from typing import List

import pandas as pd
from depends import env_service
from fastapi import APIRouter, File, HTTPException, UploadFile
from RSM.RSM import get_kpu_xlsx_df, get_orders_xlsx_df, get_resurs_xlsx_df
from schema.history import EnvStatResponse
from service.apartment_insert import insert_data_to_new_apart, insert_data_to_old_apart
from service.order_insert import insert_data_to_order_decisions

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
    end_date = datetime.combine(datetime.now().date(), time(23, 59, 59))
    df = get_kpu_xlsx_df(start_date, end_date, category, layout_id)

    result = insert_data_to_old_apart(df)

    if isinstance(result, Exception):
        raise result
    return {result}


@router.patch("/get_new_apart", description='Для обновления ресурса с РСМ')
def from_rsm_get_new_apart() -> dict:
    layout_id = 21744
    df = get_resurs_xlsx_df(layout_id)
    if df.empty:
        return {"status": "error", "message": "Нет данных для вставки"}
    
    output = BytesIO()
    output.seek(0)
    result = insert_data_to_new_apart(df)
    return {"status": "success", "inserted": result}

@router.post("/upload-file/")
async def upload_file2(file: UploadFile = File(...)):
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


@router.post("/get_orders")
async def from_rsm_get_orders():
    layout_id = 22262
    start_date = datetime(2017, 1, 1, 0, 0, 0)
    end_date = datetime.combine(datetime.now().date(), time(23, 59, 59))
    order_decisions = get_orders_xlsx_df(layout_id=layout_id, start_date=start_date, end_date=end_date)
    if order_decisions.empty:
        return {"status": "error", "message": "Нет данных для вставки"}

    result = insert_data_to_order_decisions(order_decisions)
    
    return {"status": "success", "exit_code": result}

