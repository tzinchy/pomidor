import urllib
import psycopg2
import requests
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from core.config import settings, RSM
import time
import uuid
import random
import string
from datetime import datetime, timedelta
import multiprocessing
from urllib.parse import urlencode, urljoin
from concurrent.futures import ProcessPoolExecutor, as_completed


def generate_key():
    """
    Generates unique session key
    which required to the search request for identification responses
    in RSM
    :return:
    """
    # Генерация UUID
    uuid_part = str(uuid.uuid4())
    # Генерация случайных символов
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    # Объединение частей
    key = f"{uuid_part}-{random_part}"
    return key


def process_date_range(dates):
    """
    Converter to the RSM request format
    :param dates:
    :return:
    """
    try:
        # Преобразуем даты в формат datetime
        date_objects = []

        for date_str in dates:
            if isinstance(date_str, str):

                if '.' in date_str:  # Формат dd.mm.yyyy
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                elif '-' in date_str:  # Формат yyyy-mm-dd
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    raise ValueError(f"Неподдерживаемый формат даты: {date_str}")
                date_objects.append(date_obj)

            else:
                date_objects.append(date_str)


        # Убедимся, что список содержит ровно 2 даты
        if len(date_objects) != 2:
            raise ValueError("Ожидался список ровно из двух дат")

        # Сортируем даты (меньшая -> первая, большая -> вторая)
        date_objects.sort()

        # Меньшая дата
        date_start = date_objects[0].strftime("%Y-%m-%dT%H:%M:%S")

        # Большая дата с временем 23:59:59
        date_end = (date_objects[1] + timedelta(hours=23, minutes=59, seconds=59)).strftime("%Y-%m-%dT%H:%M:%S")

        return date_start, date_end
    except ValueError as e:
        return f"ERROR: {e}", f"ERROR: {e}"


def get_cookie():
    """
    Request for the new auth token
    Login and Password required in .env
    :return:
    """

    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0,
             "download.prompt_for_download": False,
             "directory_upgrade": True,
             "safebrowsing.enabled": True,
             "safebrowsing.disable_download_protection": True}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable_web_security")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # driver = webdriver.Chrome()
    driver.get(RSM.PING_LINK)
    try:
        WebDriverWait(driver, 600).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login"]'))).click()
        driver.find_element(By.XPATH, '//*[@id="login"]').send_keys(RSM.LOGIN)
    except:
        print("Timed out waiting for page to load")
    time.sleep(3)
    try:
        WebDriverWait(driver, 600).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="password"]'))).click()
        driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(RSM.PASS)
    except:
        print("Timed out waiting for page to load")
    time.sleep(3)
    driver.find_element(By.XPATH, '//*[@id="bind"]').click()
    cooks = driver.get_cookie('Rsm.Cookie')
    cookie = cooks['value']
    driver.close()
    return cookie


def check_token():
    """
    checks is the token from DB allowed now
    if not - generates a new one
    :return:
    """
    conn_params = {
        "dbname": settings.project_management_setting.DB_NAME,
        "user": settings.project_management_setting.DB_USER,
        "password": settings.project_management_setting.DB_PASSWORD,
        "host": settings.project_management_setting.DB_HOST,
        "port": settings.project_management_setting.DB_PORT
    }

    query = "SELECT value FROM env.env WHERE name = 'rsm_token' LIMIT 1;"

    try:

        with psycopg2.connect(**conn_params) as conn:

            with conn.cursor() as cursor:

                cursor.execute(query)
                result = cursor.fetchone()

                if result:

                    value = result[0]
                    print(f"Value: {value}")

                else:

                    print("No value found.")

    except psycopg2.Error as e:

        print(f"Database error: {e}")

    response = requests.get(RSM.PING_LINK, cookies={'Rsm.Cookie': value},
                            allow_redirects=False)

    if response.status_code == 200:
        return value
    elif response.status_code == 302:
        token = get_cookie()
        print(token)

        query = f"""UPDATE env.env
                SET value = '{token}'
                WHERE name = 'rsm_token';
                """

        try:

            with psycopg2.connect(**conn_params) as conn:

                with conn.cursor() as cursor:

                    cursor.execute(query)
                    conn.commit()

        except psycopg2.Error as e:

            print(f"Database error: {e}")

        return token
    else:
        return None


def send_request(url, cookie):
    try:
        requests.get(url, cookies={'Rsm.Cookie': cookie})
    except requests.exceptions.RequestException as e:
        print(e)
        pass


def get_row_count(dates, dates_type, category, session_key, layout_id, cookie, registered=None):
    """
    search a row count in requested data
    :param dates:
    :param dates_type:
    :param category:
    :param session_key:
    :param layout_id:
    :param cookie:
    :param registered:
    :return:
    """

    dates[0], dates[1] = dates

    if dates_type == 1:
        search_link, count_link = search_kpu(session_key, layout_id,
                                             kpu_direction=category, decl_date=dates,
                                             registered=registered)
    elif dates_type == 2:
        search_link, count_link = search_kpu(session_key, layout_id,
                                             kpu_direction=category, reason2_calc=dates,
                                             registered=registered)
    elif dates_type == 3:
        search_link, count_link = search_kpu(session_key, layout_id,
                                             kpu_direction=category, reason2_date_resolution=dates,
                                             registered=registered)
    elif dates_type == 4:
        search_link, count_link = search_kurs_living_space(dates, layout_id, session_key)

    # a = requests.get(search_link,
    #                  cookies={'Rsm.Cookie': cookie})

    p = multiprocessing.Process(target=send_request, args=(search_link, cookie,))
    p.daemon = True  # Позволяет процессу завершаться вместе с родителем
    p.start()
    time.sleep(3)
    print("____40__")
    c = requests.get(count_link,
                     cookies={'Rsm.Cookie': cookie})
    count = int(c.text)
    print(count)
    return count


def split_interval(dates, dates_type, category, cookie, max_rows=1500, registered=None):
    """
    makes an intervals of dates for searching only less then 1500 rows of result at one request
    :param dates:
    :param dates_type:
    :param category:
    :param cookie:
    :param max_rows:
    :param registered:
    :return:
    """
    result_intervals = []

    # Получаем session_key для текущего процесса
    session_key = generate_key()

    # Получаем количество строк для данного интервала

    row_count = get_row_count(dates, dates_type, category, session_key, RSM.COUNTER_LAYOUT, cookie, registered)

    # Если количество строк меньше max_rows, добавляем интервал в результат
    if row_count <= max_rows:
        result_intervals.append((dates[0], dates[1], row_count))
    else:
        # Определяем количество частей, на которые нужно разделить интервал
        num_parts = (row_count // max_rows) + 1
        interval_duration = (dates[1] - dates[0]) / num_parts

        # Используем ProcessPoolExecutor для многопроцессорности
        with ProcessPoolExecutor(max_workers=50) as executor:
            future_intervals = []

            # Делим интервал на `num_parts` частей и отправляем каждую часть в параллельный процесс
            for ii in range(num_parts):
                part_start = dates[0] + ii * interval_duration
                part_end = dates[0] + (ii + 1) * interval_duration - timedelta(seconds=1)

                # Округляем границы подинтервала до секунд
                part_start = part_start.replace(microsecond=0)
                part_end = part_end.replace(microsecond=0)


                # Запускаем split_interval в отдельном процессе, передавая новый session_key
                future = executor.submit(split_interval, [part_start, part_end], dates_type,
                                         category, cookie, max_rows, registered)
                future_intervals.append(future)

            # Собираем результаты из всех завершённых задач
            for future in as_completed(future_intervals):
                result_intervals.extend(future.result())

    return result_intervals


def split_interval_ids(interval, interval_type, cookie, max_rows=1500, registered=None, category=None):
    """
    Разбивает числовой интервал на поддиапазоны, чтобы в одном запросе не запрашивалось более max_rows строк.
    :param interval: Список [start, end] с целочисленными границами.
    :param interval_type: Тип интервала.
    :param category: Категория.
    :param cookie: Куки.
    :param max_rows: Максимальное количество строк в одном запросе.
    :param registered: Дополнительный параметр.
    :return: Список кортежей (start, end, row_count).
    """
    result_intervals = []

    # Получаем session_key для текущего процесса
    session_key = generate_key()

    # Определяем количество строк для данного интервала
    row_count = get_row_count(interval, interval_type, category, session_key, 21744, cookie, registered)
    print(row_count)

    if row_count <= max_rows:
        result_intervals.append((interval[0], interval[1], row_count))
    else:
        # Определяем количество частей, на которые нужно разделить интервал
        num_parts = (row_count // max_rows) + 1
        interval_size = (interval[1] - interval[0] + 1) // num_parts

        with ProcessPoolExecutor(max_workers=50) as executor:
            future_intervals = []

            for i in range(num_parts):
                part_start = interval[0] + i * interval_size
                part_end = interval[0] + (i + 1) * interval_size - 1

                # Убедимся, что последний интервал заканчивается ровно на границе
                if i == num_parts - 1 or part_end >= interval[1]:
                    part_end = interval[1]
                print(f'интервал {part_start} - {part_end}')

                future = executor.submit(split_interval_ids, [part_start, part_end], interval_type, cookie, max_rows,
                                         registered, category)
                future_intervals.append(future)

            for future in as_completed(future_intervals):
                result_intervals.extend(future.result())

    return result_intervals


def merge_intervals(intervals, dates_type, cookie, category, layout, max_rows=1500, registered=None):
    """
    makes intervals more comfortable for multiprocessing search
    :param intervals:
    :param dates_type:
    :param cookie:
    :param category:
    :param layout:
    :param max_rows:
    :param registered:
    :return:
    """
    intervals.sort(key=lambda x: x[0])
    merged_intervals = []
    current_start = None
    current_end = None
    current_sum = 0

    for start, end, row_count in intervals:
        if current_sum + row_count <= max_rows:
            # Начало нового интервала
            if current_start is None:
                current_start = start
            # Обновляем конец текущего интервала и сумму строк
            current_end = end
            current_sum += row_count
        else:
            # Сохраняем текущий интервал и обнуляем для следующей группы

            merged_intervals.append((current_start, current_end, dates_type, current_sum,
                                     category, generate_key(), cookie, layout, registered))
            current_start = start
            current_end = end
            current_sum = row_count

    # Добавляем последний интервал, если остались неприсоединённые значения
    if current_start is not None:
        merged_intervals.append((current_start, current_end, dates_type, current_sum,
                                 category, generate_key(), cookie, layout, registered))

    return merged_intervals


def merge_intervals_ids(intervals, interval_type, cookie, layout, max_rows=1500, registered=None):
    """
    Объединяет интервалы для более эффективного многопоточного поиска.
    :param intervals: Список кортежей (start, end, row_count).
    :param interval_type: Тип интервала.
    :param cookie: Куки.
    :param category: Категория.
    :param layout: Макет.
    :param max_rows: Максимальное количество строк в одном запросе.
    :param registered: Дополнительный параметр.
    :return: Список объединённых интервалов.
    """
    intervals.sort(key=lambda x: x[0])
    merged_intervals = []
    current_start = None
    current_end = None
    current_sum = 0

    for start, end, row_count in intervals:
        if current_sum + row_count <= max_rows:
            if current_start is None:
                current_start = start
            current_end = end
            current_sum += row_count
        else:
            merged_intervals.append((current_start, current_end, interval_type, current_sum,
                                     None, generate_key(), cookie, layout, registered))
            current_start = start
            current_end = end
            current_sum = row_count

    if current_start is not None:
        merged_intervals.append((current_start, current_end, interval_type, current_sum,
                                 None, generate_key(), cookie, layout, registered))

    return merged_intervals


def get_rsm(date_start, date_end, dates_type, category, session_key, cookie, layout_id, registered):
    """
    takes an info from RSM
    :param date_start:
    :param date_end:
    :param dates_type:
    :param category:
    :param session_key:
    :param cookie:
    :param layout_id:
    :param registered:
    :return:
    """
    df = pd.DataFrame
    dates = [date_start, date_end]
    if dates_type == 1:
        search_link, count_link = search_kpu(session_key, layout_id,
                                             kpu_direction=category, decl_date=dates,
                                             registered=registered)
    elif dates_type == 2:
        search_link, count_link = search_kpu(session_key, layout_id,
                                             kpu_direction=category, reason2_calc=dates,
                                             registered=registered)
    elif dates_type == 3:
        search_link, count_link = search_kpu(session_key, layout_id,
                                             kpu_direction=category, reason2_date_resolution=dates,
                                             registered=registered)
    elif dates_type == 4:
        search_link, count_link = search_kurs_living_space(dates, layout_id, session_key)

    a = requests.get(search_link,
                     cookies={'Rsm.Cookie': cookie})
    if a.status_code != 503:
        jsonn = json.loads(a.text)
        if jsonn['Data'] != 'The service is unavailable.':
            df = pd.DataFrame(jsonn['Data'])
            i = 0
            while i < 50:
                b = requests.get(f'http://webrsm.mlc.gov:5222/Registers/GetAddData?registerId=KursKpu&uniqueSessionKey={session_key}',
                                 cookies={'Rsm.Cookie': cookie})
                jsonn = json.loads(b.text)
                df1 = pd.DataFrame(jsonn['Data'])
                df = pd.concat([df, df1], axis=0)
                # print(b.text)
                if len(df) > 1500:
                    print('warning! not all kpus are downloadet at ', date_start, '-', date_end)
                if df1.empty:
                    i = 50
                i = i + 1
    return df


def new_kpu(intervals):
    """
    starts a multiprocessing with get_rsm func
    :param intervals:
    :return:
    """
    pool_size = min(50, len(intervals))
    with multiprocessing.Pool(processes=pool_size) as pool:
        args = [(interval[0], interval[1], interval[2], interval[4], interval[5], interval[6], interval[7], interval[8])
                for interval in intervals]
        results = pool.starmap(get_rsm, args)
    # Объединение всех датафреймов в один
    combined_df = pd.concat(results, ignore_index=True)
    combined_df.drop(columns='Selected', inplace=True)
    combined_df.drop_duplicates(inplace=True)

    return combined_df


def search_kpu(
        session_key,
        layout_id,
        kpu_num=None,
        # list of directions
        kpu_direction=None,
        registered=None,
        affair_grlgot=None,
        # list, if interval - [start_year, end_year], if value [year] Год постановки на учет
        stand_year=None,
        # list, if interval - [start_date, end_date], if value [date] Дата заявления о постановке на учет
        decl_date=None,
        # list, if interval - [start_date, end_date], if value [date] Дата операции снятия с учета
        reason2_calc=None,
        # list, if interval - [start_date, end_date], if value [date] Дата распоряжения о снятии с учета
        reason2_date_resolution=None
                ):
    """
    makes a search and search_count links for the RSM requests
    :param session_key:
    :param layout_id:
    :param kpu_num:
    :param kpu_direction:
    :param registered:
    :param affair_grlgot:
    :param stand_year:
    :param decl_date:
    :param reason2_calc:
    :param reason2_date_resolution:
    :return:
    """

    search_data = []
    search_dynamic_control_data = []

    try:

        if kpu_direction:
            s_data = {
                "key": "KpuDirection",
                "value": f"{str(kpu_direction)}"
            }
            search_data.append(s_data)

        if registered is not None:
            if registered is True:
                s_data = {
                    "key": "InList",
                    "value": "true"
                }
                search_data.append(s_data)

            elif registered is False:
                s_data = {
                    "key": "Free",
                    "value": "true"
                }
                search_data.append(s_data)

        if decl_date is not None:

            if len(decl_date) == 2:
                start_date, end_date = process_date_range(decl_date)

                if 'ERROR' in start_date:
                    raise ValueError('Date formatting error')

                dyn_con_data = {
                    "IdControl": "DECL_DATE",  # Идентификатор фильтра по дате
                    "ControlType": "DynamicDate",  # Тип фильтра (динамическая дата)
                    "IdAttribute": "43608400",  # Идентификатор атрибута
                    "From": start_date,  # Начальная дата интервала
                    "To": end_date  # Конечная дата интервала
                }

                search_dynamic_control_data.append(dyn_con_data)

    except ValueError as e:
        print(e)
        return f'ERROR {e}'

    formatted_search_data = {}
    for index, item in enumerate(search_data):
        formatted_search_data[f"searchData[{index}].key"] = item["key"]
        formatted_search_data[f"searchData[{index}].value"] = str(item["value"]).lower()

    get_count_params = {
            "RegisterId": "KursKpu",  # Идентификатор реестра
            "SearchApplied": "true",  # Поиск активен (true)
            "PageChanged": "false",  # Страница не менялась
            "Page": 1,  # Номер страницы
            "PageSize": 30,  # Размер страницы
            "SelectAll": "false",  # Все записи не выбраны
            "ClearSelection": "false",  # Сброс выбора не применён
            "RegisterViewId": "KursKpu",  # Идентификатор представления реестра
            "LayoutRegisterId": "0",  # Идентификатор макета реестра (0 - по умолчанию)
            "FilterRegisterId": "0",  # Идентификатор фильтра реестра (0 - не задан)
            "ListRegisterId": "0",  # Идентификатор списка реестра (0 - не задан)
            "searchData": search_data,
            "SearchDynamicControlData": json.dumps(search_dynamic_control_data),
            "databaseFilters": [],  # База фильтров (пусто)
            "selectedLists": [],  # Списки, выбранные пользователем (пусто)
            "UniqueSessionKey": session_key,  # Уникальный ключ сессии
            "UniqueSessionKeySetManually": "true",  # Уникальный ключ установлен вручную
            "ContentLoadCounter": 1,  # Счётчик загрузки контента
            "CurrentLayoutId": layout_id  # Текущий макет (ID макета)
        }

    get_data_params_1 = {
        "sort": "",  # Параметр сортировки (не задан)
        "page": 1,  # Номер страницы данных
        "pageSize": 30,  # Количество записей на странице
        "group": "",  # Группировка данных (не задана)
        "filter": "",  # Фильтр данных (не задан)
        "RegisterId": "KursKpu",  # Идентификатор реестра
        "SearchApplied": "true",  # Поиск активен (обязательно строка для корректной сборки)
        "PageChanged": "false",  # Страница не менялась (обязательно строка для корректной сборки)
        "SelectAll": "false",  # Все записи не выбраны (обязательно строка для корректной сборки)
        "ClearSelection": "true",  # Сброс выбора записей активирован (обязательно строка для корректной сборки)
        "LayoutId": layout_id,  # Идентификатор текущего макета
        "RegisterViewId": "KursKpu",  # Идентификатор представления реестра
        "LayoutRegisterId": "0",  # Идентификатор макета реестра
        "FilterRegisterId": "0",  # Идентификатор фильтра реестра
        "ListRegisterId": "0"
    }

    get_data_params_2 = {
        "SearchDynamicControlData": search_dynamic_control_data,
        "UniqueSessionKey": session_key,  # Уникальный ключ сессии
        "UniqueSessionKeySetManually": "true",  # Уникальный ключ установлен вручную
        "ContentLoadCounter": "1"  # Счётчик загрузки контента
    }

    get_data_params_1.update(formatted_search_data)
    get_data_params_1.update(get_data_params_2)

    url_data = "http://webrsm.mlc.gov:5222/Registers/GetData"
    url_count = "http://webrsm.mlc.gov:5222/Registers/GetCount"
    query_string = urlencode(get_data_params_1)

    get_count_params_json = json.dumps(get_count_params)

    query_string_count = urlencode({"parametersJson": get_count_params_json,
                                    "registerId": "KursKpu",
                                    "uniqueSessionKey": session_key})
    # Сборка полного URL
    full_url = urljoin(url_data, f"?{query_string}")
    full_url_count = urljoin(url_count, f"?{query_string_count}")

    return full_url, full_url_count


def search_kurs_living_space(apart_id_interval, layout_id: int, session_key: str):
    '''
    small function for making links only for apart_id intervals in KursLivigSpace
    with Распорядитель_П8=11,12,30,81 and Незаселена
    in the next versions will be refactored in the same way with the search_kpu function... may be))
    layout_id required
    :param apart_id_interval:
    :param layout_id: int
    :param session_key: str
    :return:
    '''

    base_url_search = "http://webrsm.mlc.gov:5222/Registers/GetData"
    base_url_count = "http://webrsm.mlc.gov:5222/Registers/GetCount"

    # params for GetData query
    params_search = {
        "sort": "",
        "page": 1,
        "pageSize": 30,
        "group": "",
        "filter": "",
        "RegisterId": "KursLivingSpace",
        "SearchApplied": "true",
        "PageChanged": "false",
        "SelectAll": "false",
        "ClearSelection": "true",
        "LayoutId": f"{layout_id}",
        "RegisterViewId": "KursLivingSpace",
        "LayoutRegisterId": "0",
        "FilterRegisterId": "0",
        "ListRegisterId": "0",
        "SearchDataNewDesign": urllib.parse.quote(json.dumps([
            {
                "typeControl": "value",
                "type": "BOOLEAN",
                "text": "Распорядитель_П8=11,12,30,81",
                "textValue": "Да",
                "value": 1,
                "id": 43726400,
                "allowDelete": True  # Булево значение
            },
            {
                "typeControl": "value",
                "type": "BOOLEAN",
                "text": "Незаселена",
                "textValue": "Да",
                "value": 1,
                "id": 43726700,
                "allowDelete": True  # Булево значение
            },
            {
                "typeControl": "range",
                "text": "Сл.инф_APART_ID",
                "textValue": f"c {apart_id_interval[0]} до {apart_id_interval[1]}",
                "type": "INTEGER",
                "from": str(apart_id_interval[0]),
                "to": str(apart_id_interval[1]),
                "id": 43705100
            }
        ], ensure_ascii=False, separators=(',', ':')), safe=''),
        "UniqueSessionKey": f"{session_key}",
        "UniqueSessionKeySetManually": "true",
        "ContentLoadCounter": "1"
    }

    # params for GetCount query
    get_count_params = {
        "RegisterId": "KursLivingSpace",
        "SearchApplied": "true",
        "PageChanged": "false",
        "Page": 1,
        "PageSize": 30,
        "SelectAll": "false",
        "ClearSelection": "false",
        "LayoutId": f"{layout_id}",
        "RegisterViewId": "KursLivingSpace",
        "LayoutRegisterId": "0",
        "FilterRegisterId": "0",
        "ListRegisterId": "0",
        "SearchDataNewDesign": json.dumps([
            {
                "typeControl": "value",
                "type": "BOOLEAN",
                "text": "Распорядитель_П8=11,12,30,81",
                "textValue": "Да",
                "value": 1,
                "id": 43726400,
                "allowDelete": "true"
            },
            {
                "typeControl": "value",
                "type": "BOOLEAN",
                "text": "Незаселена",
                "textValue": "Да",
                "value": 1,
                "id": 43726700,
                "allowDelete": "true"
            },
            {
                "typeControl": "range",
                "text": "Сл.инф_APART_ID",
                "textValue": f"c {apart_id_interval[0]} до {apart_id_interval[1]}",
                "type": "INTEGER",
                "from": f"{apart_id_interval[0]}",
                "to": f"{apart_id_interval[1]}",
                "id": 43705100,
                "allowDelete": "true"
            }
        ], ensure_ascii=False, separators=(',', ':')),
        "databaseFilters": [],
        "selectedLists": [],
        "UniqueSessionKey": f"{session_key}",
        "UniqueSessionKeySetManually": "true",
        "ContentLoadCounter": 1,
        "CurrentLayoutId": f"{layout_id}"
    }

    get_count_params_json = json.dumps(get_count_params, ensure_ascii=False)

    query_string_search = urlencode(params_search, safe=':/')
    query_string_count = urlencode({"parametersJson": get_count_params_json,
                                    "registerId": "KursKpu",
                                    "uniqueSessionKey": session_key})

    full_url_search = urljoin(base_url_search, f"?{query_string_search}")
    full_url_count = urljoin(base_url_count, f"?{query_string_count}")

    return full_url_search, full_url_count


def get_kpu(
        start_date: datetime,
        end_date: datetime,
        date_type: int,
        category: list,
        layout_id: int,
        registered: bool = None,
):
    """

    :param start_date - дата начала отрезка:
    :param end_date - дата конца отрезка:
    :param date_type - тип даты. 1 - Дата заявления о постановке на учет,
    2 - Дата снятия с учета,
    3 - Дата распоряжения о снятии с учета:
    :param category - список направлений учета (направления integer):
    :param layout_id - Идентификатор раскладки:
    :param registered - Состоит на учете True, False, None:
    :return dataframe:
    """

    token = check_token()
    result = split_interval([start_date, end_date], date_type, category, token, registered=registered)
    merged_intervals = merge_intervals(result, date_type, token, category, layout_id, registered=registered)

    return new_kpu(merged_intervals)


def get_kurs_living_space(ids, layout_id):
    """
    gets dataframe from RSM with apartment resource by interval of APART_ID
    :param ids:
    :param layout_id:
    :return:
    """

    token = check_token()
    result = split_interval_ids(ids, 4, token)
    intervals = merge_intervals_ids(result, 4, token, layout_id)
    df = new_kpu(intervals)

    return df


if __name__ == '__main__':
    start = datetime.now()
    # token = check_token()
    # result = split_interval_ids([999, 99999999], 4, token)
    # print(merge_intervals_ids(result, 4, token, 21744))

    # df = get_kurs_living_space([999, 99999999], 21744)
    # df.to_excel("/Users/macbook/Downloads/resurs_test.xlsx")
    # print(datetime.now() - start)

    # print(split_interval_ids([999, 99999999], 4, check_token()))
    # print(search_kurs_living_space([999, 99999999], 21744, generate_key()))
    # print(check_token())
    category = [70, 91]
    layout_id = 22223 # usually use 21705
    start_date = datetime(2017, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 12, 31, 23, 59, 59)
    df = get_kpu(start_date, end_date, 1, category, layout_id)
    # search_kpu(generate_key(), 21703, registered=True, kpu_direction=[1], decl_date=['01.01.2020', '31.12.2020'])

