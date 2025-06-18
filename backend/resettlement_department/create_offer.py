import pandas as pd
import json
import psycopg2
from app.core.config import settings

# Категории статусов с правильными сопоставлениями
STATUS_CATEGORIES = {
    "согласие": 1,
    "подобрано": 7,
    "подобрано (ждет одобрения)": 7,
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
    # Приводим статусы к нижнему регистру
    if 'Результат предложения' in df.columns:
        df['Результат предложения'] = df['Результат предложения'].str.strip().str.lower()
    
    # Переименование колонок с учетом фактических названий в файле
    rename_map = {
        "ID": "offer_id",
        "Код субъекта": "subject_id",
        "Идентификатор дела": "affair_id",
        "Исх. № предложения": "outgoing_offer_number",
        "Дата предложения": "outcoming_date",
        "Сл.инф_APART_ID": "original_apart_id",
        "Кадастровый номер": "cad_num",
        "Сл.инф_UNOM": "unom",
        "Сл.инф_UNKV": "un_kv"
    }
    
    # Применяем только те переименования, для которых есть столбцы
    rename_columns = {k: v for k, v in rename_map.items() if k in df.columns}
    df = df.rename(columns=rename_columns)
    
    # Добавляем отсутствующие обязательные столбцы
    required_columns = ['offer_id', 'subject_id', 'affair_id', 'original_apart_id', 'new_apart_id']
    for col in required_columns:
        if col not in df.columns:
            df[col] = None
    
    # Преобразование типов данных
    numeric_cols = ['offer_id', 'subject_id', 'affair_id', 'original_apart_id', 'unom']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'outcoming_date' in df.columns:
        df['outcoming_date'] = pd.to_datetime(df['outcoming_date'], errors='coerce')
    
    # Замена original_apart_id на корректные new_apart_id из справочника
    def find_correct_apart_id(row):
        # Поиск по кадастровому номеру
        if pd.notna(row.get('cad_num')):
            match = new_apart_df[new_apart_df['cad_num'] == row['cad_num']]
            if not match.empty:
                return match.iloc[0]['new_apart_id']
        
        # Поиск по unom и un_kv
        if pd.notna(row.get('unom')) and pd.notna(row.get('un_kv')):
            match = new_apart_df[
                (new_apart_df['unom'] == row['unom']) & 
                (new_apart_df['un_kv'] == row['un_kv'])
            ]
            if not match.empty:
                return match.iloc[0]['new_apart_id']
        
        # Возвращаем original_apart_id, если не нашли совпадений
        return row['original_apart_id']
    
    df['new_apart_id'] = df.apply(find_correct_apart_id, axis=1)
    
    # Удаление строк с некорректными данными
    required_values = ['affair_id', 'subject_id', 'new_apart_id']
    df = df.dropna(subset=required_values)
    
    return df

def get_new_apart_data(conn):
    """Получаем справочник квартир из БД"""
    query = """
    SELECT 
        new_apart_id, 
        cad_num, 
        unom, 
        un_kv 
    FROM new_apart
    """
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        print(f"Ошибка при загрузке данных о квартирах: {str(e)}")
        return pd.DataFrame(columns=['new_apart_id', 'cad_num', 'unom', 'un_kv'])

def create_offer_structure(df: pd.DataFrame) -> pd.DataFrame:
    """Создаем структуру для вставки в таблицу offer"""
    if df.empty:
        return pd.DataFrame()
    
    # Проверяем наличие обязательных столбцов
    if 'Результат предложения' not in df.columns:
        df['Результат предложения'] = 'ожидание'
    
    # Сортируем данные
    sort_columns = ['affair_id', 'offer_id']
    df = df.sort_values(sort_columns)
    
    # Группируем дела по количеству субъектов
    subject_counts = df.groupby('affair_id')['subject_id'].nunique()
    multi_subject_affairs = subject_counts[subject_counts > 1].index
    single_subject_affairs = subject_counts[subject_counts == 1].index
    
    result_records = []
    approved_apartments = {}  # Для хранения согласованных квартир
    
    # Обработка многоподписных дел
    for affair_id in multi_subject_affairs:
        affair_df = df[df['affair_id'] == affair_id]
        
        for _, group in affair_df.groupby(['affair_id', 'outcoming_date']):
            new_aparts = {}
            
            for _, row in group.iterrows():
                status_text = row['Результат предложения'].lower().strip()
                status_id = STATUS_CATEGORIES.get(status_text, 6)
                
                apartment_data = {
                    'offer_id': int(row['offer_id']),
                    'status_id': status_id,
                    'outcoming_date': row['outcoming_date'].strftime('%Y-%m-%d') 
                        if pd.notna(row['outcoming_date']) else None,
                    'original_apart_id': int(row['original_apart_id']) 
                        if pd.notna(row['original_apart_id']) else None
                }
                
                new_aparts[str(row['new_apart_id'])] = apartment_data
                
                # Запоминаем согласованные квартиры
                if status_id == 1:
                    if affair_id not in approved_apartments:
                        approved_apartments[affair_id] = {}
                    approved_apartments[affair_id][str(row['new_apart_id'])] = apartment_data
            
            # Добавляем согласованные квартиры из предыдущих предложений
            if affair_id in approved_apartments:
                for apart_id, data in approved_apartments[affair_id].items():
                    if apart_id not in new_aparts:
                        new_aparts[apart_id] = data
            
            record = {
                'offer_id': int(group['offer_id'].iloc[0]),
                'affair_id': affair_id,
                'outcoming_date': group['outcoming_date'].iloc[0],
                'outgoing_offer_number': str(group['outgoing_offer_number'].iloc[0]) 
                    if 'outgoing_offer_number' in group.columns else None,
                'new_aparts': json.dumps(new_aparts, ensure_ascii=False),
                'subject_count': int(subject_counts[affair_id]),
                'original_apart_id': int(group['original_apart_id'].iloc[0]) 
                    if 'original_apart_id' in group.columns else None,
                'corrected_apart_id': int(group['new_apart_id'].iloc[0]),
                'cad_num': str(group['cad_num'].iloc[0]) 
                    if 'cad_num' in group.columns and pd.notna(group['cad_num'].iloc[0]) else None,
                'unom': int(group['unom'].iloc[0]) 
                    if 'unom' in group.columns and pd.notna(group['unom'].iloc[0]) else None,
                'un_kv': str(group['un_kv'].iloc[0]) 
                    if 'un_kv' in group.columns and pd.notna(group['un_kv'].iloc[0]) else None,
                'affair_type': 'Многоподписной'
            }
            result_records.append(record)
    
    # Обработка одноподписных дел
    for affair_id in single_subject_affairs:
        for _, row in df[df['affair_id'] == affair_id].iterrows():
            status_text = row['Результат предложения'].lower().strip()
            status_id = STATUS_CATEGORIES.get(status_text, 6)
            
            new_aparts = {
                str(row['new_apart_id']): {
                    'offer_id': int(row['offer_id']),
                    'status_id': status_id,
                    'outcoming_date': row['outcoming_date'].strftime('%Y-%m-%d')
                        if pd.notna(row['outcoming_date']) else None,
                    'original_apart_id': int(row['original_apart_id'])
                        if pd.notna(row['original_apart_id']) else None
                }
            }
            
            record = {
                'offer_id': int(row['offer_id']),
                'affair_id': affair_id,
                'outcoming_date': row['outcoming_date'],
                'outgoing_offer_number': str(row['outgoing_offer_number']) 
                    if 'outgoing_offer_number' in row else None,
                'new_aparts': json.dumps(new_aparts, ensure_ascii=False),
                'subject_count': 1,
                'original_apart_id': int(row['original_apart_id']) 
                    if 'original_apart_id' in row else None,
                'corrected_apart_id': int(row['new_apart_id']),
                'cad_num': str(row['cad_num']) 
                    if 'cad_num' in row and pd.notna(row['cad_num']) else None,
                'unom': int(row['unom']) 
                    if 'unom' in row and pd.notna(row['unom']) else None,
                'un_kv': str(row['un_kv']) 
                    if 'un_kv' in row and pd.notna(row['un_kv']) else None,
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
        print("Столбцы в загруженном файле:", df.columns.tolist())
        df = prepare_data(df, new_apart_df)
        
        # 3. Создаем структуру для всех дел
        offers_df = create_offer_structure(df)
        
        # 4. Сохраняем результат в Excel
        if not offers_df.empty:
            with pd.ExcelWriter('processed_offers.xlsx', engine='xlsxwriter') as writer:
                # Добавляем тип дела
                offers_df['affair_type'] = offers_df['subject_count'].apply(
                    lambda x: 'Многоподписной' if x > 1 else 'Одноподписной'
                )
                
                # Сортировка
                sort_cols = ['affair_id', 'offer_id']
                if 'offer_id' in offers_df.columns:
                    sort_cols.append('offer_id')
                offers_df = offers_df.sort_values(sort_cols)
                
                # Форматирование дат для Excel
                excel_df = offers_df.copy()
                excel_df['outcoming_date'] = excel_df['outcoming_date'].dt.strftime('%Y-%m-%d')
                
                # Сохраняем все предложения
                excel_df.to_excel(writer, sheet_name='Все подборы', index=False)
                
                # Создаем сводную таблицу
                pivot = offers_df.groupby('affair_id').agg({
                    'subject_count': 'first',
                    'outcoming_date': ['count', 'min', 'max']
                })
                pivot.columns = ['subject_count', 'offer_count', 'first_offer_date', 'last_offer_date']
                pivot.reset_index(inplace=True)
                
                # Форматирование дат в сводной таблице
                pivot['first_offer_date'] = pivot['first_offer_date'].dt.strftime('%Y-%m-%d')
                pivot['last_offer_date'] = pivot['last_offer_date'].dt.strftime('%Y-%m-%d')
                pivot.to_excel(writer, sheet_name='Сводка', index=False)
        else:
            print("Нет данных для сохранения")
            
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