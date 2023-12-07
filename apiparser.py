import os
import requests
import sqlite3
import pandas as pd

from dotenv import load_dotenv
from datetime import datetime


load_dotenv()


def change_data(data_string):
    ymd = data_string[:10].replace('.', '')
    time = data_string[-7:].replace(':', '')
    year = int(ymd[-4:])
    month = int(ymd[2:4])
    day = int(ymd[:2])
    hours = int(time[0])
    mins = int(time[1:3])
    second = int(time[-2:])
    final_date = datetime(year, month, day, hours, mins, second)
    date = datetime.strftime(final_date, '%Y-%m-%d %H:%M:%S')
    return date


def get_devices():
    """Фукнция получающая данные из api endpoint EnumDevices"""
    request = requests.get(os.getenv('ENUM_DEVICES'), params={
        "Session": os.getenv('SESSION'),
        "SchemaID": "9a342527-4e13-4fc2-a95c-269f741d4f76"
    })
    return request.json()['Items']


def get_stage(sd, ed):
    """Фукнция получающая данные из api endpoint GetStage"""
    request_2 = requests.get(os.getenv('GET_STAGE'), params={
        "Session": os.getenv('SESSION'),
        "SchemaID": os.getenv('SCHEMA_ID'),
        'IDs': os.getenv('IDS'),
        'SD': sd,
        'ED': ed,
        "StageName": "Tank*"
    })
    return request_2.json()


def get_api_data(second_response):
    """Функция запысывает данные из API(Уровень топлива,
     дата и время начало заправки, дата и время конец заправки,ID)"""
    tank = []
    for key in second_response.keys():
        new = second_response[key]
        if isinstance(new, dict):
            if 'Tank1FuelUpDnVol' in new['Params']:
                index = new['Params'].index('Tank1FuelUpDnVol')
                time = new['Params'].index('DateTimeFirst')
                last_time = new['Params'].index('DateTimeLast')
                value = new['Items']
                for item in value:
                    if item["Caption"] == 'Заправка':
                        tank_value = item['Values'][index]
                        start_of_refueling = item['Values'][time]
                        end_of_refueling = item['Values'][last_time]
                        start_of_refueling = change_data(start_of_refueling)
                        end_of_refueling = change_data(end_of_refueling)
                        tank.append((tank_value, start_of_refueling, end_of_refueling, key))
    return tank


def get_id_and_serial():
    """Функция записывает данные из API(Серийный номер, ID датчика уровня топлива) с словарь"""
    ids = []
    for item in get_devices():
        ids.append((item['Serial'], item['ID']))
    return ids


def get_total_value(stage):
    """Функция записывает данные из API(Уровень топлива за начало периода, уровень топлива в конце периода,
    общее количество топлива, ID)"""
    tank_total = []
    for key in stage.keys():
        new = stage[key]
        if isinstance(new, dict):
            if 'Tank1FuelUpDnVol' in new['Params']:
                fuel_value = new['Total']
                tank_first = fuel_value["Tank1FuelLevelFirst"]
                tank_last = fuel_value["Tank1FuelLevelLast"]
                total_tank = fuel_value["Tank1FuelUpVolDiff"]
                tank_total.append((tank_first, tank_last, total_tank, key))
    return tank_total


# def apps():
#     get_devices()
#     get_stage(SD, ED)
#     get_api_data(get_stage(SD, ED))
#     get_id_and_serial()
#     get_total_value(get_stage(SD, ED))

connect = sqlite3.connect('test.db')

cursor = connect.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS car (
id INTEGER PRIMARY KEY AUTOINCREMENT,
car_name TEXT,
car_number TEXT,
car_id INTEGER,
car_id_navigation TEXT
)
''')

cursor.execute("""
CREATE TABLE IF NOT EXISTS benz (
time TEXT,
car_name TEXT,
car_id TEXT,
litre INTEGER,
fuel_type TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS api (
tank_value INTEGER,
SD TEXT,
ED TEXT,
IDs TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ids (
serial INTEGER,
ids text
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS total_tank (
tank_first INTEGER,
tank_last INTEGER,
tank_tootal INTEGER,
ids TEXT
)
""")

cursor.execute("""
DELETE FROM car
""")

cursor.execute("""
DELETE FROM benz
""")

cursor.execute("""
DELETE FROM api
""")

cursor.execute("""
DELETE FROM ids
""")

cursor.execute("""
DELETE FROM total_tank
""")


def get_id_card(exel_file):
    """Функция получает данные из exel файла и записывает данные в sql таблицу car"""
    df = pd.read_excel(exel_file)
    df.to_sql('car', connect, index=False, if_exists='replace')
    return df


def get_benz_file(benz_xml_file):
    """Функция получает данные из xml файла и записывает данные в sql таблицу benz"""
    benz = pd.read_xml(benz_xml_file, xpath='.//filling')
    benz_df = pd.DataFrame(benz)
    benz_df['time'] = benz_df['time'].apply(change_data)
    keys_for_benz = ['time', 'user_name', 'rfid_key', 'litre', 'type']
    benz_df[keys_for_benz].to_sql('benz', connect, if_exists='replace', index=False)
    return benz_df


def from_api_to_sql_tank(tank):
    """Функция записывает данные из функции get_api_data в sql таблицу api"""
    api_df = pd.DataFrame(data=tank, columns=['tank_value', 'sd', 'ed', 'ids'])
    api_df.to_sql('api', connect, if_exists='replace', index=False)
    return api_df


def from_api_to_sql_id_serial(ids):
    """Функция записывает данные из функции get_id_and_serial в sql таблицу ids"""
    ids_df = pd.DataFrame(data=ids, columns=['serial', 'ids'])
    ids_df.to_sql('ids', connect, if_exists='replace', index=False)
    return ids_df


def from_api_to_sql_tank_total(tank_total):
    """Функция записывает данные из функции get_total_value в sql таблицу total_tank"""
    total_value_df = pd.DataFrame(data=tank_total, columns=['tank_first', 'tank_last', 'tank_total', 'ids'])
    total_value_df.to_sql('total_tank', connect, if_exists='replace', index=False)
    return total_value_df


# WHERE substr(api.ed, 1, length(api.ed) ) = substr(benz.time, 1, length(benz.time) )


def request_sql_from_api():
    """Функция делает запрос к таблицам, достает данные и формирует exel отчет по заправкам на каждый день"""
    sql = cursor.execute("""
    SELECT DISTINCT benz.user_name, benz.litre, ROUND(api.tank_value, 2),  strftime('%Y-%m-%d %H:%M:%S', api.sd,  '3 hours') as new_time, ROUND((((max(benz.litre, api.tank_value) - min(benz.litre, api.tank_value))) / min(benz.litre, api.tank_value)) * 100, 2) as dif
    FROM benz
    JOIN car ON benz.rfid_key = car.car_id_navigation
    JOIN ids ON car.car_id = ids.serial
    JOIN api ON ids.ids = api.ids
    WHERE  date(new_time) = date(benz.time) and strftime('%H', new_time) = strftime('%H', benz.time)
    ORDER BY dif DESC
    """)
    row = sql.fetchall()
    exel_ = pd.DataFrame(data=row, columns=['Название Машины',
                                            'Заправка из АЗС',
                                            'Заправка из API',
                                            'Дата заправки из API',
                                            'Разница в топливе в %'])
    exel_.to_excel('Отчёт по заправкам.xlsx', index=False)
    return exel_


def request_sql_from_api_total():
    """Функция делает запрос к таблицам, достает данные и формирует  сводный exel отчет по заправкам"""
    sql_tank_total = cursor.execute("""
    SELECT benz.user_name, ROUND(total_tank.tank_first, 2), ROUND(total_tank.tank_last, 2), ROUND(total_tank.tank_total, 2), SUM(benz.litre), ROUND((((max(total_tank.tank_total, SUM(benz.litre)) - min(total_tank.tank_total, SUM(benz.litre)))) / min(total_tank.tank_total, SUM(benz.litre))) * 100, 2) as dif
    FROM benz
    JOIN car ON benz.rfid_key = car.car_id_navigation
    JOIN ids ON car.car_id = ids.serial
    JOIN total_tank ON ids.ids = total_tank.ids
    GROUP BY benz.rfid_key
    ORDER BY dif DESC 
    """)
    row_total_tank = sql_tank_total.fetchall()
    total_tank_exel = pd.DataFrame(data=row_total_tank, columns=['Название машины',
                                                                 'Уровень топлива на начало периода по ДУТ (л)',
                                                                 'Уровень топлива на конец периода по ДУТ (л)',
                                                                 'Объем заправки по ДУТ (л)',
                                                                 'Объем заправки из ПО Бенза (л)',
                                                                 'Отклонение заправок (Бенза-ДУТ) %'])

    total_tank_exel.to_excel('Сводный отчет по заправкам.xlsx', index=False)
    return total_tank_exel


# def app():
#     SD = first_data_entry.get()
#     ED = second_data_entry.get()
#     get_devices()
#     get_stage(SD, ED)
#     get_api_data(get_stage(SD, ED))
#     get_id_and_serial()
#     get_total_value(get_stage(SD, ED))
#     get_id_card()
#     get_benz_file()
#     from_api_to_sql_tank(get_api_data(get_stage(SD, ED)))
#     from_api_to_sql_id_serial(get_id_and_serial())
#     from_api_to_sql_tank_total(get_total_value(get_stage(SD, ED)))
#     request_sql_from_api()
#     request_sql_from_api_total()


connect.commit()
