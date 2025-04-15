def process_stages(data):
    """
    Обрабатывает данные этапов, собирает старые и новые адреса в отдельные массивы
    и выводит их в консоль.
    
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
    old_addresses = []
    new_addresses = []
    
    # Собираем все старые адреса
    for key in sorted(data.keys()):
        if key.startswith('old_apartment_house_address_'):
            addresses = data[key]
            if isinstance(addresses, list):
                old_addresses.extend(addresses)
            else:
                old_addresses.append(addresses)
    
    # Собираем все новые адреса
    for key in sorted(data.keys()):
        if key.startswith('new_apartment_house_address_'):
            addresses = data[key]
            if isinstance(addresses, list):
                new_addresses.extend(addresses)
            else:
                new_addresses.append(addresses)
    
    # Выводим результаты
    print("\n=== Все старые адреса ===")
    print(old_addresses)
    
    print("\n=== Все новые адреса ===")
    print(new_addresses)
    
    print(f"\nИтого: {len(old_addresses)} старых адресов и {len(new_addresses)} новых адресов")


# Пример использования
if __name__ == "__main__":
    # Тестовые данные
    test_data = {
        'old_apartment_house_address_1': ['ул. Ленина, 10'],
        'new_apartment_house_address_1': ['ул. Пушкина, 15'],
        'old_apartment_house_address_2': ['ул. Гагарина, 20', 'ул. Советская, 5'],
        'new_apartment_house_address_2': ['ул. Садовая, 3'],
        'some_other_data': ['Дополнительные данные']
    }
    
    process_stages(test_data)