def process_stages(data):
    """
    Обрабатывает данные этапов и выводит их в консоль в правильном порядке
    
    Args:
        data (dict): Словарь с данными этапов в формате:
            {
                'old_apartment_house_address_1': [...],
                'new_apartment_house_address_1': [...],
                'old_apartment_house_address_2': [...],
                'new_apartment_house_address_2': [...],
                ...
            }
    """
    # Извлекаем все уникальные номера этапов
    stage_numbers = set()
    for key in data.keys():
        if 'old_apartment' in key or 'new_apartment' in key:
            # Извлекаем номер из ключа (последнее число в строке)
            stage_num = int(key.split('_')[-1])
            stage_numbers.add(stage_num)
    
    # Сортируем номера этапов
    sorted_stages = sorted(stage_numbers)
    
    # Выводим данные по каждому этапу
    for stage_num in sorted_stages:
        old_key = f'old_apartment_house_address_{stage_num}'
        new_key = f'new_apartment_house_address_{stage_num}'
        
        print(f"\n=== Этап {stage_num} ===")
        print(f"Старый дом ({old_key}): {data.get(old_key, 'Нет данных')}")
        print(f"Новый дом ({new_key}): {data.get(new_key, 'Нет данных')}")
    
    print("\nОбработка завершена!")


# Пример использования
if __name__ == "__main__":
    # Тестовые данные (такие же как в вашем примере)
    test_data = {
        'old_apartment_house_address_1': ['Данные старого дома 1'],
        'new_apartment_house_address_1': ['Данные нового дома 1'],
        'old_apartment_house_address_2': ['Данные старого дома 2'],
        'new_apartment_house_address_2': ['Данные нового дома 2']
    }
    
    process_stages(test_data)