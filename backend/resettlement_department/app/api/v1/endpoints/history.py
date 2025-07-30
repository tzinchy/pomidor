from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import FileResponse
import os
from pathlib import Path
from typing import List

from schema.history import HistoryResponse
from schema.apartment import Balance
from service.auth import mp_employee_required
from depends import history_service

from service.balance_alghorithm import save_views_to_excel

from service.container_service import (
    generate_excel_from_two_dataframes,
    upload_container,
    set_is_uploaded,
)
from service.container_service import update_apart_status_by_history_id

router = APIRouter(tags=["History"], dependencies=[Depends(mp_employee_required)])

@router.get("/history", response_model=List[HistoryResponse])
async def get_history():
    return await history_service.get_history()


@router.get("/manual")
async def get_manual_history():
    return await history_service.get_manual_load_history()


@router.post("/balance")
async def balance(requirements: Balance = Body(...)):
    try:
        # Создаем папки если их нет
        print("requirements", requirements)
        folders = [Path("uploads")]
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
        uploads_folder = os.path.join(os.getcwd(), "././uploads/")
        if requirements.is_wave or requirements.is_shadow:
            file_name = f"matching_result_{requirements.history_id}.xlsx"
        else:
            file_name = "matching_result.xlsx"
        output_path = os.path.join(uploads_folder, file_name)
        print(output_path)
        print(os.listdir(uploads_folder))
        print("ТО ЧТО ВЫШЕ ЭТО ПАРАМЕТР")
        if not (requirements.is_wave or requirements.is_shadow):
            save_views_to_excel(
                output_path=output_path,
                history_id=requirements.history_id,
            )

        return FileResponse(
            path=output_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=output_path,
        )
    except Exception as e:
        return {"error": str(e)}


@router.post("/container/{history_id}")
def container(history_id: int):
    # Генерация файла
    generate_excel_from_two_dataframes(history_id)

    # Формируем правильный путь к файлу
    file_path = f"./uploads/container_{history_id}.xlsx"

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден!")

    # Возвращаем файл как ответ
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"container_{history_id}.xlsx",
    )



@router.post("/push_container/{history_id}")
def push_container(history_id: int):
    try:
        # Генерация файла
        generate_excel_from_two_dataframes(history_id)
        set_is_uploaded(history_id)

        file_path = f"./uploads/container_{history_id}.xlsx"
        upload_container(history_id=history_id, file_path=file_path)
        update_apart_status_by_history_id(history_id=history_id)
    except Exception as e:
        return HTTPException(detail=str(e))


@router.patch("/approve/{history_id}")
async def approve_history(history_id: int):
    return await history_service.approve_history(history_id)


@router.delete("/clear_matching_files")
def clear_matching_files():
    try:
        history_service.clear_matching_files()
        return {"succes": True}
    except Exception as e:
        HTTPException(status_code=400, detail=e)


@router.delete("/delete/{history_id}")
async def cancell_history(history_id: int):
    return await history_service.cancell_history(history_id)


@router.delete("/delete/manual_load/{manual_load_id}")
async def cancell_history_manual_load(manual_load_id: int):
    return await history_service.cancell_manual_load(manual_load_id)
