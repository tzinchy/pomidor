from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from utils.apartment_insert import insert_data_to_needs, insert_offer, insert_data_to_structure, new_apart_insert

router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Универсальный endpoint для загрузки файлов и их обработки.
    Названия файлов определяют тип обрабатываемых данных:
        - "structure" -> family_structure
        - "needs" -> family_apartment_needs
        - "new_apart" -> new_apart
        - "offer" -> offer
    """
    # Проверка типа файла
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel"
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    try:
        # Чтение Excel-файла в DataFrame
        content = await file.read()
        df = pd.read_excel(BytesIO(content))

        # Определяем функцию на основе имени файла
        filename = file.filename.lower()

        if "structure" in filename:
            result = insert_data_to_structure(df)
            return {"status": "success", "file": "structure", "details": result}

        elif "needs" in filename:
            result = insert_data_to_needs(df)
            return {"status": "success", "file": "needs", "details": result}

        elif "new_apart" in filename or "objects" in filename:
            result = new_apart_insert(df)
            return {"status": "success", "file": "new_apart", "details": result}

        elif "offer" in filename:
            result = insert_offer(df)
            return {"status": "success", "file": "offer", "details": result}

        else:
            raise HTTPException(status_code=400, detail="File name does not match expected types (structure, needs, new_apart, offer).")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")