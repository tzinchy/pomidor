import pandas as pd
import json
import psycopg2
from app.core.config import settings

# Определяем категории статусов
STATUS_CATEGORIES = {
    "согласие": 1,
    "подобрано": 7,
    "подобрано (ждет одобрения)": 6,
    "ожидание": 6,
    "отказ": 2,
    "архивный отказ": 2,
    "не подобрано": 8,
    "подборов не будет": 14,
    "суд": 3,
    "фонд компенсация": 4,
    "фонд докупка": 5,
    "мфр (вне района)": 9,
    "мфр компенсация (вне района)": 10,
    "свободная": 11,
    "резерв": 12,
    "блок": 13,
    "передано во вне": 15
}

def prepare_data(df: pd.DataFrame, new_apart_df: pd.DataFrame) -> pd.DataFrame:
    """Подготовка и очистка данных с заменой new_apart_id"""
    # Приводим статусы к строковому типу и нижнему регистру
    df['Результат предложения'] = df['Результат предложения'].astype(str).str.strip().str.lower()
    
    # Переименование колонок
    rename_map = {
        "Код субъекта": "subject_id",
        "Идентификатор дела": "affair_id",
        "Исх. № предложения": "outgoing_offer_number",
        "Дата предложения": "outcoming_date",
        "Претензия": "claim",
        "Примечание": "notes",
        "Сл.инф_APART_ID": "original_apart_id",
        "Кадастровый номер": "cad_num",
        "Сл.инф_UNOM": "unom",
        "Сл.инф_UNKV": "un_kv"
    }
    
    # Применяем переименование только для существующих колонок
    rename_map = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=rename_map)
    
    # Преобразование типов
    numeric_cols = ['subject_id', 'affair_id', 'original_apart_id', 'unom']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'outcoming_date' in df.columns:
        df['outcoming_date'] = pd.to_datetime(df['outcoming_date'], errors='coerce')
    
    # Заменяем original_apart_id на корректные new_apart_id из справочника
    def find_correct_apart_id(row):
        # Ищем по кадастровому номеру
        if 'cad_num' in row and pd.notna(row['cad_num']):
            match = new_apart_df[new_apart_df['cad_num'] == row['cad_num']]
            if not match.empty:
                return match.iloc[0]['new_apart_id']
        
        # Ищем по unom и un_kv
        if 'unom' in row and 'un_kv' in row and pd.notna(row['unom']) and pd.notna(row['un_kv']):
            match = new_apart_df[(new_apart_df['unom'] == row['unom']) & 
                               (new_apart_df['un_kv'] == row['un_kv'])]
            if not match.empty:
                return match.iloc[0]['new_apart_id']
        
        # Если ничего не нашли, оставляем original_apart_id
        return row['original_apart_id'] if 'original_apart_id' in row else None
    
    df['new_apart_id'] = df.apply(find_correct_apart_id, axis=1)
    
    # Удаление некорректных данных
    required_cols = [col for col in ['affair_id', 'subject_id', 'new_apart_id'] if col in df.columns]
    df = df.dropna(subset=required_cols)
    return df

def get_new_apart_data(conn):
    """Получаем справочник квартир из БД"""
    query = "SELECT new_apart_id, cad_num, unom, un_kv FROM new_apart"
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Ошибка при загрузке данных квартир: {str(e)}")
        return pd.DataFrame(columns=['new_apart_id', 'cad_num', 'unom', 'un_kv'])

def create_offer_structure(df: pd.DataFrame, conn) -> pd.DataFrame:
    """Создаем структуру для вставки в таблицу offer"""
    result_records = []
    
    # Проверяем наличие необходимых колонок
    if 'Результат предложения' not in df.columns:
        raise ValueError("Отсутствует обязательная колонка 'Результат предложения'")
    
    # Преобразуем статусы в строки
    df['Результат предложения'] = df['Результат предложения'].astype(str).str.strip().str.lower()
    
    # Определяем многоподписные дела
    subject_counts = df.groupby('affair_id')['subject_id'].nunique()
    multi_subject_affairs = set(subject_counts[subject_counts > 1].index)
    single_subject_affairs = set(subject_counts[subject_counts == 1].index)
    
    # Создаем словарь для хранения согласованных квартир
    approved_apartments = {}
    
    # Обрабатываем многоподписные дела
    for affair_id in multi_subject_affairs:
        affair_df = df[df['affair_id'] == affair_id]
        
        if 'outcoming_date' in df.columns:
            grouped = affair_df.groupby(['affair_id', 'outcoming_date'])
        else:
            grouped = affair_df.groupby(['affair_id'])
        
        for group_key, group in grouped:
            if isinstance(group_key, tuple):
                affair_id, outcoming_date = group_key
            else:
                affair_id = group_key
                outcoming_date = None
            
            if affair_id not in approved_apartments:
                approved_apartments[affair_id] = {}
            
            new_aparts = {}
            for _, row in group.iterrows():
                try:
                    status_text = str(row['Результат предложения']).strip().lower()
                    status_id = int(STATUS_CATEGORIES.get(status_text, 7))
                except Exception as e:
                    print(f"Ошибка обработки статуса: {e}, значение: {row['Результат предложения']}")
                    status_id =int(7)  # Статус по умолчанию
                
                entry = {
                    'status_id': status_id,
                    'outcoming_date': outcoming_date.strftime('%Y-%m-%d') 
                    if pd.notnull(outcoming_date) else None
                }
                
                new_aparts[str(row['new_apart_id'])] = entry
                
                if status_id == 1:  # Согласие
                    approved_apartments[affair_id][str(row['new_apart_id'])] = entry
            
            # Добавляем все согласованные квартиры для этого дела
            for apart_id, apart_data in approved_apartments.get(affair_id, {}).items():
                if apart_id not in new_aparts:
                    new_aparts[apart_id] = apart_data
            
            record = {
                'affair_id': affair_id,
                'outcoming_date': outcoming_date,
                'outgoing_offer_number': str(group['outgoing_offer_number'].iloc[0]) if 'outgoing_offer_number' in group.columns else None,
                'new_aparts': json.dumps(new_aparts, ensure_ascii=False),
                'subject_count': int(subject_counts[affair_id]),
                'original_apart_id': int(group['original_apart_id'].iloc[0]) if 'original_apart_id' in group.columns else None,
                'corrected_apart_id': int(group['new_apart_id'].iloc[0]) if 'new_apart_id' in group.columns else None,
                'cad_num': str(group['cad_num'].iloc[0]) if 'cad_num' in group.columns and pd.notna(group['cad_num'].iloc[0]) else None,
                'unom': int(group['unom'].iloc[0]) if 'unom' in group.columns and pd.notna(group['unom'].iloc[0]) else None,
                'un_kv': str(group['un_kv'].iloc[0]) if 'un_kv' in group.columns and pd.notna(group['un_kv'].iloc[0]) else None,
                'affair_type': 'Многоподписной'
            }
            result_records.append(record)
    
    # Обрабатываем одноподписные дела
    for affair_id in single_subject_affairs:
        affair_df = df[df['affair_id'] == affair_id]
        for _, row in affair_df.iterrows():
            try:
                status_text = str(row['Результат предложения']).strip().lower()
                status_id = STATUS_CATEGORIES.get(status_text, 6)
            except Exception as e:
                print(f"Ошибка обработки статуса: {e}, значение: {row['Результат предложения']}")
                status_id = 6  # Статус по умолчанию
            
            new_aparts = {
                str(row['new_apart_id']): {
                    'status_id': status_id,
                    'outcoming_date': row['outcoming_date'].strftime('%Y-%m-%d') 
                    if 'outcoming_date' in row and pd.notna(row['outcoming_date']) else None
                }
            }
            
            record = {
                'affair_id': affair_id,
                'outcoming_date': row['outcoming_date'] if 'outcoming_date' in row else None,
                'outgoing_offer_number': str(row['outgoing_offer_number']) if 'outgoing_offer_number' in row else None,
                'new_aparts': json.dumps(new_aparts, ensure_ascii=False),
                'subject_count': 1,
                'original_apart_id': int(row['original_apart_id']) if 'original_apart_id' in row else None,
                'corrected_apart_id': int(row['new_apart_id']) if 'new_apart_id' in row else None,
                'cad_num': str(row['cad_num']) if 'cad_num' in row and pd.notna(row['cad_num']) else None,
                'unom': int(row['unom']) if 'unom' in row and pd.notna(row['unom']) else None,
                'un_kv': str(row['un_kv']) if 'un_kv' in row and pd.notna(row['un_kv']) else None,
                'affair_type': 'Одноподписной'
            }
            result_records.append(record)
    
    return pd.DataFrame(result_records)

def process_offers_data(input_file):
    """Основной процесс обработки данных"""
    conn = None
    try:
        # Устанавливаем соединение с БД
        conn = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME,
        )
        
        # 1. Загружаем справочник квартир
        new_apart_df = get_new_apart_data(conn)
        
        # 2. Загрузка и подготовка данных
        df = pd.read_excel(input_file)
        print("Загружены столбцы:", df.columns.tolist())  # Для отладки
        
        # Сортируем по ID, если такой столбец есть
        if 'ID' in df.columns:
            df = df.sort_values('ID')
        
        df = prepare_data(df, new_apart_df)
        print("Данные успешно подготовлены")
        
        # 3. Создаем структуру для всех дел
        offers_df = create_offer_structure(df, conn)
        
        # 4. Сохраняем результат в Excel
        with pd.ExcelWriter('processed_offers.xlsx', engine='xlsxwriter') as writer:
            # Все данные на одном листе с пометками
            offers_df['affair_type'] = offers_df['subject_count'].apply(
                lambda x: 'Многоподписной' if x > 1 else 'Одноподписной'
            )
            
            # Сортируем: сначала многоподписные, затем одноподписные
            sort_cols = ['affair_type', 'affair_id']
            if 'outcoming_date' in offers_df.columns:
                sort_cols.append('outcoming_date')

            
            # Преобразуем даты в строки только для вывода в Excel
            excel_df = offers_df.copy()
            if 'outcoming_date' in excel_df.columns:
                excel_df['outcoming_date'] = excel_df['outcoming_date'].dt.strftime('%Y-%m-%d')
            excel_df.to_excel(writer, sheet_name='Все подборы', index=False)
            
            # Создаем сводную таблицу (упрощенную)
            pivot_cols = ['subject_count']
            if 'outcoming_date' in offers_df.columns:
                pivot_cols.extend([
                    ('outcoming_date', 'count'),
                    ('outcoming_date', lambda x: x.min().strftime('%Y-%m-%d')),
                    ('outcoming_date', lambda x: x.max().strftime('%Y-%m-%d'))
                ])
            
            pivot = offers_df.groupby('affair_id').agg({
                'subject_count': 'first',
                **({'outcoming_date': ['count', lambda x: x.min().strftime('%Y-%m-%d'),
                                    lambda x: x.max().strftime('%Y-%m-%d')]} 
                  if 'outcoming_date' in offers_df.columns else {})
            })
            
            pivot.columns = ['subject_count'] + (['offer_count', 'first_offer_date', 'last_offer_date'] 
                                              if 'outcoming_date' in offers_df.columns else [])
            pivot.reset_index(inplace=True)
            pivot.to_excel(writer, sheet_name='Сводка', index=False)
            
    except Exception as e:
        print(f"Ошибка обработки данных: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()
        print("Обработка завершена. Результаты сохранены в processed_offers.xlsx")

if __name__ == "__main__":
    input_file = '2025.06.02 Подбор квартир (полный).xlsx'
    process_offers_data(input_file)