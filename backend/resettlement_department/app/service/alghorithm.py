import psycopg2
import pandas as pd
from core.config import settings
from datetime import datetime
import json

def get_db_connection():
    return psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME
       
    )

def match_new_apart_to_family_batch(
    start_date=None,
    end_date=None,
    new_selected_addresses=None,
    old_selected_addresses=None,
    new_selected_districts=None,
    old_selected_districts=None,
    new_selected_areas=None,
    old_selected_areas=None,
    date=False,
    ochered=False,
):
    if (new_selected_addresses is None or old_selected_addresses is None):
        print('POPALSA SUKA')
        return None
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                family_query = """
                        SELECT 
                        o.affair_id, 
                        o.kpu_number,
                        o.district, 
                        o.municipal_district, 
                        o.room_count, 
                        o.full_living_area, 
                        o.total_living_area, 
                        o.living_area, 
                        o.is_special_needs_marker, 
                        o.min_floor, 
                        o.max_floor, 
                        o.buying_date,
                        ARRAY_AGG(EXTRACT(YEAR FROM AGE(fm.date_of_birth))) AS ages,
                        count(o.affair_id) AS members_amount,
                        MAX(EXTRACT(YEAR FROM AGE(fm.date_of_birth::timestamp with time zone))) AS oldest,
                        o.is_queue,
                        o.queue_square
                    FROM 
						old_apart o 
                    LEFT JOIN 
                        family_member fm ON o.kpu_number = fm.kpu_number 
                    WHERE (o.rsm_status <> 'снято' or rsm_status is NULL) and
                        o.affair_id NOT IN (
                            SELECT affair_id
                            FROM  offer
                            where status_id <> 2
                        ) 
                """
                
                old_apart_query_params = []

                # Дополнительные фильтры
                if old_selected_addresses:
                    family_query += " AND o.house_address IN %s"
                    old_apart_query_params.append(tuple(old_selected_addresses))

                if old_selected_districts:
                    family_query += " AND o.district IN %s"
                    old_apart_query_params.append(tuple(old_selected_districts))

                if old_selected_areas:
                    family_query += " AND o.municipal_district IN %s"
                    old_apart_query_params.append(tuple(old_selected_areas))

                if date:
                    family_query += " AND o.updated_at = (SELECT MAX(updated_at) FROM public.old_apart)"
                
                # Добавляем секцию GROUP BY
                family_query += """
						GROUP BY 
                        o.affair_id, 
                        o.kpu_number, 
                        o.district, 
                        o.municipal_district, 
                        o.room_count, 
                        o.full_living_area, 
                        o.total_living_area, 
                        o.living_area, 
                        o.is_special_needs_marker, 
                        o.min_floor, 
                        o.max_floor, 
                        o.buying_date, 
                        o.is_queue, 
                        o.queue_square
                    ORDER BY 
                        o.room_count ASC, 
                        (o.full_living_area + o.living_area + (COUNT(fm.family_member_id) / 3.9)) ASC, 
                        MAX(EXTRACT(YEAR FROM AGE(fm.date_of_birth::timestamp with time zone))) DESC,
                       	o.living_area ASC,  
                        o.full_living_area ASC, 
                        o.total_living_area ASC;
                """

                # Выполнение запроса
                cursor.execute(family_query, old_apart_query_params)
                old_aparts = cursor.fetchall()
                print('FAMILY QUERY', len(old_aparts), family_query, old_apart_query_params)
                if not old_aparts:
                    return ("No old apartments found.")
                # Запрос для новых квартир с учетом диапазонов
                new_apart_query = """
                SELECT 
                    na.new_apart_id, 
                    na.district, 
                    na.municipal_district, 
                    na.house_address, 
                    na.apart_number, 
                    na.floor, 
                    na.room_count, 
                    na.full_living_area, 
                    na.total_living_area, 
                    na.living_area, 
                    na.for_special_needs_marker                
                FROM 
                    public.new_apart na
                WHERE new_apart_id::text NOT IN 
                            (SELECT key FROM public.offer, 
                            json_each_text(new_aparts::json) AS j(key, value) 
                            WHERE (value::json->>'status_id')::int != 2) AND (na.status_id NOT IN (12, 13) or na.status_id is null)
                """

                new_apart_query_params = []
                print('NEW_ADDRESSES --------------------------------------------------', new_selected_addresses)

                # Обрабатываем адреса с диапазонами квартир
                if new_selected_addresses and len(new_selected_addresses) > 0:
                    print(new_selected_addresses)
                    # Извлекаем данные из вложенного списка
                    if isinstance(new_selected_addresses, list) and len(new_selected_addresses) > 0 and isinstance(new_selected_addresses[0], list):
                        new_selected_addresses = new_selected_addresses[0]
                    
                    address_conditions = []
                    
                    for address_data in new_selected_addresses:
                        # Проверяем, является ли address_data словарем
                        if not isinstance(address_data, dict):
                            continue
                            
                        address = address_data.get('address')
                        sections = address_data.get('sections', [])
                        
                        # Если нет секций, добавляем просто условие по адресу
                        if not sections:
                            address_conditions.append("(na.house_address = %s)")
                            new_apart_query_params.append(address)
                            continue
                            
                        # Для каждого адреса создаем условия по секциям и диапазонам
                        section_conditions = []
                        
                        for section_data in sections:
                            if not isinstance(section_data, dict):
                                continue
                                
                            section = section_data.get('section')
                            range_data = section_data.get('range', {})
                            
                            # Обрабатываем разные форматы range (как объект или массив)
                            if isinstance(range_data, dict):
                                try:
                                    min_apart = int(range_data.get('from', 0))
                                    max_apart = int(range_data.get('to', 0))
                                except (ValueError, TypeError):
                                    continue  # Пропускаем некорректные данные
                            elif isinstance(range_data, list) and len(range_data) >= 2:
                                try:
                                    min_apart = int(range_data[0])
                                    max_apart = int(range_data[1])
                                except (ValueError, TypeError):
                                    continue  # Пропускаем некорректные данные
                            else:
                                continue  # Пропускаем некорректные данные
                            
                            # Добавляем условие для номера квартиры в диапазоне
                            section_conditions.append(
                                "(na.house_address = %s AND na.apart_number BETWEEN %s AND %s)"
                            )
                            new_apart_query_params.extend([address, min_apart, max_apart])
                        
                        # Объединяем условия для секций через OR
                        if section_conditions:
                            address_conditions.append(f"({' OR '.join(section_conditions)})")
                        else:
                            # Если были секции, но все оказались некорректными, все равно добавляем адрес
                            address_conditions.append("(na.house_address = %s)")
                            new_apart_query_params.append(address)

                    # Объединяем условия для адресов через OR
                    if address_conditions:
                        new_apart_query += " AND (" + " OR ".join(address_conditions) + ")"

                # Остальные условия (районы, муниципальные округа, дата)
                if new_selected_districts:
                    new_apart_query += " AND district IN %s"
                    new_apart_query_params.append(tuple(new_selected_districts))

                if new_selected_areas:
                    new_apart_query += " AND municipal_district IN %s"
                    new_apart_query_params.append(tuple(new_selected_areas))

                if date:
                    new_apart_query += " AND updated_at = (SELECT MAX(updated_at) FROM public.new_apart)"

                # Сортировка
                new_apart_query += " ORDER BY room_count ASC, (full_living_area + living_area), floor, living_area ASC, full_living_area ASC, total_living_area ASC"

                print("Final query:", new_apart_query)
                print("New Apart Query params:", new_apart_query_params)

                cursor.execute(new_apart_query, new_apart_query_params)
                new_aparts = cursor.fetchall()
                #print(new_aparts)
                #print('FAMILY QUERY', len(new_aparts), new_apart_query, new_apart_query_params)
                #print(new_apart_query, new_apart_query_params)

                if not new_aparts:
                    return("No new apartments found.")
                
                # --- Создание DataFrame и расчет рангов ---
                df_old_apart = pd.DataFrame(old_aparts,columns=[
                        "affair_id", "kpu_number", "district", "municipal_district", "room_count", "full_living_area",
                        "total_living_area", "living_area", "is_special_needs_marker", "min_floor", "max_floor", "buying_date", 
                        "ages", "members_amount", "oldest", "is_queue", "queue_square",
                    ],
                )

                df_new_apart = pd.DataFrame(new_aparts, columns=[
                        "new_apart_id", "district", "municipal_district", "house_address", "apart_number", "floor",
                        "room_count", "full_living_area", "total_living_area", "living_area", "for_special_needs_marker",
                    ],
                )
                df_new_apart_rev = pd.DataFrame(new_aparts, columns=[
                        "new_apart_id", "district", "municipal_district", "house_address", "apart_number", "floor",
                        "room_count", "full_living_area", "total_living_area", "living_area", "for_special_needs_marker",
                    ],
                )
                # Создаем комбинированный столбец для старых и новых квартир
                df_old_apart["combined_area"] = (df_old_apart["living_area"] + df_old_apart["full_living_area"])
                df_new_apart["combined_area"] = (df_new_apart["living_area"] + df_new_apart["full_living_area"])

                # Присваиваем ранги старым квартирам
                df_old_apart["rank"] = df_old_apart.groupby("room_count")["combined_area"].rank(method="dense").astype(int)

                # Определяем минимальную площадь среди старых квартир 1 ранга
                min_area_rank_1 = df_old_apart[df_old_apart["rank"] == 1].groupby("room_count")["combined_area"].min().to_dict()

                # Создаем словарь для хранения максимальных рангов по количеству комнат среди старых квартир
                max_rank_by_room_count = df_old_apart.groupby("room_count")["rank"].max().to_dict()

                # Присваиваем ранги новым квартирам на основе рангов старых
                df_new_apart["rank"] = 0  # Инициализация колонки для рангов в новых квартирах
                

                for idx, new_row in df_new_apart.iterrows():
                    # Определяем минимальную площадь для 1 ранга
                    min_area_1_rank = min_area_rank_1.get(new_row["room_count"], float("inf"))

                    # Присваиваем ранг 0, если площадь новой квартиры меньше минимальной площади старой квартиры с 1 рангом
                    if new_row["combined_area"] < min_area_1_rank:
                        df_new_apart.at[idx, "rank"] = 0
                    else:
                        # Фильтруем старые квартиры, чтобы найти максимальную старую квартиру, которая покрывается новой
                        filtered_old = df_old_apart[
                            (df_old_apart["room_count"] == new_row["room_count"]) &
                            (df_old_apart["living_area"] <= new_row["living_area"]) &
                            (df_old_apart["full_living_area"] <= new_row["full_living_area"]) &
                            (df_old_apart["total_living_area"] <= new_row["total_living_area"]) & 
                            (df_old_apart["is_special_needs_marker"] == new_row["for_special_needs_marker"])
                        ]

                        if not filtered_old.empty:
                            max_rank = filtered_old["rank"].max()
                            df_new_apart.at[idx, "rank"] = max_rank

                # Объединяем данные старых и новых квартир
                df_combined = pd.concat([df_old_apart.assign(status="old"), df_new_apart.assign(status="new")], ignore_index=True)

                # Присваиваем индивидуальные ранги без группировки
                df_combined["rank_group"] = df_combined["rank"].astype(int)

                # Обновляем ранги в базе данных для старых и новых квартир
                old_apart_rank_update = list(zip(df_old_apart["rank"], df_old_apart["affair_id"]))
                new_apart_rank_update = list(zip(df_new_apart["rank"], df_new_apart["new_apart_id"]))

                cursor.executemany(
                    """UPDATE public.old_apart
                                    SET rank = %s
                                    WHERE affair_id = %s""",
                    old_apart_rank_update,
                )
                cursor.executemany(
                    """UPDATE public.new_apart
                                    SET rank = %s
                                    WHERE new_apart_id = %s
                                """,
                    new_apart_rank_update,
                )

                # Prepare lists of IDs directly from the result sets
                old_apart_ids_for_history = [row[0] for row in old_aparts]
                new_apart_ids_for_history = [row[0] for row in new_aparts]

                cursor.execute("SELECT history_id, old_house_addresses, new_house_addresses FROM public.history")
                history_data = cursor.fetchall()
                # Флаг для проверки наличия повторяющихся записей
                record_exists = False

                if date or history_data is None:
                    cursor.execute(
                        "SELECT DISTINCT house_address FROM public.old_apart WHERE affair_id IN (SELECT affair_id FROM public.old_apart WHERE updated_at = (SELECT MAX(updated_at) FROM public.old_apart))"
                    )
                    old_selected_addresses = [r[0] for r in cursor.fetchall()]
                    cursor.execute(
                        "SELECT DISTINCT house_address FROM public.new_apart WHERE updated_at = (SELECT MAX(updated_at) FROM public.new_apart)"
                    )
                    new_selected_addresses = [r[0] for r in cursor.fetchall()]
                else:
                    for record in history_data :
                        (history_id, old_house_addresses, new_house_addresses) = record
                        if (old_house_addresses == old_selected_addresses and new_house_addresses == new_selected_addresses):
                            record_exists = True
                            break

                # Если записи не существует, вставляем новую запись в таблицу history
                new_addresses = [item['address'] for item in new_selected_addresses] if not date else new_selected_addresses
                if not record_exists:
                    cursor.execute(
                        """
                        INSERT INTO public.history(
                            old_house_addresses, 
                            new_house_addresses
                        ) 
                        VALUES(%s, %s)
                        RETURNING history_id
                    """,
                        (old_selected_addresses, new_addresses),
                    )
                    last_history_id = cursor.fetchone()[0]
                    conn.commit()

                    # Обновление history_id для всех старых квартир, если они есть
                    if old_apart_ids_for_history:
                        cursor.execute(
                            """
                            UPDATE public.old_apart
                            SET history_id = %s
                            WHERE affair_id IN %s
                        """,
                            (last_history_id, tuple(old_apart_ids_for_history)),
                        )
                    conn.commit()

                    # Обновление history_id для всех новых квартир, если они есть
                    if new_apart_ids_for_history:
                        cursor.execute(
                            """
                            UPDATE public.new_apart
                            SET history_id = %s
                            WHERE new_apart_id IN %s
                        """,
                            (last_history_id, tuple(new_apart_ids_for_history)),
                        )
                    conn.commit()

                # --- Логика поиска соответствий ---
                offers_to_insert = []
                cannot_offer_to_insert = []

                old_apart_ranks = df_old_apart.groupby("room_count")["rank"].max().to_dict()
                old_apart_count = df_old_apart.groupby("room_count")["affair_id"].count().to_dict()
                new_apart_count = df_new_apart.groupby("room_count")["new_apart_id"].count().to_dict()

                df_old_apart_reversed = df_old_apart.loc[::-1]
                a = {}
                delta = {1: 1.5, 2: 3, 3: 5, 4: 6.5, 5: 8, 6: 9.5, 7: 11, 8: 12.5}
                df_new_apart_second = df_new_apart_rev.loc[::-1]
                min_rank_by_room = {}

                for i in range(1, (df_old_apart['room_count'].max() if df_old_apart['room_count'].max() > df_new_apart['room_count'].max() else df_new_apart['room_count'].max()) + 1):
                    if (((old_apart_ranks[i] if old_apart_ranks.get(i) is not None else  0) > (max_rank_by_room_count[i] if max_rank_by_room_count.get(i) is not None else  0)) 
                    or ((old_apart_count[i] if old_apart_count.get(i) is not None else  0) > (new_apart_count[i] if new_apart_count.get(i) is not None else  0))):
                        a[i] = 0

                        old_apart_list = []

                        print("DEFICIT")
                        for _, old_apart in df_old_apart_reversed[df_old_apart_reversed["room_count"] == i].iterrows():
                            old_apart_id = int(old_apart["affair_id"])
                            # Определяем условие по этажу
                            floor_condition = (
                                ((df_new_apart["floor"] >= (old_apart["min_floor"] - 2)) & 
                                 (df_new_apart["floor"] <= (old_apart["max_floor"] + 2))
                                ) if old_apart["min_floor"] or old_apart["max_floor"] else True
                            )

                            if (old_apart["is_queue"] == 1) and (ochered):
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                    (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                    (df_new_apart["living_area"]>= old_apart["living_area"])& 
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])& 
                                    (df_new_apart["floor"] >= (old_apart["min_floor"]))&
                                    (df_new_apart["floor"]<= (old_apart["max_floor"]))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart["full_living_area"]>= old_apart["full_living_area"])& 
                                        (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                        (df_new_apart["living_area"]>= old_apart["living_area"])& 
                                        (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                        & floor_condition
                                    ]

                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                            (df_new_apart["total_living_area"]>= old_apart["total_living_area"])&
                                            (df_new_apart["living_area"]>= old_apart["living_area"])&
                                            (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                        ]
                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id,))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            old_apart_list.append(old_apart_id)
                                            df_new_apart = df_new_apart[df_new_apart["new_apart_id"]!= new_apart_id]
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        old_apart_list.append(old_apart_id)
                                        df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart["new_apart_id"])
                                    old_apart_list.append(old_apart_id)
                                    df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                continue

                            # Условие для даты "Дата покупки"
                            elif (
                                old_apart["buying_date"] is not None and old_apart["buying_date"] > datetime.strptime("2017-08-01", "%Y-%m-%d").date()
                                and not (old_apart["min_floor"] or old_apart["max_floor"])
                            ):
                                s = df_new_apart[
                                    (df_new_apart["room_count"]== old_apart["room_count"])&
                                    (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                    (df_new_apart["total_living_area"]>= old_apart["total_living_area"])&
                                    (df_new_apart["living_area"]>= old_apart["living_area"])&
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                ]

                                if not s.empty:
                                    sap = s.iloc[0]

                                    suitable_aparts = df_new_apart[
                                        (df_new_apart["room_count"]== old_apart["room_count"])& 
                                        (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                        (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                        (df_new_apart["living_area"]>= old_apart["living_area"])&
                                        (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])&
                                        ((df_new_apart["full_living_area"] - sap["full_living_area"])<= delta[i])
                                    ].sort_values(by="floor", ascending=True)

                                    # Если подходящих квартир нет, проверяем с условием floor_condition
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[ 
                                            (df_new_apart["room_count"]== old_apart["room_count"])& 
                                            (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                            (df_new_apart["total_living_area"]>= old_apart["total_living_area"])&
                                            (df_new_apart["living_area"]>= old_apart["living_area"])&
                                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id,))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                            offers_to_insert.append((old_apart_id, new_apart_id))
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                        offers_to_insert.append((old_apart_id, new_apart_id,))
                                else:
                                    cannot_offer_to_insert.append((old_apart_id, ))
                                    if i in min_rank_by_room:
                                        if old_apart["rank"] < min_rank_by_room[i]:
                                            min_rank_by_room[i] = old_apart["rank"]
                                    else:
                                        min_rank_by_room[i] = old_apart["rank"]

                            else:
                                # Если "Дата покупки" <= 2017-08-01 или пустая, используем floor_condition
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["room_count"]== old_apart["room_count"])&
                                    (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                    (df_new_apart["total_living_area"] >= old_apart["total_living_area"])&
                                    (df_new_apart["living_area"]>= old_apart["living_area"])&
                                    (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])&
                                    (df_new_apart["floor"]>= (old_apart["min_floor"]))& 
                                    (df_new_apart["floor"] <= (old_apart["max_floor"]))
                                ]
                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart["room_count"] == old_apart["room_count"])&
                                        (df_new_apart["full_living_area"] >= old_apart["full_living_area"])&
                                        (df_new_apart["total_living_area"] >= old_apart["total_living_area"])&
                                        (df_new_apart["living_area"]>= old_apart["living_area"])&
                                        (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])&
                                        floor_condition
                                    ]

                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart["room_count"] == old_apart["room_count"])&
                                            (df_new_apart["full_living_area"] >= old_apart["full_living_area"])& 
                                            (df_new_apart["total_living_area"] >= old_apart["total_living_area"])&
                                            (df_new_apart["living_area"] >= old_apart["living_area"])& 
                                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                        ]
                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, ))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            old_apart_list.append(old_apart_id)
                                            df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        old_apart_list.append(old_apart_id)
                                        df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart["new_apart_id"])
                                    old_apart_list.append(old_apart_id)
                                    df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]

                        print('REVERSED NEW', df_new_apart_second[df_new_apart_second['room_count'] == 2])
                        print('REVERSED OLD', df_old_apart_reversed[df_old_apart_reversed["room_count"] == 2])

                        for _, old_apart in df_old_apart_reversed[df_old_apart_reversed["room_count"] == i].iterrows():
                            old_apart_id = int(old_apart["affair_id"])
                            #if old_apart_id not in old_apart_list:
                            #    continue
                            # Определяем условие по этажу
                            floor_condition = (
                                ((df_new_apart_second["floor"]>= (old_apart["min_floor"] - 2))&
                                (df_new_apart_second["floor"] <= (old_apart["max_floor"] + 2)))
                                if old_apart["min_floor"] or old_apart["max_floor"]
                                else True
                            )

                            # Условие для даты "Дата покупки"
                            if (old_apart["buying_date"] is not None and old_apart["buying_date"] > datetime.strptime("2017-08-01", "%Y-%m-%d").date()
                                and not (old_apart["min_floor"] or old_apart["max_floor"])
                            ):
                                s = df_new_apart_second[
                                    (df_new_apart_second["room_count"]== old_apart["room_count"])&
                                    (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                                    (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                                    (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                    (df_new_apart_second["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                ]

                                if not s.empty:
                                    sap = s.iloc[0]

                                    suitable_aparts = df_new_apart_second[
                                        (df_new_apart_second["room_count"] == old_apart["room_count"])& 
                                        (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                                        (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])&
                                        (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                        (df_new_apart_second["for_special_needs_marker"]== old_apart["is_special_needs_marker"])& 
                                        ((df_new_apart_second["full_living_area"]- sap["full_living_area"] ) <= delta[i])
                                    ].sort_values(by="floor", ascending=True)

                                    # Если подходящих квартир нет, проверяем с условием floor_condition
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart_second[
                                            (df_new_apart_second["room_count"]  == old_apart["room_count"])& 
                                            (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                                            (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                                            (df_new_apart_second["living_area"] >= old_apart["living_area"])& 
                                            (df_new_apart_second[ "for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id,))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            df_new_apart_second = df_new_apart_second[df_new_apart_second["new_apart_id"]!= new_apart_id]
                                            offers_to_insert.append(
                                                (old_apart_id, new_apart_id,)
                                            )
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(
                                            suitable_apart["new_apart_id"]
                                        )
                                        df_new_apart_second = df_new_apart_second[
                                            df_new_apart_second["new_apart_id"]
                                            != new_apart_id
                                        ]
                                        offers_to_insert.append((old_apart_id, new_apart_id,))
                                else:
                                    cannot_offer_to_insert.append((old_apart_id, ))
                                    if i in min_rank_by_room:
                                        if old_apart["rank"] < min_rank_by_room[i]:
                                            min_rank_by_room[i] = old_apart["rank"]
                                    else:
                                        min_rank_by_room[i] = old_apart["rank"]
                            else:
                                # Если "Дата покупки" <= 2017-08-01 или пустая, используем floor_condition
                                suitable_aparts = df_new_apart_second[
                                    (df_new_apart_second["room_count"]  == old_apart["room_count"])& 
                                    (df_new_apart_second["full_living_area"] >= old_apart["full_living_area"])& 
                                    (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                                    (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                    ( df_new_apart_second["for_special_needs_marker"] == old_apart["is_special_needs_marker"])& 
                                    (df_new_apart_second["floor"] >= (old_apart["min_floor"]))& 
                                    (df_new_apart_second["floor"]<= (old_apart["max_floor"]))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart_second[
                                        (df_new_apart_second["room_count"] == old_apart["room_count"])& 
                                        (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                                        (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                                        (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                        (df_new_apart_second["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                        & floor_condition
                                    ]
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart_second[
                                            (df_new_apart_second["room_count"] == old_apart["room_count"])& 
                                            (df_new_apart_second["full_living_area"] >= old_apart["full_living_area"])& 
                                            (df_new_apart_second["total_living_area"] >= old_apart["total_living_area"])&
                                            (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                            (df_new_apart_second["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                        ]
                                        if suitable_aparts.empty:
                                            print('PROBLEM --- ',old_apart_id)
                                            cannot_offer_to_insert.append((old_apart_id,))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            df_new_apart_second = df_new_apart_second[df_new_apart_second["new_apart_id"]!= new_apart_id]
                                            offers_to_insert.append((old_apart_id, new_apart_id,))

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        df_new_apart_second = df_new_apart_second[df_new_apart_second["new_apart_id"] != new_apart_id]
                                        offers_to_insert.append((old_apart_id, new_apart_id, ))
                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart["new_apart_id"])
                                    df_new_apart_second = df_new_apart_second[
                                        df_new_apart_second["new_apart_id"] != new_apart_id]
                                    offers_to_insert.append((old_apart_id, new_apart_id,))
                    else:
                        a[i] = 1
                        print("PROFICIT")

                        for _, old_apart in df_old_apart[
                            df_old_apart["room_count"] == i
                        ].iterrows():
                            old_apart_id = int(old_apart["affair_id"])
                            # Определяем условие по этажу
                            floor_condition = ((
                                    (df_new_apart["floor"]>= (old_apart["min_floor"] - 2))& 
                                    (df_new_apart["floor"] <= (old_apart["max_floor"] + 2)))
                                if old_apart["min_floor"] or old_apart["max_floor"]
                                else True
                            )

                            if (old_apart["is_queue"] == 1) and (ochered):
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["full_living_area"]>= old_apart["full_living_area"])& 
                                    (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                    (df_new_apart["living_area"]>= old_apart["living_area"])& 
                                    (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])& 
                                    (df_new_apart["floor"]>= (old_apart["min_floor"]))& 
                                    (df_new_apart["floor"]<= (old_apart["max_floor"]))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart["full_living_area"]>= old_apart["full_living_area"])& 
                                        (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                        (df_new_apart["living_area"]>= old_apart["living_area"])&
                                        (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"]) & floor_condition
                                    ]
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart["full_living_area"] >= old_apart["full_living_area"])&
                                            (df_new_apart["total_living_area"] >= old_apart["total_living_area"])&
                                            (df_new_apart["living_area"] >= old_apart["living_area"])&
                                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id, ))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                            offers_to_insert.append((old_apart_id, new_apart_id,))

                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                        offers_to_insert.append((old_apart_id, new_apart_id,))

                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart["new_apart_id"])
                                    df_new_apart = df_new_apart[
                                        df_new_apart["new_apart_id"] != new_apart_id
                                    ]
                                    offers_to_insert.append((old_apart_id, new_apart_id,))
                                continue

                            # Условие для даты "Дата покупки"
                            if (old_apart["buying_date"] is not None and old_apart["buying_date"] > datetime.strptime("2017-08-01", "%Y-%m-%d").date() 
                                and not (old_apart["min_floor"] or old_apart["max_floor"])
                            ):
                                s = df_new_apart[
                                    (df_new_apart["room_count"] == old_apart["room_count"]) &
                                    (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) &
                                    (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                                    (df_new_apart["living_area"] >= old_apart["living_area"]) &
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                ]

                                if not s.empty:
                                    sap = s.iloc[0]

                                    suitable_aparts = df_new_apart[
                                        (df_new_apart["room_count"] == old_apart["room_count"]) &
                                        (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) &
                                        (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                                        (df_new_apart["living_area"] >= old_apart["living_area"]) &
                                        (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"]) &
                                        ((df_new_apart["full_living_area"] - sap["full_living_area"]) <= delta[i])
                                    ].sort_values(by="floor", ascending=True)

                                    # Если подходящих квартир нет, проверяем с условием floor_condition
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart["room_count"] == old_apart["room_count"])  &
                                            (df_new_apart["full_living_area"] >= old_apart["full_living_area"])  &
                                            (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                                            (df_new_apart["living_area"] >= old_apart["living_area"]) &
                                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                        ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id,))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]
                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                            offers_to_insert.append((old_apart_id,new_apart_id,))
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                        offers_to_insert.append((old_apart_id, new_apart_id,))
                                else:
                                    cannot_offer_to_insert.append((old_apart_id,))
                                    if i in min_rank_by_room:
                                        if old_apart["rank"] < min_rank_by_room[i]:
                                            min_rank_by_room[i] = old_apart["rank"]
                                    else:
                                        min_rank_by_room[i] = old_apart["rank"]
                            else:
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["room_count"] == old_apart["room_count"])  &
                                    (df_new_apart["full_living_area"] >= old_apart["full_living_area"])  & 
                                    (df_new_apart["total_living_area"] >= old_apart["total_living_area"])  &
                                    (df_new_apart["living_area"] >= old_apart["living_area"])  &
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])  &
                                    (df_new_apart["floor"] >= (old_apart["min_floor"])) & 
                                    (df_new_apart["floor"] <= (old_apart["max_floor"]))
                                ]

                                # Проверка наличия подходящих квартир
                                if suitable_aparts.empty:
                                    suitable_aparts = df_new_apart[
                                        (df_new_apart["room_count"] == old_apart["room_count"]) &
                                        (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) & 
                                        (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) & 
                                        (df_new_apart["living_area"] >= old_apart["living_area"]) & 
                                        (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"]) &
                                        floor_condition
                                    ]
                                    if suitable_aparts.empty:
                                        suitable_aparts = df_new_apart[
                                            (df_new_apart["room_count"] == old_apart["room_count"]) &
                                            (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) &
                                            (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                                            (df_new_apart["living_area"] >= old_apart["living_area"])&
                                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                            ]

                                        if suitable_aparts.empty:
                                            cannot_offer_to_insert.append((old_apart_id,))
                                            if i in min_rank_by_room:
                                                if old_apart["rank"] < min_rank_by_room[i]:
                                                    min_rank_by_room[i] = old_apart["rank"]
                                            else:
                                                min_rank_by_room[i] = old_apart["rank"]

                                        else:
                                            suitable_apart = suitable_aparts.iloc[0]
                                            new_apart_id = int(suitable_apart["new_apart_id"])
                                            df_new_apart = df_new_apart[df_new_apart["new_apart_id"]!= new_apart_id]

                                            offers_to_insert.append((old_apart_id, new_apart_id,))
                                    else:
                                        suitable_apart = suitable_aparts.iloc[0]
                                        new_apart_id = int(suitable_apart["new_apart_id"])
                                        df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]
                                        offers_to_insert.append((old_apart_id, new_apart_id,))

                                else:
                                    suitable_apart = suitable_aparts.iloc[0]
                                    new_apart_id = int(suitable_apart["new_apart_id"])
                                    df_new_apart = df_new_apart[df_new_apart["new_apart_id"] != new_apart_id]

                                    offers_to_insert.append(
                                        (old_apart_id, new_apart_id,)
                                    )

                # Удаление дубликатов из cannot_offer_to_insert
                cannot_offer_to_insert = list(set(cannot_offer_to_insert))
                print('min_rank_by_room - ', min_rank_by_room)
                print('offers_to_insert - ', len(offers_to_insert))
                print('cannot offer to insert - ', len(cannot_offer_to_insert))
                # --- Обновление базы данных ---
                # Создаем словарь для сопоставления affair_id с rank
                old_apart_ranks = df_old_apart.set_index("affair_id")["rank"].astype(str).to_dict()

                # Список для массового обновления рангов в new_apart
                new_apart_rank_update = []

                for old_apart_id, new_apart_id in offers_to_insert:
                    # Получаем rank из словаря
                    rank = old_apart_ranks.get(old_apart_id)
                    
                    # Добавляем данные для обновления new_apart
                    if rank is not None:
                        new_apart_rank_update.append((rank, new_apart_id))
                    
                    # Обновляем запись в offer (без добавления rank в JSON)
                    cursor.execute(
                        "SELECT new_aparts FROM public.offer WHERE affair_id = %s",
                        (old_apart_id,)
                    )
                    result = cursor.fetchone()
                    
                    current_new_aparts = {}
                    if result and result[0]:
                        current_new_aparts = json.loads(result[0])
                    
                    current_new_aparts[str(new_apart_id)] = {
                        "status_id": 7  # Только статус, без ранга
                    }
                    
                    new_aparts_json = json.dumps(current_new_aparts, ensure_ascii=False)
                    
                    if result:
                        cursor.execute(
                            "UPDATE public.offer SET new_aparts = %s WHERE affair_id = %s",
                            (new_aparts_json, old_apart_id)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO public.offer (affair_id, new_aparts, status_id) VALUES (%s, %s, 7)",
                            (old_apart_id, new_aparts_json)
                        )

                # Массовое обновление рангов в new_apart
                if new_apart_rank_update:
                    cursor.executemany(
                        """UPDATE public.new_apart
                            SET rank = %s
                            WHERE new_apart_id = %s""",
                        new_apart_rank_update
                    )
                
                if cannot_offer_to_insert and not df_new_apart_second.empty:                    
                    # Подготавливаем данные для обновления
                    update_data = []
                    for _, row in df_new_apart_second.iterrows():
                        room_count = row['room_count']
                        new_id = row['new_apart_id']
                        
                        # Получаем минимальный ранг для данной комнатности
                        min_rank = min_rank_by_room.get(room_count)
                        print('min_rank -------------- ', min_rank-1)
                        update_data.append((min_rank-1, new_id))

                    # Выполняем массовое обновление
                    if update_data:
                        cursor.executemany(
                            """UPDATE public.new_apart
                                SET rank = %s
                                WHERE new_apart_id = %s""",
                            update_data
                        )

                conn.commit()
                res = {'cannot_offer': len(cannot_offer_to_insert), 'offer':  len(offers_to_insert)}
                return res
    except Exception as e:
        print(f"Error: {e}")
        raise