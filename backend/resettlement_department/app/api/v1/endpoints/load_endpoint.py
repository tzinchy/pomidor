from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO

router = APIRouter()

@router.post("/upload-file/")
async def upload_excel_file(file: UploadFile = File(...)):
    """
    Загрузка и проверка Excel файла.
    """
   
    if file.content_type not in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files (.xls, .xlsx) are allowed.")
    
    try:
        contents = await file.read()
        excel_data = pd.read_excel(BytesIO(contents)) 
        return {
            "filename": file.filename,
            "message": "File successfully uploaded and verified as Excel.",
            "columns": list(excel_data.columns) 
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing the Excel file: {str(e)}")
