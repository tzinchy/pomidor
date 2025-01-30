from fastapi import APIRouter, Body
from fastapi.responses import FileResponse
from depends import apartment_service
from schema.apartment import ApartType, MatchingSchema
from service.alghorithm import match_new_apart_to_family_batch
from service.balance_alghorithm import save_views_to_excel
import os 

router = APIRouter(prefix="/fisrt_matching", tags=["Первичный подбор"])

# Получение списка адресов домов
@router.get("/family_structure/house_addresses")
async def get_family_structure_house_addresses():
    return await apartment_service.get_house_address_with_room_count(apart_type=ApartType.OLD)

# Получение списка адресов домов
@router.get("/new_apartment/house_addresses")
async def get_new_apartment_house_addresses():
    return await apartment_service.get_house_address_with_room_count(apart_type=ApartType.NEW)

@router.post('/matching')
async def start_matching(
    requirements: MatchingSchema 
):
    result = None 
    try:
        match_new_apart_to_family_batch(new_selected_districts=requirements.new_apartment_district,
                                        old_selected_districts=requirements.family_structure_municipal_district,
                                        new_selected_areas=requirements.family_structure_municipal_district,
                                        old_selected_areas=requirements.family_structure_municipal_district,
                                        new_selected_addresses=requirements.new_apartment_house_address,
                                        old_selected_addresses=requirements.family_structure_house_address)
        result = 'ok'
    except Exception as e: 
        result = e 
    return {"message": result}

@router.post('/balance')
async def balance(
    requirements: MatchingSchema = Body(...)
):
    try:
        # Формируем путь для сохранения файла
        output_path = os.path.join(os.getcwd(), 'uploads', 'matching_result.xlsx')

        # Сохраняем файл (здесь вызывается ваша функция)
        save_views_to_excel(
            output_path=output_path,
            new_selected_districts=requirements.new_apartment_district,
            old_selected_districts=requirements.family_structure_municipal_district,
            new_selected_areas=requirements.family_structure_municipal_district,
            old_selected_areas=requirements.family_structure_municipal_district,
            new_selected_addresses=requirements.new_apartment_house_address,
            old_selected_addresses=requirements.family_structure_house_address)

        # Возвращаем файл клиенту
        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='matching_result.xlsx'
        )
    except Exception as e:
        return {"error": str(e)}