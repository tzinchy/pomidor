from utils.apartment_insert import insert_data_to_needs, insert_offer, insert_data_to_structure, new_apart_insert
import pandas as pd

class ValidationService:
    @staticmethod
    def validate_etl(df: pd.DataFrame, functions):
        """
        Проверяет наличие необходимых столбцов в DataFrame для каждой функции из списка.
        
        :param df: DataFrame с данными из Excel
        :param functions: Список функций для обработки данных
        :return: Список ошибок, если такие есть
        """
        errors = []

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
            else:
                continue

            # Проверка наличия необходимых столбцов в DataFrame
            missing_columns = required_columns - set(df.columns)
            if missing_columns:
                errors.append(
                    f"Missing required columns for {function.__name__}: {missing_columns}"
                )
                continue

            try:
                # Вызов функции обработки
                result = function(df)
                if isinstance(result, Exception):
                    errors.append(f"Error in {function.__name__}: {str(result)}")
            except Exception as e:
                errors.append(f"Unhandled exception in {function.__name__}: {str(e)}")

        return errors