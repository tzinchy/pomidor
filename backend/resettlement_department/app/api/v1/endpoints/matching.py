from fastapi import APIRouter
from depends import apartment_service
from schema.apartment import ApartTypeSchema, MatchingSchema
from service.alghorithm import match_new_apart_to_family_batch
from fastapi import File, HTTPException, UploadFile
from io import BytesIO
import pandas as pd
from service.apartment_insert import insert_to_db
from pathlib import Path


router = APIRouter(prefix="/fisrt_matching", tags=["Первичный подбор"])


# Получение списка адресов домов
@router.get("/old_apartment/house_addresses")
async def get_family_structure_house_addresses():
    return await apartment_service.get_house_address_with_room_count(
        apart_type=ApartTypeSchema.OLD
    )


# Получение списка адресов домов
@router.get("/new_apartment/house_addresses")
async def get_new_apartment_house_addresses():
    return await apartment_service.get_house_address_with_room_count(
        apart_type=ApartTypeSchema.NEW
    )


@router.post("/matching")
async def start_matching(requirements: MatchingSchema):
    print(requirements.old_apartment_house_address)
    print("--------------------------------------")
    print(requirements.new_apartment_house_address)
    matching_result = match_new_apart_to_family_batch(
        new_selected_districts=requirements.new_apartment_district,
        old_selected_districts=requirements.old_apartment_district,
        new_selected_areas=requirements.new_apartment_municipal_district,
        old_selected_areas=requirements.old_apartment_district,
        new_selected_addresses=requirements.new_apartment_house_address,
        old_selected_addresses=requirements.old_apartment_house_address,
        date=requirements.is_date,
    )
    print(matching_result)

    return matching_result


@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Создаем папки если их нет
        folders = [Path("manual_download")]

        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)

        # Читаем содержимое файла
        content = await file.read()

        # Сохраняем в manual_download
        manual_path = Path("manual_download") / file.filename
        with open(manual_path, "wb") as f:
            f.write(content)

        # Обработка данных
        new_apart = pd.read_excel(BytesIO(content), sheet_name="new_apart")
        old_apart = pd.read_excel(BytesIO(content), sheet_name="old_apart")
        cin = pd.read_excel(BytesIO(content), sheet_name="cin")
        # Вызов функции с нужными параметрами
        insert_to_db(
            new_apart_df=new_apart,
            old_apart_df=old_apart,
            cin_df=cin,
            file_name=file.filename,  # Имя файла
            file_path=str(manual_path),  # Полный путь к файлу
        )
        return {"message": "Файл успешно загружен и обработан"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при обработке файла: {str(e)}"
        )
    finally:
        await file.close()
