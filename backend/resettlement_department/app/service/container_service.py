import requests
import os
import logging
import openpyxl
import pandas as pd
from repository.database import get_db_connection
from datetime import datetime


# Настраиваем логирование
logging.basicConfig(
    filename='app_container.log',          # Имя файла, куда будут записываться логи
    level=logging.INFO,                    # Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Формат сообщений
)

def upload_container(history_id, file_path):
    """
    Загружает файл на сервер по указанному пути.
    :param history_id: ID истории для формирования имени файла.
    :param file_path: Полный путь к файлу для загрузки.
    :return: Код статуса HTTP-ответа.
    """
    url = "http://webspd.mlc.gov/SpdRemote/spdremotemvc/MassStart/Parse"
    login, password = "GabitovDS", "21v1DF43!!!!"
    logging.info('Начало загрузки файла')

    try:
        with open(file_path, "rb") as file:
            # Данные формы
            data = {
                "selectedMassObjectType": "1",
                "reglamentId": "934",
                "klassIndex": "801-402",
            }
            logging.info(f'Файл для загрузки: {file_path}')

            # Файл для загрузки
            files = {
                "file": (f"container_{history_id}.xlsx", file, 
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            }
            logging.info(f'Файл подготовлен: {files}')

            # Выполнение POST-запроса
            response = requests.post(url, data=data, files=files, auth=(login, password))

            logging.info(f'Ответ сервера: {response.status_code}')
            return response.status_code
    except FileNotFoundError:
        logging.error(f"Файл {file_path} не найден.")
        return 404
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
        return 500

def generate_excel_from_two_dataframes(history_id, output_dir="./uploads", new_selected_addresses=None, old_selected_addresses=None,
                                       new_selected_districts=None, old_selected_districts=None,
                                       new_selected_areas=None, old_selected_areas=None, date=False):
    """
    Генерирует Excel-файл и загружает его на сервер.
    :param history_id: ID истории для формирования имени файла.
    :param output_dir: Директория для сохранения файла.
    :param new_selected_addresses: Список новых адресов.
    :param old_selected_addresses: Список старых адресов.
    :param date: Флаг для включения даты.
    :return: Код статуса HTTP-ответа от сервера.
    """
    # Проверка и создание директории, если её нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Формируем полный путь к файлу
    file_name = f"container_{history_id}.xlsx"
    output_path = os.path.join(output_dir, file_name)

    # Создаем соединение с базой данных
    connection = get_db_connection()
    cursor = connection.cursor()

    # Основной запрос
    query = """
        SELECT ol.house_address, ol.apart_number, ol.type_of_settlement, ol.kpu_number, new_apart_id, 
               n.house_address, n.apart_number, n.full_living_area, n.total_living_area, n.room_count, 
               n.living_area, n.floor, cin_address, cin_schedule, dep_schedule, phone_osmotr, phone_otvet,  nd.unom, start_date, cin.otdel
        FROM offer o
        JOIN family_apartment_needs nd USING (family_apartment_needs_id)
        JOIN family_structure ol USING (affair_id)
        JOIN new_apart n USING (new_apart_id)
        JOIN cin ON cin.old_address = ol.house_address
        WHERE ol.is_queue <> 1
    """
    params = []

    # Добавляем условия в зависимости от входных параметров
    if old_selected_addresses:
        query += " AND ol.house_address IN %s"
        params.append(tuple(old_selected_addresses))
    if new_selected_addresses:
        query += " AND n.house_address IN %s"
        params.append(tuple(new_selected_addresses))

    # Выполняем запрос
    cursor.execute(query, params)
    aparts = cursor.fetchall()

    # Создаем DataFrame из результатов запроса
    df = pd.DataFrame(aparts, columns=[
        'old_address', 'old_number', 'type_of_settlement', 'kpu_number', 'new_apart_id', 
        'new_address', 'new_number', 'full_living_area', 'total_living_area', 'room_count', 
        'living_area', 'floor', 'cin_address', 'cin_schedule', 'dep_schedule', 'phone_osmotr', 'phone_otvet', 'unom', 'start_date', 'otdel'
    ])

    # Создаем новую книгу Excel и выбираем активный лист
    wb = openpyxl.Workbook()
    sheet = wb.active

    # Определяем заголовки на русском и английском
    russian_headers = [
        "Номер заявки", "Заявитель.Тип (1=ФЛ,2=ЮЛ,3=ИП)", "Заявитель.Порядковый номер", "Заявитель.Имя",
        "Заявитель.Наименование юр.лица", "Заявитель.Почтовый адрес. Адрес строкой", "Заявитель.Почтовый адрес. Индекс",
        "Заявитель.Почтовый адрес. Населенный пункт", "Помещение. Кадастровый номер", "Помещение. Адресный ориентир",
        "Помещение. Площадь общая", "Помещение. Площадь жилая", "Помещение. Этаж", "Помещение. Количество комнат",
        "Помещение. Площадь Жилого помещения", "Помещение. Статус помещения", "Помещение. Идентификатор источника",
        "Свед.о действ.отнош. Номер", "Доп.параметр.Имя", "Доп.параметр.Значение", "Идентификатор документа для автогенерации"
    ]
    english_headers = [
        "NumPP", "appApplicantList.type", "appApplicantList.tab", "appApplicantList.firstname", "appApplicantList.name",
        "appApplicantList.postAddressList.address", "appApplicantList.postAddressList.index", "appApplicantList.postAddressList.locality",
        "flatList.cadastralNumber", "flatList.address", "flatList.square", "flatList.livingSquare", "flatList.floorNumber",
        "flatList.room_number", "flatList.sDwellingArea", "flatList.flatStatus", "flatList.sourceid", "actDocList.documentNumber",
        "customInputDataList.tagName", "customInputDataList.value", "reportID"
    ]

    # Заполняем первую строку русскими заголовками
    for col_num, header in enumerate(russian_headers, 1):
        sheet.cell(row=1, column=col_num, value=header)

    # Заполняем вторую строку английскими идентификаторами
    for col_num, header in enumerate(english_headers, 1):
        sheet.cell(row=2, column=col_num, value=header)

    # Дополнительные значения и тексты для столбцов
    additional_values = ["VSOOTVET", "INFO_SOB", "ISPOLNITEL", "OSMOTR", "GETKEY", "OTVET"]

    # Заполняем данные из DataFrame
    row_num = 3  # Начинаем с третьей строки
    for index, row in df.iterrows():
        report_id = 49101 if row['type_of_settlement'] == "частная собственность" else 49181

        for i, tag in enumerate(additional_values):
            additional_texts = {
                "VSOOTVET": f"Согласно постановлению Правительства Москвы от 01.08.2017 № 497-ПП «О программе реновации жилищного фонда в городе Москве» (далее - Программа реновации) в отношении многоквартирного дома по адресу: г. Москва, {row['old_address']} принято решение о включении в Программу реновации.",
                "INFO_SOB": """- заявление о включении в предмет Договора предлагаемого жилого помещения;
                - оригиналы документов личного характера и правоустанавливающие документы на освобождаемое жилое помещение.
                Просим довести указанную в письме информацию до всех правообладателей.""",
                "ISPOLNITEL": "Тест",
                "OSMOTR": f"""Для осмотра квартиры необходимо {('с ' + (str(row['start_date'])[5:7] + '.' + str(row['start_date'])[8:] + '.' +str(row['start_date'])[:4])) if row['start_date'] != None and row['start_date'] > datetime.now().date() else '' } в течение 7 рабочих дней обратиться в инф. центр по адресу: г. Москва, {row['cin_address']} ({row['cin_schedule']}) по пред. записи онлайн на сайте https://www.mos.ru/ в разделе «Осмотр квартиры» (для перехода наведите камеру смартфона на QR~код) или по тел. {row['phone_osmotr']}""" if row['cin_schedule'] != 'time2plan' else "Предварительная запись на показ жилого помещения доступна на сервисе онлайн-записи «Время планировать вместе с ДГИ»: https://time2plan.online.",
                "GETKEY": " ",
                "OTVET": f"Всем правообладателям необходимо предоставить свое согласие либо отказ от предлагаемого жилого помещения в срок не позднее 7 рабочих дней в инф. центр по адресу: г. Москва, {row['cin_address'] if row['dep_schedule']!= 'отдел' else row['otdel']} {('(' + row['dep_schedule'] + ')') if row['dep_schedule']!= 'отдел' else ''}, по пред. записи по вышеуказанному тел., при себе необходимо иметь следующие документы:"
            }

            # Номер заявки
            sheet.cell(row=row_num, column=1, value=index + 1)

            if i == 0:  # Первая строка каждой группы
                sheet.cell(row=row_num, column=2, value=1)  # appApplicantList.type
                sheet.cell(row=row_num, column=3, value=1)  # appApplicantList.tab
                sheet.cell(row=row_num, column=4, value="Уважаемый правообладатель!")  # appApplicantList.firstname
                sheet.cell(row=row_num, column=6, value=f"{row['old_address']} кв. {row['old_number']}")  # Адрес
                sheet.cell(row=row_num, column=7, value=124365)  # Индекс
                sheet.cell(row=row_num, column=8, value="г. Москва")  # Населенный пункт
                sheet.cell(row=row_num, column=9, value='тест')  # Кадастровый номер
                sheet.cell(row=row_num, column=10, value=f"{row['new_address']} кв. {row['new_number']}")  # flatList.address

                # Заполняем данные flatList
                sheet.cell(row=row_num, column=11, value=row['full_living_area'])  # flatList.square
                sheet.cell(row=row_num, column=12, value=row['total_living_area'])  # flatList.livingSquare
                sheet.cell(row=row_num, column=13, value=row['floor'])  # flatList.floorNumber
                sheet.cell(row=row_num, column=14, value=row['room_count'])  # flatList.room_number
                sheet.cell(row=row_num, column=15, value=row['living_area'])  # flatList.sDwellingArea
                sheet.cell(row=row_num, column=16, value=3)  # flatList.flatStatus
                sheet.cell(row=row_num, column=17, value=row['new_apart_id'])  # flatList.sourceid
                sheet.cell(row=row_num, column=18, value=row['kpu_number'])  # actDocList.documentNumber
                sheet.cell(row=row_num, column=21, value=report_id)  # reportID

            sheet.cell(row=row_num, column=19, value=tag)  # customInputDataList.tagName
            sheet.cell(row=row_num, column=20, value=additional_texts[tag])  # customInputDataList.value

            row_num += 1

    # Сохраняем файл
    wb.save(output_path)
    logging.info(f"Excel файл '{output_path}' создан.")
    connection.close()

    # Загружаем файл на сервер
    #return upload_container(history_id, output_path)

