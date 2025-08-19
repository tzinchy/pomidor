import json

STATUS_MAPPING = {
    1: "Согласие",
    2: "Отказ",
    3: "Суд",
    4: "МФР Компенсация",
    5: "МФР Докупка",
    6: "Ожидание",
    7: "Ждёт одобрения",
    8: "Не подобрано",
    9: "МФР (вне района)",
    10: "МФР Компенсация (вне района)",
    11: "Свободная",
    16: "Подготовить смотровой",
    17: "Отказ (Выход из Суда)"
}

old_apart_test_data = [
    {
        'affair_id': 1001,
        'kpu_number': 'test1',
        'fio': 'test1',
        'people_in_family': 3,
        'cad_num': 'test1',
        'house_address': 'test1',
        'apart_number': 'test1',
        'room_count': 2,
        'floor': 3,
        'living_area': 45.5,
        'people_v_dele': 2,
        'people_uchet': 3,
        'apart_type': 'test1',
        'municipal_district': 'test1',
        'is_special_needs_marker': 1,
        'is_queue': 0,
        'unom': 'test1',
        'total_living_area': 50.0,
        'full_living_area': 55.0
    },
    {
        'affair_id': 1002,
        'kpu_number': 'test2',
        'fio': 'test2',
        'people_in_family': 2,
        'cad_num': 'test2',
        'house_address': 'test2',
        'apart_number': 'test2',
        'room_count': 1,
        'floor': 2,
        'living_area': 33.2,
        'people_v_dele': 1,
        'people_uchet': 2,
        'apart_type': 'test2',
        'municipal_district': 'test2',
        'is_special_needs_marker': 0,
        'is_queue': 1,
        'unom': 'test2',
        'total_living_area': 35.0,
        'full_living_area': 40.0
    },
    {
        'affair_id': 1003,
        'kpu_number': 'test3',
        'fio': 'test3',
        'people_in_family': 4,
        'cad_num': 'test3',
        'house_address': 'test3',
        'apart_number': 'test3',
        'room_count': 3,
        'floor': 5,
        'living_area': 65.0,
        'people_v_dele': 3,
        'people_uchet': 4,
        'apart_type': 'test3',
        'municipal_district': 'test3',
        'is_special_needs_marker': 0,
        'is_queue': 0,
        'unom': 'test3',
        'total_living_area': 70.0,
        'full_living_area': 75.0
    }
]
new_apart_test_data = [
    {
        'new_apart_id': 2001,
        'rsm_apart_id': 3001,
        'cad_num': 'test_new1',
        'unom': 2001,
        'un_kv': 101,
        'house_address': 'test_new1',
        'apart_number': 101,
        'floor': 3,
        'room_count': 2,
        'living_area': 45.5,
    },
    {
        'new_apart_id': 2002,
        'rsm_apart_id': 3002,
        'cad_num': 'test_new2',
        'unom': 2002,
        'un_kv': 102,
        'house_address': 'test_new2',
        'apart_number': 102,
        'floor': 2,
        'room_count': 1,
        'living_area': 33.2,
    },
    {
        'new_apart_id': 2003,
        'rsm_apart_id': 3003,
        'cad_num': 'test_new3',
        'unom': 2003,
        'un_kv': 103,
        'house_address': 'test_new3',
        'apart_number': 103,
        'floor': 5,
        'room_count': 3,
        'living_area': 65.0,
    },
    {
        'new_apart_id': 2004,
        'rsm_apart_id': 3004,
        'cad_num': 'test_new4',
        'unom': 2004,
        'un_kv': 104,
        'house_address': 'test_new4',
        'apart_number': 104,
        'floor': 4,
        'room_count': 2,
        'living_area': 50.0,
    },
    {
        'new_apart_id': 2005,
        'rsm_apart_id': 3005,
        'cad_num': 'test_new5',
        'unom': 2005,
        'un_kv': 105,
        'house_address': 'test_new5',
        'apart_number': 105,
        'floor': 1,
        'room_count': 1,
        'living_area': 35.0,
    }
]

offer_test_data = [
    {
        'offer_id': 1,
        'affair_id': 1001,
        'new_aparts': json.dumps({'2001': {'status_id': 2}})
    },
    {
        'offer_id': 2,
        'affair_id': 1001,
        'new_aparts': json.dumps({'2002': {'status_id': 2}})
    },
    {
        'offer_id': 3,
        'affair_id': 1001,
        'new_aparts': json.dumps({'2003': {'status_id': 2}})

    },
    {
        'offer_id': 4,
        'affair_id': 1001,
        'new_aparts': json.dumps({'2004': {'status_id': 2}, '2005': {'status_id': 2}})
    },
    {
        'offer_id': 5,
        'affair_id': 1002,
        'new_aparts': json.dumps({'2002': {'status_id': 2}})
    },
    {
        'offer_id': 6,
        'affair_id': 1002,
        'new_aparts': json.dumps({'2001': {'status_id': 2}})
    },
    {
        'offer_id': 8,
        'affair_id': 1003,
        'new_aparts': json.dumps({'2002': {'status_id': 2}})
    },
    {
        'offer_id': 9,
        'affair_id': 1003,
        'new_aparts': json.dumps({'2001': {'status_id': 2}})
    },
    {
        'offer_id': 10,
        'affair_id': 1003,
        'new_aparts': json.dumps({'2003': {'status_id': 2}})

    }
    ]

order_decisions_test_data = {    
    3 :
    {
        'affair_id': 1002,
        'order_id': 5002,
        'is_cancelled': False,
        'article_code': '97/70',
        'collateral_type': 'ППд',
        'accounting_article': '70Переселение',
        'cad_num': 'test_new2',
        'unom': 2002,
        'un_kv': 101,
        'area_id': json.dumps({'2001' : {}}),
        'status_id' : 3
    },
    
    5 :
    {
        'affair_id': 1002,
        'order_id': 5003,
        'is_cancelled': False,
        'article_code': '7002',
        'collateral_type': 'ППд',
        'accounting_article': '70',
        'cad_num': 'test_new2',
        'unom': 2002,
        'un_kv': 101,
        'area_id': json.dumps({'2001' : {}}),
        'status_id' : 5
    },
    
    4: 
    {
        'affair_id': 1002,
        'order_id': 5004,
        'is_cancelled': False,
        'article_code': '7002',
        'collateral_type': 'ППк789',
        'accounting_article': '70Реновация',
        'cad_num': 'test_new2',  # Проверка поиска по unom/un_kv
        'unom': 2002,
        'un_kv': 101,
        'area_id': json.dumps(None),
        'status_id' : 4
    },
    
    1:
    {
        'affair_id': 1002,
        'order_id': 5005,
        'is_cancelled': False,
        'article_code': '9715',
        'collateral_type': 'ППв',
        'accounting_article': '70',
        'cad_num': 'test_new2',
        'unom': None, 
        'un_kv': None,
        'area_id': json.dumps({'2001' : {}}),
        'status_id' : 1
    },
    9 :  {
        'affair_id': 1002,
        'order_id': 5006,
        'is_cancelled': False,
        'article_code': '7002',
        'collateral_type': 'ППв',
        'accounting_article': '70',
        'cad_num': 'test_new2',
        'unom': None, 
        'un_kv': None,
        'area_id': json.dumps({'2001' : {}}),
        'status_id' : 1
    },
    10 : {
        'affair_id': 1002,
        'order_id': 5006,
        'is_cancelled': False,
        'article_code': '7002',
        'collateral_type': 'ППвк',
        'accounting_article': '70',
        'cad_num': 'test_new2',
        'unom': None, 
        'un_kv': None,
        'area_id': json.dumps({'2001' : {}}),
        'status_id' : 1
    },
}