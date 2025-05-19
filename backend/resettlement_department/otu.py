import pandas as pd

# Загрузка данных из Excel
df = pd.read_excel('/Users/macbook/Downloads/Telegram Desktop/Копия_2025_05_12_Квартирография_ТЗ_ОПР_на_согл_ДГИ (4).xlsx', sheet_name='Лист1')

# Выводим реальные названия столбцов для проверки
print("Фактические названия столбцов:")
print(df.columns.tolist())

# Переименование столбцов с учетом реальных названий
column_mapping = {
    'Кол-во комн': 'rooms',
    'Тип': 'type',
    'Секция': 'section',
    'Площадь жилая,\n м.кв': 'living_area',
    'Площадь квартир\n(без учета летних помещений)': 'apartment_area',
    'Площадь\nMAX, м.кв\n(с учетом летних помещений - лоджия с коэф. 0,5)': 'max_area',
    'Количество\nштук': 'quantity'
}
df = df.rename(columns=column_mapping)

# Преобразование числовых столбцов (замена запятых на точки для десятичных чисел)
numeric_cols = ['living_area', 'apartment_area', 'max_area', 'quantity']
for col in numeric_cols:
    # Сначала преобразуем в строку, затем заменяем запятые, затем в число
    df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

# Удаление строк с пропущенными значениями
df = df.dropna()

# Дублирование строк согласно количеству
result_rows = []
for _, row in df.iterrows():
    count = int(row['quantity'])
    for _ in range(count):
        result_rows.append(row.to_dict())

# Создание результирующего DataFrame
result = pd.DataFrame(result_rows)

# Удаление столбца с количеством
result = result.drop(columns=['quantity'])

# Сохранение результата
output_file = 'результат_обработки.xlsx'
result.to_excel(output_file, index=False)

# Формирование отчета
original_count = len(df)
result_count = len(result)
summary = pd.DataFrame({
    'Показатель': ['Исходное количество строк', 'Количество после дублирования'],
    'Значение': [original_count, result_count]
})

# Сохранение отчета в тот же файл на отдельный лист
with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
    summary.to_excel(writer, sheet_name='Отчет', index=False)

print(f"Обработка завершена. Результат сохранен в файл: '{output_file}'")
print(f"Исходных строк: {original_count}, Результирующих строк: {result_count}")