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

def wave_matching(
    df_new_apart,
    df_old_apart,
    cursor,
    conn
):
    try:
        max_rank_by_room_count = df_old_apart.groupby("room_count")["rank"].max().to_dict()
        df_new_apart_rev = df_new_apart.loc[::-1]
        offers_to_insert = []
        cannot_offer_to_insert = []

        old_apart_ranks = df_old_apart.groupby("room_count")["rank"].max().to_dict()
        old_apart_count = df_old_apart.groupby("room_count")["affair_id"].count().to_dict()
        new_apart_count = df_new_apart.groupby("room_count")["new_apart_id"].count().to_dict()

        df_old_apart_reversed = df_old_apart.loc[::-1]
        a = {}
        delta = {1: 1.5, 2: 3, 3: 5, 4: 6.5, 5: 8, 6: 9.5, 7: 11, 8: 12.5}

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

                    if (old_apart["is_queue"] == 1):
                        suitable_aparts = df_new_apart[
                            (df_new_apart["full_living_area"]>= old_apart["queue_square"])& 
                            (df_new_apart["full_living_area"]<= old_apart["queue_square"] + 9)& 
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
                                (df_new_apart["full_living_area"] >= old_apart["queue_square"])&
                                (df_new_apart["full_living_area"]<= old_apart["queue_square"] + 9)&
                                (df_new_apart["full_living_area"]>= old_apart["full_living_area"])& 
                                (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                (df_new_apart["living_area"]>= old_apart["living_area"])& 
                                (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                & floor_condition
                            ]

                            if suitable_aparts.empty:
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["full_living_area"]>= old_apart["queue_square"])&
                                    (df_new_apart["full_living_area"]<= old_apart["queue_square"] + 9)& 
                                    (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                    (df_new_apart["total_living_area"]>= old_apart["total_living_area"])&
                                    (df_new_apart["living_area"]>= old_apart["living_area"])&
                                    (df_new_apart["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                ]
                                if suitable_aparts.empty:
                                    cannot_offer_to_insert.append((old_apart_id,))
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
                            (df_new_apart["full_living_area"]>= old_apart["queue_square"])&
                            (df_new_apart["room_count"]== old_apart["room_count"])&
                            (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                            (df_new_apart["total_living_area"]>= old_apart["total_living_area"])&
                            (df_new_apart["living_area"]>= old_apart["living_area"])&
                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                        ]

                        if not s.empty:
                            sap = s.iloc[0]

                            suitable_aparts = df_new_apart[
                                (df_new_apart["full_living_area"] >= old_apart["queue_square"])&
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
                                    (df_new_apart["full_living_area"]>= old_apart["queue_square"])& 
                                    (df_new_apart["room_count"]== old_apart["room_count"])& 
                                    (df_new_apart["full_living_area"]>= old_apart["full_living_area"])&
                                    (df_new_apart["total_living_area"]>= old_apart["total_living_area"])&
                                    (df_new_apart["living_area"]>= old_apart["living_area"])&
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                ]

                                if suitable_aparts.empty:
                                    cannot_offer_to_insert.append((old_apart_id,))
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

                df_new_apart_second = df_new_apart_rev.loc[::-1]
                print('REVERSED NEW', df_new_apart_second[df_new_apart_second['room_count'] == 2])
                print('REVERSED OLD', df_old_apart_reversed[df_old_apart_reversed["room_count"] == 2])

                for _, old_apart in df_old_apart_reversed[df_old_apart_reversed["room_count"] == i].iterrows():
                    old_apart_id = int(old_apart["affair_id"])
                    if old_apart_id not in old_apart_list:
                        continue
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
                            (df_new_apart_second["full_living_area"]>= old_apart["queue_square"])& 
                            (df_new_apart_second["room_count"]== old_apart["room_count"])&
                            (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                            (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                            (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                            (df_new_apart_second["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                        ]

                        if not s.empty:
                            sap = s.iloc[0]

                            suitable_aparts = df_new_apart_second[
                                (df_new_apart_second["full_living_area"] >= old_apart["queue_square"])& 
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
                                    (df_new_apart_second["full_living_area"] >= old_apart["queue_square"])& 
                                    (df_new_apart_second["room_count"]  == old_apart["room_count"])& 
                                    (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                                    (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                                    (df_new_apart_second["living_area"] >= old_apart["living_area"])& 
                                    (df_new_apart_second[ "for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                ]

                                if suitable_aparts.empty:
                                    cannot_offer_to_insert.append((old_apart_id,))
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
                    else:
                        # Если "Дата покупки" <= 2017-08-01 или пустая, используем floor_condition
                        suitable_aparts = df_new_apart_second[
                            (df_new_apart_second["full_living_area"]>= old_apart["queue_square"])& 
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
                                (df_new_apart_second["full_living_area"]>= old_apart["queue_square"])& 
                                (df_new_apart_second["room_count"] == old_apart["room_count"])& 
                                (df_new_apart_second["full_living_area"]>= old_apart["full_living_area"])& 
                                (df_new_apart_second["total_living_area"]>= old_apart["total_living_area"])& 
                                (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                (df_new_apart_second["for_special_needs_marker"]== old_apart["is_special_needs_marker"])
                                & floor_condition
                            ]
                            if suitable_aparts.empty:
                                suitable_aparts = df_new_apart_second[
                                    (df_new_apart_second["full_living_area"] >= old_apart["queue_square"])& 
                                    (df_new_apart_second["room_count"] == old_apart["room_count"])& 
                                    (df_new_apart_second["full_living_area"] >= old_apart["full_living_area"])& 
                                    (df_new_apart_second["total_living_area"] >= old_apart["total_living_area"])&
                                    (df_new_apart_second["living_area"]>= old_apart["living_area"])& 
                                    (df_new_apart_second["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                ]
                                if suitable_aparts.empty:
                                    print('PROBLEM --- ',old_apart_id)
                                    cannot_offer_to_insert.append((old_apart_id,))

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

                    if (old_apart["is_queue"] == 1):
                        suitable_aparts = df_new_apart[
                            (df_new_apart["full_living_area"]>= old_apart["queue_square"])& 
                            (df_new_apart["full_living_area"]<= old_apart["queue_square"] + 9)& 
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
                                (df_new_apart["full_living_area"]>= old_apart["queue_square"])& 
                                (df_new_apart["full_living_area"]<= old_apart["queue_square"] + 9)& 
                                (df_new_apart["full_living_area"]>= old_apart["full_living_area"])& 
                                (df_new_apart["total_living_area"]>= old_apart["total_living_area"])& 
                                (df_new_apart["living_area"]>= old_apart["living_area"])&
                                (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"]) & floor_condition
                            ]
                            if suitable_aparts.empty:
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["full_living_area"] >= old_apart["queue_square"])& 
                                    (df_new_apart["full_living_area"] <= old_apart["queue_square"] + 9)& 
                                    (df_new_apart["full_living_area"] >= old_apart["full_living_area"])&
                                    (df_new_apart["total_living_area"] >= old_apart["total_living_area"])&
                                    (df_new_apart["living_area"] >= old_apart["living_area"])&
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                ]

                                if suitable_aparts.empty:
                                    cannot_offer_to_insert.append((old_apart_id, ))

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
                            (df_new_apart["full_living_area"] >= old_apart["queue_square"]) &
                            (df_new_apart["room_count"] == old_apart["room_count"]) &
                            (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) &
                            (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                            (df_new_apart["living_area"] >= old_apart["living_area"]) &
                            (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                        ]

                        if not s.empty:
                            sap = s.iloc[0]

                            suitable_aparts = df_new_apart[
                                (df_new_apart["full_living_area"]>= old_apart["queue_square"])
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
                                    (df_new_apart["full_living_area"] >= old_apart["queue_square"]) &
                                    (df_new_apart["room_count"] == old_apart["room_count"])  &
                                    (df_new_apart["full_living_area"] >= old_apart["full_living_area"])  &
                                    (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                                    (df_new_apart["living_area"] >= old_apart["living_area"]) &
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                ]

                                if suitable_aparts.empty:
                                    cannot_offer_to_insert.append((old_apart_id,))
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
                    else:
                        suitable_aparts = df_new_apart[
                            (df_new_apart["full_living_area"] >= old_apart["queue_square"]) &
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
                                (df_new_apart["full_living_area"] >= old_apart["queue_square"]) &
                                (df_new_apart["room_count"] == old_apart["room_count"]) &
                                (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) & 
                                (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) & 
                                (df_new_apart["living_area"] >= old_apart["living_area"]) & 
                                (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"]) &
                                floor_condition
                            ]
                            if suitable_aparts.empty:
                                suitable_aparts = df_new_apart[
                                    (df_new_apart["full_living_area"] >= old_apart["queue_square"]) &
                                    (df_new_apart["room_count"] == old_apart["room_count"]) &
                                    (df_new_apart["full_living_area"] >= old_apart["full_living_area"]) &
                                    (df_new_apart["total_living_area"] >= old_apart["total_living_area"]) &
                                    (df_new_apart["living_area"] >= old_apart["living_area"])&
                                    (df_new_apart["for_special_needs_marker"] == old_apart["is_special_needs_marker"])
                                    ]

                                if suitable_aparts.empty:
                                    cannot_offer_to_insert.append((old_apart_id,))

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
        print('offers_to_insert - ', len(offers_to_insert))
        print('cannot offer to insert - ', len(cannot_offer_to_insert))
        # --- Обновление базы данных ---
        # Для каждой пары old_apart_id и new_apart_id
        for old_apart_id, new_apart_id in offers_to_insert:
            # Создаём JSON с новым апартаментом
            new_aparts_data = {
                str(new_apart_id): {"status_id": 7}
            }
            new_aparts_json = json.dumps(new_aparts_data, ensure_ascii=False)
            print("INSERT INTO public.offer (affair_id, new_aparts, status_id) VALUES (%s, %s, 7)",
                (old_apart_id, new_aparts_json))
            
            # Вставляем новую запись
            cursor.execute(
                "INSERT INTO public.offer (affair_id, new_aparts, status_id) VALUES (%s, %s, 7)",
                (old_apart_id, new_aparts_json)
            )
            print('INSERTED')

        conn.commit()
        res = {'cannot_offer': len(cannot_offer_to_insert), 'offer':  len(offers_to_insert)}
        return res
    except Exception as e:
        print(f"Error: {e}")
        raise


def df_for_aparts(cursor, old_selected_addresses=None, new_selected_addresses=None):
    """
    Retrieves old and new apartment data based on selected addresses.
    
    Args:
        cursor: Database cursor for executing queries
        old_selected_addresses: List of addresses to filter old apartments
        new_selected_addresses: List of addresses with optional sections/ranges to filter new apartments
        
    Returns:
        tuple: (df_old_apart, df_new_apart) - DataFrames containing old and new apartment data
    """
    
    # Query for old apartments
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
            o.queue_square,
            o.rank
        FROM 
            old_apart o 
        LEFT JOIN 
            family_member fm ON o.kpu_number = fm.kpu_number 
        WHERE (o.rsm_status <> 'снято' or rsm_status is NULL) and
            o.affair_id NOT IN (
                SELECT affair_id
                FROM offer
                WHERE status_id <> 2
            ) 
    """
    
    old_apart_query_params = []

    # Additional filters for old apartments
    if old_selected_addresses:
        family_query += " AND o.house_address IN %s"
        old_apart_query_params.append(tuple(old_selected_addresses))
    
    # Add GROUP BY and ORDER clauses
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

    # Execute old apartments query
    cursor.execute(family_query, old_apart_query_params)
    old_aparts = cursor.fetchall()
    
    # Query for new apartments
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
            na.for_special_needs_marker,
            na.rank              
        FROM 
            public.new_apart na
        WHERE new_apart_id::text NOT IN 
                    (SELECT key FROM public.offer, 
                    json_each_text(new_aparts::json) AS j(key, value) 
                    WHERE (value::json->>'status_id')::int != 2) AND (na.status_id NOT IN (12, 13) or na.status_id is null)
    """

    new_apart_query_params = []

    # Process addresses with apartment ranges for new apartments
    if new_selected_addresses and len(new_selected_addresses) > 0:
        # Extract data from nested list if needed
        if isinstance(new_selected_addresses, list) and len(new_selected_addresses) > 0 and isinstance(new_selected_addresses[0], list):
            new_selected_addresses = new_selected_addresses[0]
        
        address_conditions = []
        
        for address_data in new_selected_addresses:
            if not isinstance(address_data, dict):
                continue
                
            address = address_data.get('address')
            sections = address_data.get('sections', [])
            
            if not sections:
                address_conditions.append("(na.house_address = %s)")
                new_apart_query_params.append(address)
                continue
                
            section_conditions = []
            
            for section_data in sections:
                if not isinstance(section_data, dict):
                    continue
                    
                section = section_data.get('section')
                range_data = section_data.get('range', {})
                
                if isinstance(range_data, dict):
                    try:
                        min_apart = int(range_data.get('from', 0))
                        max_apart = int(range_data.get('to', 0))
                    except (ValueError, TypeError):
                        continue
                elif isinstance(range_data, list) and len(range_data) >= 2:
                    try:
                        min_apart = int(range_data[0])
                        max_apart = int(range_data[1])
                    except (ValueError, TypeError):
                        continue
                else:
                    continue
                
                section_conditions.append(
                    "(na.house_address = %s AND na.apart_number BETWEEN %s AND %s)"
                )
                new_apart_query_params.extend([address, min_apart, max_apart])
            
            if section_conditions:
                address_conditions.append(f"({' OR '.join(section_conditions)})")
            else:
                address_conditions.append("(na.house_address = %s)")
                new_apart_query_params.append(address)

        if address_conditions:
            new_apart_query += " AND (" + " OR ".join(address_conditions) + ")"

    # Add sorting for new apartments
    new_apart_query += " ORDER BY room_count ASC, (full_living_area + living_area), floor, living_area ASC, full_living_area ASC, total_living_area ASC"

    # Execute new apartments query
    cursor.execute(new_apart_query, new_apart_query_params)
    new_aparts = cursor.fetchall()
    
    # Create DataFrames
    df_old_apart = pd.DataFrame(old_aparts, columns=[
        "affair_id", "kpu_number", "district", "municipal_district", "room_count", "full_living_area",
        "total_living_area", "living_area", "is_special_needs_marker", "min_floor", "max_floor", "buying_date", 
        "ages", "members_amount", "oldest", "is_queue", "queue_square", "rank"
    ])

    df_new_apart = pd.DataFrame(new_aparts, columns=[
        "new_apart_id", "district", "municipal_district", "house_address", "apart_number", "floor",
        "room_count", "full_living_area", "total_living_area", "living_area", "for_special_needs_marker", "rank"
    ])

    return df_old_apart, df_new_apart



def waves(data, cursor):
    # Extract addresses from input data
    old_selected_addresses = []
    new_selected_addresses = []

    # Collect old addresses
    for key in sorted(data.keys()):
        if key.startswith('old_apartment_house_address_'):
            for item in data[key]:
                if 'address' in item:
                    old_selected_addresses.append(item['address'])

    # Collect new addresses with ranges
    for key in sorted(data.keys()):
        if key.startswith('new_apartment_house_address_'):
            address_data = {
                'address': None,
                'sections': []
            }
            
            for item in data[key]:
                if 'address' in item:
                    address_data['address'] = item['address']
                
                if 'sections' in item:
                    for section in item['sections']:
                        section_data = {
                            'section': section.get('section', ''),
                            'range': section.get('range', {})
                        }
                        address_data['sections'].append(section_data)
            
            if address_data['address']:
                new_selected_addresses.append(address_data)

    # Print address information (for debugging)
    print("\n=== Old addresses ===")
    for i, addr in enumerate(old_selected_addresses, 1):
        print(f"{i}. {addr}")

    print("\n=== New addresses with ranges ===")
    for i, addr in enumerate(new_selected_addresses, 1):
        print(f"{i}. {addr['address']}")
        for j, section in enumerate(addr['sections'], 1):
            print(f"   Section {j}: {section['section']} - Range: {section['range'].get('from', '?')}-{section['range'].get('to', '?')}")

    print(f"\nTotal: {len(old_selected_addresses)} old and {len(new_selected_addresses)} new addresses")

    df_old_apart, df_new_apart = df_for_aparts(cursor, old_selected_addresses=old_selected_addresses, new_selected_addresses=new_selected_addresses)

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

    print('old_apart_rank_update', old_apart_rank_update)
    print('new_apart_rank_update', new_apart_rank_update)

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

    print("Ranking completed successfully")


    # Получаем все ключи, которые начинаются с нужных префиксов
    matching_keys = [key for key in data.keys() 
                    if key.startswith(('old_apartment_house_address_', 'new_apartment_house_address_'))]

    # Если нет подходящих ключей, устанавливаем max_i = 0
    if not matching_keys:
        max_i = 0
    else:
        # Извлекаем номера из ключей и находим максимальный
        max_i = max(int(key.split('_')[-1]) for key in matching_keys)

    # Итерируем по всем возможным индексам
    for i in range(1, max_i + 1):
        old_key = f'old_apartment_house_address_{i}'
        new_key = f'new_apartment_house_address_{i}'
        
        print(f"\n=== Итерация {i} ===")
        
        # Получаем старые адреса
        old_addresses = []
        if old_key in test_data:
            old_addresses = [item['address'] for item in test_data[old_key] if 'address' in item]
            print(f"Старые адреса ({old_key}): {', '.join(old_addresses)}")
        else:
            print(f"Старые адреса ({old_key}): отсутствуют")
        
        # Получаем новые адреса
        new_addresses = []
        if new_key in test_data:
            new_addresses = test_data[new_key]  # Полный объект с секциями и диапазонами
            print(f"Новые адреса ({new_key}):")
            for addr in new_addresses:
                print(f"  Адрес: {addr.get('address', 'Неизвестный адрес')}")
                for section in addr.get('sections', []):
                    print(f"    Секция {section.get('section', '?')}: квартиры "
                        f"{section.get('range', {}).get('from', '?')}-{section.get('range', {}).get('to', '?')}")
        else:
            print(f"Новые адреса ({new_key}): отсутствуют")

        if old_addresses and new_addresses:
            df_old_apart_wave, df_new_apart_wave = df_for_aparts(cursor, old_addresses, new_addresses)
            
            wave_matching(df_new_apart_wave, df_old_apart_wave, cursor, conn)

    return None


# Example usage
if __name__ == "__main__":    
    # Connect to your database
    conn = get_db_connection()
    cursor = conn.cursor()

    test_data = {
        'old_apartment_house_address_1': [{'address': 'Амурская ул., д.66'}],
        'new_apartment_house_address_1': [{
            'address': 'Авиаторов ул., д.5 кор.5',
            'sections': []
        }],
        'old_apartment_house_address_2': [{'address': 'Багрицкого ул., д.6 кор.1'}],
        'new_apartment_house_address_2': [{
            'address': 'Авиационная ул., д.61/2',
            'sections': []
        }],
    }
    
    result = waves(test_data, cursor)
    print(result)
    
    conn.commit()
    conn.close()