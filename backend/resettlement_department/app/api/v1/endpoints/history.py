from fastapi import APIRouter
from depends import history_service

router = APIRouter(tags=['history'])

@router.get('/history')
async def get_history():
    return await history_service.get_history()

@router.patch('/approve/{history_id}')
async def post_approve(history_id : int): 
    return 
'''
@router.post('/download/{history_id}')
async def balance(
    history_id : int
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
'''