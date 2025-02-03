from fastapi import APIRouter, Body
from fastapi.responses import FileResponse
from depends import history_service
from schema.history import HistoryResponse
from typing import List
from service.balance_alghorithm import save_views_to_excel
from schema.apartment import MatchingSchema
import os 

router = APIRouter(tags=['history'])

@router.get('/history', response_model=List[HistoryResponse])
async def get_history():
    return await history_service.get_history()

@router.patch('/approve/{history_id}')
async def approve_history(history_id : int): 
    return await history_service.approve_history(history_id)

@router.delete('/delete/{history_id}')
async def cancell_history(history_id : int):
    return await history_service.cancell_history(history_id)

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
            old_selected_addresses=requirements.family_structure_house_address,
            date=requirements.is_date)

        # Возвращаем файл клиенту
        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='matching_result.xlsx'
        )
    except Exception as e:
        return {"error": str(e)}