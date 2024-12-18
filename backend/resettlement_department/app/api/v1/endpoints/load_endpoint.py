from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from io import BytesIO
from utils.apartment_insert import insert_data_to_needs, insert_offer, insert_data_to_structure, new_apart_insert

router = APIRouter()

@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Универсальный endpoint для загрузки Excel-файлов.
    Структура данных определяется по столбцам.
    """
    # Проверка типа файла
    if file.content_type not in [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    ]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only Excel files are allowed.")

    functions = [insert_data_to_needs, insert_offer, insert_data_to_structure, new_apart_insert]
    errors = []  # Для сбора ошибок

    try:
        # Чтение данных из Excel
        content = await file.read()
        df = pd.read_excel(BytesIO(content))

        # Лог столбцов для отладки
        print("Полученные столбцы:", df.columns)

        for function in functions:
            # Определение необходимых столбцов для каждой функции
            if function == insert_offer:
                required_columns = {'ID', 'SentenceDate', 'GiveDate', 'Registry', 'AnswerDate', 
                                    'SentenceNumber', 'SelectionAction', 'Conditions', 'Notes', 
                                    'Claim', 'SubjectID', 'ObjectID', 'Result'}
            elif function == insert_data_to_needs:
                required_columns = {'affair_id', 'CountBusiness_x', 'ID'}
            elif function == insert_data_to_structure:
                required_columns = {'ID', 'КПУ_Дело_№ полный(новый)', 'КПУ_Заявитель_Фамилия'}
            elif function == new_apart_insert:
                required_columns = {'Сл.инф_APART_ID', 'Сл.инф_UNOM', 'Адрес_Округ'}

            # Проверка наличия необходимых столбцов в DataFrame
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                errors.append(
                    f"Missing required columns for {function.__name__}: {missing_columns}"
                )
                continue  # Пропускаем эту функцию и идем к следующей

            try:
                # Вызов функции обработки
                result = function(df)
                if isinstance(result, Exception):
                    errors.append(f"Error in {function.__name__}: {str(result)}")
            except Exception as e:
                errors.append(f"Unhandled exception in {function.__name__}: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    # Если есть ошибки, возвращаем их, но не прерываем выполнение
    if errors:
        return {"status": "partial_success", "errors": errors}

    return {"status": "success"}
