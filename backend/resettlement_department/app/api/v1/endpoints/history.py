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

        output_path = os.path.join(os.getcwd(), '././uploads', 'matching_result.xlsx')

        save_views_to_excel(
            output_path=output_path,
            new_selected_addresses=requirements.new_apartment_house_address,
            old_selected_addresses=requirements.family_structure_house_address,
            date=requirements.is_date)

        return FileResponse(
            path=output_path,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename='matching_result.xlsx'
        )
    except Exception as e:
        return {"error": str(e)}