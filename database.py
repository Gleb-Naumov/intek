import sqlite3
import pandas as pd

from apiparser import *

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
time DATETIME,
car_name TEXT,
car_id TEXT,
litre INTEGER,
fuel_type TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS api (
tank_value INTEGER,
SD DATETIME,
ED DATETIME,
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


def get_id_card():
    """Функция получает данные из exel файла и записывает данные в sql таблицу car"""
    exel_file = 'ИдАвтографиКарточки (1).xlsx'
    df = pd.read_excel(exel_file)
    df.to_sql('car', connect, index=False, if_exists='replace')
    return df


def get_benz_file():
    """Функция получает данные из xml файла и записывает данные в sql таблицу benz"""
    benz_xml_file = 'бенза_автодоргрупп_с_1_21_октября_2023.xml'
    benz = pd.read_xml(benz_xml_file, xpath='.//filling')
    benz_df = pd.DataFrame(benz)
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
    SELECT benz.user_name, benz.litre, ROUND(api.tank_value, 2), api.ed, ROUND((((max(benz.litre, api.tank_value) - min(benz.litre, api.tank_value))) / min(benz.litre, api.tank_value)) * 100, 2) as dif
    FROM benz
    JOIN car ON benz.rfid_key = car.car_id_navigation
    JOIN ids ON car.car_id = ids.serial
    JOIN api ON ids.ids = api.ids
    ORDER BY api.ed
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


def start_app():
    get_id_card()
    get_benz_file()
    from_api_to_sql_tank(get_api_data(get_stage(20231101, 20231121)))
    from_api_to_sql_id_serial(get_id_and_serial())
    from_api_to_sql_tank_total(get_total_value(get_stage(20231101, 20231121)))
    request_sql_from_api()
    request_sql_from_api_total()


connect.commit()
connect.close()
