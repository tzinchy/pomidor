import psycopg2
import pandas as pd 
from core.config import Settings
from datetime import datetime

def get_db_connection():
    return psycopg2.connect(
        host=Settings.DB_HOST,
        port=Settings.DB_PORT,
        database=Settings.DB_NAME,
        user=Settings.DB_USER,
        password=Settings.DB_PASS,
    )


def match_new_apart_to_family_batch(start_date=None, end_date=None,
                                    new_selected_addresses=None, old_selected_addresses=None,
                                    new_selected_districts=None, old_selected_districts=None,
                                    new_selected_areas=None, old_selected_areas=None,
                                    date=False, ochered=False):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # --- Запросы к базе данных ---
                # Запрос для старых квартир
                family_query = """
                    SELECT 
                        family_apartment_needs.family_apartment_needs_id AS old_apart_id, 
                        family_structure.kpu_number,
                        family_structure.district, 
                        family_structure.municipal_district, 
                        family_structure.room_count, 
                        family_structure.full_living_area, 
                        family_structure.total_living_area, 
                        family_structure.living_area, 
                        family_structure.is_special_needs_marker, 
                        family_structure.min_floor, 
                        family_structure.max_floor, 
                        family_structure.buying_date,
                        ARRAY_AGG(EXTRACT(YEAR FROM AGE(family_member.date_of_birth))) AS ages,
                        COUNT(family_member.kpu_number) AS members_amount,
                        MAX(EXTRACT(YEAR FROM AGE(family_member.date_of_birth::timestamp with time zone))) AS oldest,
                        family_structure.is_queue,
                        family_structure.queue_square
                    FROM 
                        public.family_apartment_needs
                    LEFT JOIN 
                        public.family_structure USING (affair_id)
                    LEFT JOIN 
                        public.family_member ON family_structure.kpu_number = family_member.kpu_number 
                    WHERE 
                        family_apartment_needs.family_apartment_needs_id NOT IN (
                            SELECT old_apart_id 
                            FROM recommendation.offer
                        )
                """

                old_apart_query_params = []

                # Дополнительные фильтры
                if old_selected_addresses:
                    family_query += " AND family_structure.house_address IN %s"
                    old_apart_query_params.append(tuple(old_selected_addresses))

                if old_selected_districts:
                    family_query += " AND family_structure.district IN %s"
                    old_apart_query_params.append(tuple(old_selected_districts))

                if old_selected_areas:
                    family_query += " AND family_structure.municipal_district IN %s"
                    old_apart_query_params.append(tuple(old_selected_areas))

                if date:
                    family_query += " AND family_apartment_needs.created_at = (SELECT MAX(created_at) FROM public.family_apartment_needs)"

                # Добавляем секцию GROUP BY
                family_query += """
                    GROUP BY 
                        family_apartment_needs.family_apartment_needs_id, 
                        family_structure.kpu_number, 
                        family_structure.district, 
                        family_structure.municipal_district, 
                        family_structure.room_count, 
                        family_structure.full_living_area, 
                        family_structure.total_living_area, 
                        family_structure.living_area, 
                        family_structure.is_special_needs_marker, 
                        family_structure.min_floor, 
                        family_structure.max_floor, 
                        family_structure.buying_date, 
                        family_structure.is_queue, 
                        family_structure.queue_square
                    ORDER BY 
                        family_structure.room_count ASC, 
                        (family_structure.full_living_area + family_structure.living_area + (COUNT(family_member.kpu_number) / 3.9)) ASC, 
                        MAX(EXTRACT(YEAR FROM AGE(family_member.date_of_birth::timestamp with time zone))) DESC,
                        family_structure.living_area ASC,  
                        family_structure.full_living_area ASC, 
                        family_structure.total_living_area ASC;
                """

                # Выполнение запроса
                cursor.execute(family_query, old_apart_query_params)
                old_aparts = cursor.fetchall()

                if not old_aparts:
                    print("No old apartments found.")
                    return
                # Запрос для новых квартир
                new_apart_query = """
                    SELECT new_apart_id, district, municipal_district, house_address, apart_number, floor, room_count, full_living_area, total_living_area, living_area, special_needs_marker                
                    FROM public.new_apartment
                    WHERE new_apart_id NOT IN (SELECT new_apart_id FROM recommendation.offer)
                """

                new_apart_query_params = []

                if new_selected_addresses:
                    new_apart_query += " AND house_address IN %s"
                    new_apart_query_params.append(tuple(new_selected_addresses))

                if new_selected_districts:
                    new_apart_query += " AND district IN %s"
                    new_apart_query_params.append(tuple(new_selected_districts))

                if new_selected_areas:
                    new_apart_query += " AND municipal_district IN %s"
                    new_apart_query_params.append(tuple(new_selected_areas))

                if date:
                    new_apart_query += " AND created_at = (SELECT MAX(created_at) public.new_apart) "

                new_apart_query += " ORDER BY room_count ASC, (full_living_area + living_area), floor, living_area ASC, full_living_area ASC, total_living_area ASC"

                cursor.execute(new_apart_query, new_apart_query_params)
                new_aparts = cursor.fetchall()

                if not new_aparts:
                    print("No new apartments found.")
                    return

                # --- Создание DataFrame и расчет рангов ---
                df_old_apart = pd.DataFrame(old_aparts, columns=[
                    'old_apart_id', 'kpu_number', 'district', 'municipal_district', 'room_count', 'full_living_area',
                    'total_living_area', 'living_area', 'special_needs_marker', 'min_floor', 'max_floor', 'buying_date',
                    'ages', 'members_amount', 'oldest', 'is_queue', 'queue_square'
                ])

                df_new_apart = pd.DataFrame(new_aparts, columns=[
                    'new_apart_id', 'district', 'municipal_district', 'house_address', 'apart_number', 'floor',
                    'room_count', 'full_living_area', 'total_living_area', 'living_area', 'status_marker'
                ])

                df_new_apart_second = pd.DataFrame(new_aparts, columns=[
                    'new_apart_id', 'district', 'municipal_district', 'house_address', 'apart_number', 'floor',
                    'room_count', 'full_living_area', 'total_living_area', 'living_area', 'status_marker'
                ])

                # Создаем комбинированный столбец для старых и новых квартир
                df_old_apart['combined_area'] = df_old_apart['living_area'] + df_old_apart['full_living_area']
                df_new_apart['combined_area'] = df_new_apart['living_area'] + df_new_apart['full_living_area']

                # Присваиваем ранги старым квартирам
                df_old_apart['rank'] = df_old_apart.groupby('room_count')['combined_area'].rank(method='dense').astype(int)

                # Определяем минимальную площадь среди старых квартир 1 ранга
                min_area_rank_1 = df_old_apart[df_old_apart['rank'] == 1].groupby('room_count')['combined_area'].min().to_dict()

                # Создаем словарь для хранения максимальных рангов по количеству комнат среди старых квартир
                max_rank_by_room_count = df_old_apart.groupby('room_count')['rank'].max().to_dict()

                # Присваиваем ранги новым квартирам на основе рангов старых
                df_new_apart['rank'] = 0  # Инициализация колонки для рангов в новых квартирах

                for idx, new_row in df_new_apart.iterrows():
                    # Определяем минимальную площадь для 1 ранга
                    min_area_1_rank = min_area_rank_1.get(new_row['room_count'], float('inf'))

                    # Присваиваем ранг 0, если площадь новой квартиры меньше минимальной площади старой квартиры с 1 рангом
                    if new_row['combined_area'] < min_area_1_rank:
                        df_new_apart.at[idx, 'rank'] = 0
                    else:
                        # Фильтруем старые квартиры, чтобы найти максимальную старую квартиру, которая покрывается новой
                        filtered_old = df_old_apart[
                            (df_old_apart['room_count'] == new_row['room_count']) &
                            (df_old_apart['living_area'] <= new_row['living_area']) &
                            (df_old_apart['full_living_area'] <= new_row['full_living_area']) &
                            (df_old_apart['total_living_area'] <= new_row['total_living_area']) &
                            (df_old_apart['is_special_needs_marker'] == new_row['for_special_needs_marker'])
                        ]

                        if not filtered_old.empty:
                            max_rank = filtered_old['rank'].max()
                            df_new_apart.at[idx, 'rank'] = max_rank

                # Объединяем данные старых и новых квартир
                df_combined = pd.concat([df_old_apart.assign(status='old'), df_new_apart.assign(status='new')], ignore_index=True)

                # Присваиваем индивидуальные ранги без группировки
                df_combined['rank_group'] = df_combined['rank'].astype(int)


                # Обновляем ранги в базе данных для старых и новых квартир
                old_apart_rank_update = list(zip(df_old_apart['rank'], df_old_apart['old_apart_id']))
                new_apart_rank_update = list(zip(df_new_apart['rank'], df_new_apart['new_apart_id']))

                cursor.executemany('''UPDATE public.family_structure
                                    SET rank = %s
                                    WHERE old_apart_id = %s''', old_apart_rank_update)
                conn.commit()
                cursor.executemany('''UPDATE public.new_apartment
                                    SET rank = %s
                                    WHERE new_apart_id = %s
                                ''', new_apart_rank_update)
                conn.commit()
                # Prepare lists of IDs directly from the result sets
                old_apart_ids_for_history = [row[0] for row in
                                 old_aparts]  # Assuming 'old_aparts' is the result of the earlier fetch
                new_apart_ids_for_history = [row[0] for row in
                                 new_aparts]  # Assuming 'new_aparts' is the result of the earlier fetch
                # Выполнение запроса для получения всех данных из таблицы history
                # Выполнение запроса для получения всех данных из таблицы history
                cursor.execute("SELECT * FROM recommendation.history")
                history_data = cursor.fetchall()

                # Флаг для проверки наличия повторяющихся записей
                record_exists = False

                # Проход по всем строкам из таблицы history
                if not date:
                    for record in history_data:
                        # Распаковываем данные из текущей строки
                        history_id, old_apart_house_address, new_aparts_house_address, _ = record
                        history_id, old_apart_house_address, new_aparts_house_address, _, _ = record
                        # Проверка наличия совпадающих записей
                        if old_apart_house_address == old_selected_addresses and new_aparts_house_address == new_selected_addresses:
                            record_exists = True
                            break
                else:
                    cursor.execute("SELECT DISTINCT house_adress FROM recommendation.old_apart WHERE insert_date = (SELECT MAX(insert_date) FROM recommendation.old_apart)")
                    old_selected_addresses = cursor.fetchall()
                    cursor.execute("SELECT DISTINCT house_adress FROM recommendation.new_apart WHERE insert_date = (SELECT MAX(insert_date) FROM recommendation.new_apart)")
                    new_selected_addresses = cursor.fetchall()

                # Если записи не существует, вставляем новую запись в таблицу history
                if not record_exists:
                    cursor.execute("""
                        INSERT INTO recommendation.history(
                            old_house_addresses, 
                            new_house_addresses
                        ) 
                        VALUES(%s, %s)
                    """, (old_selected_addresses, new_selected_addresses))
                    conn.commit()

                    # Получаем последний вставленный history_id
                    cursor.execute("SELECT MAX(history_id) FROM recommendation.history")
                    last_history_id = cursor.fetchone()[0]

                    # Обновление history_id для всех старых квартир, если они есть
                    if old_apart_ids_for_history:
                        cursor.execute('''
                            UPDATE recommendation.old_apart
                            SET history_id = %s
                            WHERE old_apart_id IN %s
                        ''', (last_history_id, tuple(old_apart_ids_for_history)))
                    conn.commit()

                    # Обновление history_id для всех новых квартир, если они есть
                    if new_apart_ids_for_history:
                        cursor.execute('''
                            UPDATE recommendation.new_apart
                            SET history_id = %s
                            WHERE new_apart_id IN %s
                        ''', (last_history_id, tuple(new_apart_ids_for_history)))
                    conn.commit()

                # --- Логика поиска соответствий ---
                offers_to_insert = []
                cannot_offer_to_insert = []

                current_date = datetime.now()

                old_apart_ranks = df_old_apart.groupby('room_count')['rank'].max().to_dict()
                old_apart_count = df_old_apart.groupby('room_count')['old_apart_id'].count().to_dict()
                new_apart_count = df_new_apart.groupby('room_count')['new_apart_id'].count().to_dict()

                df_old_apart_reversed = df_old_apart.loc[::-1]
                a = {}
                delta = {1:1.5, 2:3, 3:5, 4:6.5, 5:8, 6:9.5, 7:11, 8:12.5}

                for i in range(1, (df_old_apart['room_count'].max() if df_old_apart['room_count'].max() > df_new_apart['room_count'].max() else df_new_apart['room_count'].max()) + 1):
                    if (((old_apart_ranks[i] if old_apart_ranks.get(i) is not None else  0) > (max_rank_by_room_count[i] if max_rank_by_room_count.get(i) is not None else  0)) 
                    or ((old_apart_count[i] if old_apart_count.get(i) is not None else  0) > (new_apart_count[i] if new_apart_count.get(i) is not None else  0))):
                        a[i] = 0

                        old_apart_list = []

                        print('DEFICIT')
                        for _, old_apart in df_old_apart_reversed[df_old_apart_reversed['room_count'] == i].iterrows():
                            old_apart_id = int(old_apart['old_apart_id'])
                            # Определяем условие по этажу
                            floor_condition = (
                                (df_new_apart['floor'] >= (old_apart['min_floor'] - 2)) &
                                (df_new_apart['floor'] <= (old_apart['max_floor'] + 2))
                            ) if old_apart['min_floor'] or old_apart['max_floor'] else True

                            if (old_apart['ochered'] == 1) and (ochered):
                                suitable_aparts = df_new_apart[
                                    (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart['full_living_area'] <= old_apart['ochered_squere'] + 9) &
                                    (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart['status_marker'] == old_apart['need']) &
                                    (df_new_apart['floor'] >= (old_apart['min_floor'])) &
                                    (df_new_apart['floor'] <= (old_apart['max_floor']))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart['full_living_area'] <= old_apart['ochered_squere'] + 9) &
                                        (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart['status_marker'] == old_apart['need']) &
                                        floor_condition
                                    ]

                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart['full_living_area'] <= old_apart['ochered_squere'] + 9) &
                                            (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart['status_marker'] == old_apart['need'])
                                        ]
                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            old_apart_list.append(old_apart_id)
                                            df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        old_apart_list.append(old_apart_id)
                                        df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart['new_apart_id'])
                                    old_apart_list.append(old_apart_id)
                                    df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                continue


                            # Условие для даты "Дата покупки"
                            if (old_apart['buying_date'] is not None and old_apart['buying_date'] > datetime.strptime("2017-08-01", "%Y-%m-%d").date() and not (old_apart['min_floor'] or old_apart['max_floor'])):
                                s = df_new_apart[
                                    (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart['room_count'] == old_apart['room_count']) &
                                    (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart['status_marker'] == old_apart['need'])]
                                
                                if not s.empty:
                                    sap = s.iloc[0]

                                    suitable_aparts = df_new_apart[
                                        (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart['room_count'] == old_apart['room_count']) &
                                        (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart['status_marker'] == old_apart['need']) &
                                        ((df_new_apart['full_living_area'] - sap['full_living_area']) <= delta[i])
                                    ].sort_values(by='floor', ascending=True)

                                    # Если подходящих квартир нет, проверяем с условием floor_condition
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart['room_count'] == old_apart['room_count']) &
                                            (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart['status_marker'] == old_apart['need'])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id, current_date)
                                            )
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                        offers_to_insert.append(
                                            (old_apart_id, new_apart_id, current_date)
                                        )
                                else:
                                    cannot_offer_to_insert.append((old_apart_id, current_date))

                            else:
                                # Если "Дата покупки" <= 2017-08-01 или пустая, используем floor_condition
                                suitable_aparts = df_new_apart[
                                    (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart['room_count'] == old_apart['room_count']) &
                                    (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart['status_marker'] == old_apart['need']) &
                                    (df_new_apart['floor'] >= (old_apart['min_floor'])) &
                                    (df_new_apart['floor'] <= (old_apart['max_floor']))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart['room_count'] == old_apart['room_count']) &
                                        (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart['status_marker'] == old_apart['need']) &
                                        floor_condition
                                    ]

                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart['room_count'] == old_apart['room_count']) &
                                            (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart['status_marker'] == old_apart['need'])
                                        ]
                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            old_apart_list.append(old_apart_id)
                                            df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        old_apart_list.append(old_apart_id)
                                        df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart['new_apart_id'])
                                    old_apart_list.append(old_apart_id)
                                    df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]

                        df_new_apart_second

                        for _, old_apart in df_old_apart[df_old_apart['room_count'] == i].iterrows():
                            old_apart_id = int(old_apart['old_apart_id'])
                            if old_apart_id not in old_apart_list:
                                continue
                            # Определяем условие по этажу
                            floor_condition = (
                                (df_new_apart_second['floor'] >= (old_apart['min_floor'] - 2)) &
                                (df_new_apart_second['floor'] <= (old_apart['max_floor'] + 2))
                            ) if old_apart['min_floor'] or old_apart['max_floor'] else True

                            # Условие для даты "Дата покупки"
                            if (old_apart['buying_date'] is not None and old_apart['buying_date'] > datetime.strptime("2017-08-01", "%Y-%m-%d").date() and not (old_apart['min_floor'] or old_apart['max_floor'])):
                                s = df_new_apart_second[
                                    (df_new_apart_second['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart_second['room_count'] == old_apart['room_count']) &
                                    (df_new_apart_second['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart_second['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart_second['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart_second['status_marker'] == old_apart['need'])]
                                
                                if not s.empty:
                                    sap = s.iloc[0]

                                    suitable_aparts = df_new_apart_second[
                                        (df_new_apart_second['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart_second['room_count'] == old_apart['room_count']) &
                                        (df_new_apart_second['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart_second['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart_second['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart_second['status_marker'] == old_apart['need']) &
                                        ((df_new_apart_second['full_living_area'] - sap['full_living_area']) <= delta[i])
                                    ].sort_values(by='floor', ascending=True)

                                    # Если подходящих квартир нет, проверяем с условием floor_condition
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart_second[
                                            (df_new_apart_second['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart_second['room_count'] == old_apart['room_count']) &
                                            (df_new_apart_second['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart_second['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart_second['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart_second['status_marker'] == old_apart['need'])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            df_new_apart_second = df_new_apart_second[df_new_apart_second['new_apart_id'] != new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id, current_date)
                                            )
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        df_new_apart_second = df_new_apart_second[df_new_apart_second['new_apart_id'] != new_apart_id]
                                        offers_to_insert.append(
                                            (old_apart_id, new_apart_id, current_date)
                                        )
                                else:
                                    cannot_offer_to_insert.append((old_apart_id, current_date))
                            else:
                                # Если "Дата покупки" <= 2017-08-01 или пустая, используем floor_condition
                                suitable_aparts = df_new_apart_second[
                                    (df_new_apart_second['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart_second['room_count'] == old_apart['room_count']) &
                                    (df_new_apart_second['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart_second['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart_second['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart_second['status_marker'] == old_apart['need']) &
                                    (df_new_apart_second['floor'] >= (old_apart['min_floor'])) &
                                    (df_new_apart_second['floor'] <= (old_apart['max_floor']))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart_second[
                                        (df_new_apart_second['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart_second['room_count'] == old_apart['room_count']) &
                                        (df_new_apart_second['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart_second['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart_second['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart_second['status_marker'] == old_apart['need']) &
                                        floor_condition
                                    ]
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart_second[
                                            (df_new_apart_second['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart_second['room_count'] == old_apart['room_count']) &
                                            (df_new_apart_second['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart_second['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart_second['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart_second['status_marker'] == old_apart['need'])
                                        ]
                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]  
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            df_new_apart_second = df_new_apart_second[df_new_apart_second['new_apart_id'] != new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id, current_date)
                                            )

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]  
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        df_new_apart_second = df_new_apart_second[df_new_apart_second['new_apart_id'] != new_apart_id]
                                        offers_to_insert.append(
                                            (old_apart_id, new_apart_id, current_date)
                                        )
                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart['new_apart_id'])
                                    df_new_apart_second = df_new_apart_second[df_new_apart_second['new_apart_id'] != new_apart_id]
                                    offers_to_insert.append(
                                        (old_apart_id, new_apart_id, current_date)
                                    )           
                    else:
                        a[i] = 1
                        print('PROFICIT')

                        for _, old_apart in df_old_apart[df_old_apart['room_count'] == i].iterrows():
                            old_apart_id = int(old_apart['old_apart_id'])
                            # Определяем условие по этажу
                            floor_condition = (
                                (df_new_apart['floor'] >= (old_apart['min_floor'] - 2)) &
                                (df_new_apart['floor'] <= (old_apart['max_floor'] + 2))
                            ) if old_apart['min_floor'] or old_apart['max_floor'] else True

                            if (old_apart['ochered'] == 1) and (ochered):
                                suitable_aparts = df_new_apart[
                                    (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart['full_living_area'] <= old_apart['ochered_squere'] + 9) &
                                    (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart['status_marker'] == old_apart['need']) &
                                    (df_new_apart['floor'] >= (old_apart['min_floor'])) &
                                    (df_new_apart['floor'] <= (old_apart['max_floor']))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart['full_living_area'] <= old_apart['ochered_squere'] + 9) &
                                        (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart['status_marker'] == old_apart['need']) &
                                        floor_condition
                                    ]
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart['full_living_area'] <= old_apart['ochered_squere'] + 9) &
                                            (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart['status_marker'] == old_apart['need'])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]  
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id, current_date)
                                            )

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]  
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                        offers_to_insert.append(
                                            (old_apart_id, new_apart_id, current_date)
                                        )

                                else:
                                    suitable_apart = suitable_aparts.iloc[0]  
                                    new_apart_id = int(suitable_apart['new_apart_id'])
                                    df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                    offers_to_insert.append(
                                        (old_apart_id, new_apart_id, current_date)
                                    )
                                continue

                            # Условие для даты "Дата покупки"
                            if (old_apart['buying_date'] is not None and old_apart['buying_date'] > datetime.strptime("2017-08-01", "%Y-%m-%d").date() and not (old_apart['min_floor'] or old_apart['max_floor'])):
                                
                                s = df_new_apart[
                                    (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart['room_count'] == old_apart['room_count']) &
                                    (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart['status_marker'] == old_apart['need'])]
                                
                                if not s.empty:
                                    sap = s.iloc[0]

                                    suitable_aparts = df_new_apart[
                                        (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart['room_count'] == old_apart['room_count']) &
                                        (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart['status_marker'] == old_apart['need']) &
                                        ((df_new_apart['full_living_area'] - sap['full_living_area']) <= delta[i])
                                    ].sort_values(by='floor', ascending=True)

                                    # Если подходящих квартир нет, проверяем с условием floor_condition
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart['room_count'] == old_apart['room_count']) &
                                            (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart['status_marker'] == old_apart['need'])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id, current_date)
                                            )
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                        offers_to_insert.append(
                                            (old_apart_id, new_apart_id, current_date)
                                        )
                                else:
                                    cannot_offer_to_insert.append((old_apart_id, current_date))
                            else:
                                # Если "Дата покупки" <= 2017-08-01 или пустая, используем floor_condition
                                suitable_aparts = df_new_apart[
                                    (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                    (df_new_apart['room_count'] == old_apart['room_count']) &
                                    (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                    (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                    (df_new_apart['living_area'] >= old_apart['living_area']) &
                                    (df_new_apart['status_marker'] == old_apart['need']) &
                                    (df_new_apart['floor'] >= (old_apart['min_floor'])) &
                                    (df_new_apart['floor'] <= (old_apart['max_floor']))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                        (df_new_apart['room_count'] == old_apart['room_count']) &
                                        (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                        (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                        (df_new_apart['living_area'] >= old_apart['living_area']) &
                                        (df_new_apart['status_marker'] == old_apart['need']) &
                                        floor_condition
                                    ]
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart['full_living_area'] >= old_apart['ochered_squere']) &
                                            (df_new_apart['room_count'] == old_apart['room_count']) &
                                            (df_new_apart['full_living_area'] >= old_apart['full_living_area']) &
                                            (df_new_apart['total_living_area'] >= old_apart['total_living_area']) &
                                            (df_new_apart['living_area'] >= old_apart['living_area']) &
                                            (df_new_apart['status_marker'] == old_apart['need'])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, current_date))

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]  
                                            new_apart_id = int(suitable_apart['new_apart_id'])
                                            df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id, current_date)
                                            )

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]  
                                        new_apart_id = int(suitable_apart['new_apart_id'])
                                        df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                        offers_to_insert.append(
                                            (old_apart_id, new_apart_id, current_date)
                                        )

                                else:
                                    suitable_apart = suitable_aparts.iloc[0]  
                                    new_apart_id = int(suitable_apart['new_apart_id'])
                                    df_new_apart = df_new_apart[df_new_apart['new_apart_id'] != new_apart_id]
                                    offers_to_insert.append(
                                        (old_apart_id, new_apart_id, current_date)
                                    )

                # Удаление дубликатов из cannot_offer_to_insert
                cannot_offer_to_insert = list(set(cannot_offer_to_insert))

                # --- Обновление базы данных ---
                for old_apart_id, new_apart_id, insert_date in offers_to_insert:
                    cursor.execute(
                        """
                        INSERT INTO recommendation.offer (old_apart_id, new_apart_id, insert_date, status_id) 
                        VALUES (%s, %s, %s, 8)
                        ON CONFLICT (old_apart_id) 
                        DO UPDATE SET 
                            new_apart_id = EXCLUDED.new_apart_id,
                            status_id = 8,
                            insert_date = EXCLUDED.insert_date
                        """,
                        (old_apart_id, new_apart_id, insert_date)
                    )

                    cursor.execute(
                        """
                        UPDATE recommendation.old_apart
                        SET list_of_offers = array_append(list_of_offers, %s)
                        WHERE old_apart_id = %s
                        """,
                        (new_apart_id, old_apart_id)
                    )

                if cannot_offer_to_insert:
                    print('INSERTING INTO CANNOT_OFFER')
                    cursor.executemany(
                        """
                        INSERT INTO recommendation.cannot_offer (old_apart_id, insert_date) 
                        VALUES (%s, %s)
                        ON CONFLICT (old_apart_id) 
                        DO UPDATE SET 
                            insert_date = EXCLUDED.insert_date
                        """,
                        cannot_offer_to_insert
                    )

                conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        raise