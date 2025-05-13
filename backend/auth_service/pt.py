import pandas as pd

# Вариант 1: Если данные в Excel-файле (пропускаем первую строку)
df = pd.read_excel('/Users/macbook/Downloads/Telegram Desktop/2025-05-07_Квартирография_ТЗ_ОПР.xlsx', sheet_name='Лист1', skiprows=1)

# Вариант 2: Если данные в буфере обмена (скопированы из Excel)
# df = pd.read_clipboard(skiprows=1)

# Размножаем строки согласно колонке "Количество штук"
expanded_rows = []
for _, row in df.iterrows():
    count = row['Количество\nштук']  # или row['Количество штук'], если название без \n
    for _ in range(count):
        expanded_rows.append(row)

expanded_df = pd.DataFrame(expanded_rows)

# Сохраняем в новый Excel-файл
expanded_df.to_excel('output.xlsx', index=False, sheet_name='Лист1')

print("Готово! Результат сохранён в output.xlsx")