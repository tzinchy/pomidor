import pandas as pd

# Загрузка данных из Excel файла
df = pd.read_excel('sndtvj5qm1.xlsx')  # укажите правильное имя файла

# Создание нового DataFrame с повторяющимися строками
new_df = df.loc[df.index.repeat(df['Количество штук'])].reset_index(drop=True)

# Сохранение результата в новый Excel файл (если нужно)
new_df.to_excel('результат.xlsx', index=False)

# Вывод результата (первые 20 строк для примера)
print(new_df.head(20))