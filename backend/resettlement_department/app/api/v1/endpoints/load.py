from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from service.apartment_insert import insert_data_to_needs, insert_offer, insert_data_to_structure, new_apart_insert
from service.validation_service import ValidationService

router = APIRouter(prefix="/load", tags=["Загрузка файлов"])
'''
@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Универсальный endpoint для загрузки Excel-файлов.
    """
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    try:
        content = await file.read()
        df = pd.read_excel(BytesIO(content))
        print("Полученные столбцы:", df.columns)

        functions = [insert_data_to_needs, insert_offer, insert_data_to_structure, new_apart_insert]
        errors = ValidationService.validate_etl(df, functions)

        if errors:
            return {"status": "partial_success", "errors": errors}

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
'''
