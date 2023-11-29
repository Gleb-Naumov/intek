import os
import requests

from dotenv import load_dotenv

load_dotenv()


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


def main():
    get_devices()
    get_stage(20231101, 20231121)
    get_api_data(get_stage(20231101, 20231121))
    get_id_and_serial()
    get_total_value(get_stage(20231101, 20231121))
