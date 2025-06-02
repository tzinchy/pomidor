import pandas as pd
import json
from tqdm import tqdm
import psycopg2
from psycopg2 import errors
from app.core.config import settings

# Определяем категории статусов
STATUS_CATEGORIES = {
    "согласие": 1,
    "подобрано": 1,
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
    df['Состояние'] = df['Состояние'].str.strip().str.lower()
    
    # Переименование колонок
    df = df.rename(columns={
        "Код субъекта": "subject_id",
        "Идентификатор дела": "affair_id",
        "Исх. № предложения": "outgoing_offer_number",
        "Дата предложения": "outcoming_date",
        "Претензия": "claim",
        "Примечание": "notes",
        "Сл.инф_APART_ID": "original_apart_id",
        "Кадастровй номер": "cad_num",
        "Сл.инф_UNOM": "unom",
        "Сл.инф_UNKV": "un_kv"
    })
    
    # Преобразование типов
    df['subject_id'] = pd.to_numeric(df['subject_id'], errors='coerce')
    df['affair_id'] = pd.to_numeric(df['affair_id'], errors='coerce')
    df['original_apart_id'] = pd.to_numeric(df['original_apart_id'], errors='coerce')
    df['outcoming_date'] = pd.to_datetime(df['outcoming_date'], errors='coerce')
    df['unom'] = pd.to_numeric(df['unom'], errors='coerce')
    
    # Заменяем original_apart_id на корректные new_apart_id из справочника
    def find_correct_apart_id(row):
        # Ищем по кадастровому номеру
        if pd.notna(row['cad_num']):
            match = new_apart_df[new_apart_df['cad_num'] == row['cad_num']]
            if not match.empty:
                return match.iloc[0]['new_apart_id']
        
        # Ищем по unom и un_kv
        if pd.notna(row['unom']) and pd.notna(row['un_kv']):
            match = new_apart_df[(new_apart_df['unom'] == row['unom']) & 
                                (new_apart_df['un_kv'] == row['un_kv'])]
            if not match.empty:
                return match.iloc[0]['new_apart_id']
        
        # Если ничего не нашли, оставляем original_apart_id
        return row['original_apart_id']
    
    df['new_apart_id'] = df.apply(find_correct_apart_id, axis=1)
    
    # Удаление некорректных данных
    df = df.dropna(subset=['affair_id', 'subject_id', 'new_apart_id'])
    return df

def get_new_apart_data(conn):
    """Получаем справочник квартир из БД"""
    query = "SELECT new_apart_id, cad_num, unom, un_kv FROM new_apart"
    # Используем psycopg2 напрямую вместо SQLAlchemy
    return pd.read_sql_query(query, conn)

def insert_decline_reason(claim: str, conn) -> int:
    """Вставляет причину отказа (claim) и возвращает ID"""
    if not claim or pd.isna(claim):
        return None
    
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                "INSERT INTO decline_reason (notes) VALUES (%s) RETURNING decline_reason_id;",
                (str(claim),))  # Приводим к строке на всякий случай
            decline_reason_id = cursor.fetchone()[0]
            conn.commit()
            return decline_reason_id
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при вставке причины отказа: {str(e)}")
            return None

def combine_notes(notes_series):
    """Объединяет заметки из нескольких строк, исключая дубликаты"""
    # Преобразуем все элементы в строки и удаляем NaN/None
    notes = [str(note) for note in notes_series.dropna().unique() if note is not None]
    if not notes:
        return None
    return "; ".join(notes)

def create_offer_structure(df: pd.DataFrame, conn) -> pd.DataFrame:
    """Создаем структуру для вставки в таблицу offer"""
    result_records = []
    
    # Сортируем данные по дате предложения
    df = df.sort_values(['affair_id', 'outcoming_date'])
    
    # Определяем многоподписные дела
    subject_counts = df.groupby('affair_id')['subject_id'].nunique()
    multi_subject_affairs = set(subject_counts[subject_counts > 1].index)
    single_subject_affairs = set(subject_counts[subject_counts == 1].index)
    
    # Создаем словарь для хранения согласованных квартир
    approved_apartments = {}
    
    # Обрабатываем многоподписные дела
    for affair_id in multi_subject_affairs:
        affair_df = df[df['affair_id'] == affair_id]
        grouped = affair_df.groupby(['affair_id', 'outcoming_date'])
        
        for (affair_id, outcoming_date), group in grouped:
            if affair_id not in approved_apartments:
                approved_apartments[affair_id] = {}
            
            new_aparts = {}
            for _, row in group.iterrows():
                status_text = row['Состояние'].lower().strip()
                status_id = STATUS_CATEGORIES.get(status_text, 6)
                
                entry = {
                    'status_id': status_id,
                    'outcoming_date': row['outcoming_date'].strftime('%Y-%m-%d') 
                    if pd.notna(row['outcoming_date']) else None
                }
                
                if status_id in [2, 8, 14] and pd.notna(row['claim']):
                    decline_reason_id = insert_decline_reason(str(row['claim']), conn)
                    if decline_reason_id:
                        entry['decline_reason_id'] = decline_reason_id
                
                new_aparts[str(row['new_apart_id'])] = entry
                
                if status_id == 1:  # Согласие
                    approved_apartments[affair_id][str(row['new_apart_id'])] = entry
            
            # Добавляем все согласованные квартиры для этого дела
            for apart_id, apart_data in approved_apartments.get(affair_id, {}).items():
                if apart_id not in new_aparts:
                    new_aparts[apart_id] = apart_data
            
            combined_notes = combine_notes(group['notes'])
            
            record = {
                'affair_id': affair_id,
                'outcoming_date': outcoming_date,  # Оставляем как datetime
                'outgoing_offer_number': str(group['outgoing_offer_number'].iloc[0]),
                'new_aparts': json.dumps(new_aparts, ensure_ascii=False),
                'subject_count': int(subject_counts[affair_id]),
                'original_apart_id': int(group['original_apart_id'].iloc[0]),
                'corrected_apart_id': int(group['new_apart_id'].iloc[0]),
                'cad_num': str(group['cad_num'].iloc[0]) if pd.notna(group['cad_num'].iloc[0]) else None,
                'unom': int(group['unom'].iloc[0]) if pd.notna(group['unom'].iloc[0]) else None,
                'un_kv': str(group['un_kv'].iloc[0]) if pd.notna(group['un_kv'].iloc[0]) else None,
                'notes': combined_notes,
                'affair_type': 'Многоподписной'
            }
            result_records.append(record)
    
    # Обрабатываем одноподписные дела
    for affair_id in single_subject_affairs:
        affair_df = df[df['affair_id'] == affair_id]
        for _, row in affair_df.iterrows():
            status_text = row['Состояние'].lower().strip()
            status_id = STATUS_CATEGORIES.get(status_text, 6)
            
            new_aparts = {
                str(row['new_apart_id']): {
                    'status_id': status_id,
                    'outcoming_date': row['outcoming_date'].strftime('%Y-%m-%d') 
                    if pd.notna(row['outcoming_date']) else None
                }
            }
            
            if pd.notna(row['claim']):
                decline_reason_id = insert_decline_reason(str(row['claim']), conn)
                if decline_reason_id:
                    new_aparts[str(row['new_apart_id'])]['decline_reason_id'] = decline_reason_id
            
            record = {
                'affair_id': affair_id,
                'outcoming_date': row['outcoming_date'],  # Оставляем как datetime
                'outgoing_offer_number': str(row['outgoing_offer_number']),
                'new_aparts': json.dumps(new_aparts, ensure_ascii=False),
                'subject_count': 1,
                'original_apart_id': int(row['original_apart_id']),
                'corrected_apart_id': int(row['new_apart_id']),
                'cad_num': str(row['cad_num']) if pd.notna(row['cad_num']) else None,
                'unom': int(row['unom']) if pd.notna(row['unom']) else None,
                'un_kv': str(row['un_kv']) if pd.notna(row['un_kv']) else None,
                'notes': str(row['notes']) if pd.notna(row['notes']) else None,
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
        df = prepare_data(df, new_apart_df)
        
        # 3. Создаем структуру для всех дел
        offers_df = create_offer_structure(df, conn)
        
        # 4. Сохраняем результат в Excel
        with pd.ExcelWriter('processed_offers.xlsx', engine='xlsxwriter') as writer:
            # Все данные на одном листе с пометками
            offers_df['affair_type'] = offers_df['subject_count'].apply(
                lambda x: 'Многоподписной' if x > 1 else 'Одноподписной'
            )
            
            # Сортируем: сначала многоподписные, затем одноподписные
            offers_df = offers_df.sort_values(['affair_type', 'affair_id', 'outcoming_date'],
                                            ascending=[False, True, True])
            
            # Преобразуем даты в строки только для вывода в Excel
            excel_df = offers_df.copy()
            excel_df['outcoming_date'] = excel_df['outcoming_date'].dt.strftime('%Y-%m-%d')
            excel_df.to_excel(writer, sheet_name='Все подборы', index=False)
            
            # Создаем сводную таблицу (упрощенную)
            pivot = offers_df.groupby('affair_id').agg({
                'subject_count': 'first',
                'outcoming_date': ['count', lambda x: x.min().strftime('%Y-%m-%d'),
                                 lambda x: x.max().strftime('%Y-%m-%d')]
            })
            pivot.columns = ['subject_count', 'offer_count', 'first_offer_date', 'last_offer_date']
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
    input_file = '/Users/macbook/Documents/1.xlsx'
    process_offers_data(input_file)