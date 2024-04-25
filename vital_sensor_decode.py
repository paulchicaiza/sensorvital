import base64

from datetime import datetime, timedelta, date, time

from models.message_encode_model import MessageEncodeModel, MessageDecodeValueModel

from models.device_model import DeviceModel

import swarm_provider

import app_config

import json

import csv

logger = app_config.CustomLogger('decode_util')

device_config = app_config.DeviceConfig()

def get_device_mult_offset_list(device_name: str) -> list[tuple[float, float]]:
    '''Retorna la lista con los valores mult y offset a partir del nombre del dispositivo'''
    try:
        return device_config.data[device_name]
    except Exception:
        return []


def find_device_by_id(device_list: list[DeviceModel], target_id) -> DeviceModel | None:
    '''Busca el dispositivo a partir de una lista de dispositivos por el device_id'''
    for device in device_list:
        if device.deviceId == target_id:
            return device
    return None

def get_mult_offset(values: list[tuple[float, float]], index: int) -> tuple[float, float]:
    '''Retorna una tupla con los valores (mult, offset) a partir de una lista de valores y el index.
    Retorna (1.0, 0.0) por defecto en caso que el index sea mayor a lista de valores'''
    if index < len(values):
            return values[index]
    return (1.0, 0.0)

def convert_pseudo_to_int(pseudo: str) -> int:
    '''Decodifica un str de n bytes y lo convierte a int'''
    string_array = [''] * len(pseudo)
    result = ''
    ii = 0

    if len(pseudo) > 0:
        ii = len(pseudo) - 1

    for c in pseudo:
        int_c = ord(c)
        if int_c == 63:
            int_c = 127  # '?' represents a value of 127 in decimal
        binary = bin(int_c)[2:].zfill(8)[2:]
        string_array[ii] = binary
        ii -= 1
        result += binary

    n = int(result, 2)
    if n > 131071:
        n = -n + 131072
    return n

def int_to_date(date_int: int) -> date:
    '''Retorna un objecto date a partir de la fecha con valor entero. 
    El entero debe seguir el formato juliano YYDDD, siendo YY el año y DDD el día juliano'''
    value_str = str(round(date_int / 1000.0, 3))
    value_split = value_str.split('.')
    if len(value_split) != 2:
        raise ValueError('int_to_date >> Value not follows the format make sure are using YYDDD')
    year = int(value_split[0]) + 2000
    julian_days = int(value_split[1])
    dt = datetime(year, 1, 1) + timedelta(days=julian_days - 1)
    return dt.date()

def int_to_datetime(date_int: int, time_int: int) -> datetime:
    '''Retorna un objeto datetime a partir de la fecha y tiempo con valor entero. 
    La fecha debe tener el formato juliano.
    El tiempo se basa en HHMMSS, en el caso de que sea negativo se suma 12 horas'''
    date_result = int_to_date(date_int)
    is_pm = False
    
    if (time_int < 0):
        is_pm = True

    time_int = abs(time_int)
    hour_split = str(round(time_int / 10000.0, 4)).split('.')

    if len(hour_split) != 2:
        raise ValueError('int_to_datetime >> Hour not follows the format')
    
    hour = int(hour_split[0])
    if is_pm:
        hour += 12

    minute_split = str(round(float(hour_split[1]) / 100.0, 2)).split('.')

    if (len(minute_split) != 2):
        raise ValueError('int_to_datetime >> Minute not follows the format')

    minute = int(minute_split[0])
    second = int(minute_split[1])

    desired_time = time(hour, minute, second)

    return datetime.combine(date_result, desired_time)

def int_to_minutes_n_vars(value: int) -> tuple[int, int]:
    '''Retorna una tupla con los valores (minutos, n variables) a partir de un entero'''
    value = abs(value)
    value_str = str(round(value / 100.0, 2))
    value_split = value_str.split('.')
    if len(value_split) != 2:
        raise ValueError('int_to_minutes_n_vars >> value not follows the format, make sure the frame has 000 format to get minutes and n vars')
    return (int(value_split[0]), int(value_split[1]))

def int_to_measure(value: int, mult: float, offset: float, round_digits: int = app_config.ROUND_DIGITS) -> float:
    '''Retorna el valor aplicando la formula: value * mult + offset. Aplica redondeo al resultado.'''
    return round((float(value) * mult) + offset, round_digits)

def data_to_date_minutes_n_vars(data: str, n_bytes = app_config.N_BYTES):
    '''Retorna los valores (fecha inicial, minutos, n variables) a partir de la trama. 
    La trama debe ser mayor a 3 * n_bytes caracteres.'''
    if len(data) < (3 * n_bytes):
        raise ValueError(f'data_to_date_minutes_n_vars >> Min data lenght is {3 * n_bytes}, current is {len(data)}')
    
    date_int = convert_pseudo_to_int(data[0:int(n_bytes)])
    time_int = convert_pseudo_to_int(data[int(n_bytes):int(n_bytes * 2)])
    vars_int = convert_pseudo_to_int(data[int(n_bytes * 2):int(n_bytes * 3)])
    datetime_value = int_to_datetime(date_int, time_int)
    (minutes, n_vars) = int_to_minutes_n_vars(vars_int)
    return datetime_value, minutes, n_vars

def decode_message_values(message: MessageEncodeModel, n_bytes = app_config.N_BYTES) -> list[MessageDecodeValueModel]:
    '''Decodifica los valores de la trama (data) del objecto MessageEncodeModel.
    La trama (data) debe ser mayor a 0.
    La cantidad de variables (n_vars) debe ser mayor 0.
    La fecha (initial_date) debe estar establecida.
    \nImportante: en el caso de que el valor pertenezca a los valores NaN, se establece como None.'''

    decode_values: list[MessageDecodeValueModel] = []

    data = message.data
    date = message.initial_date
    minutes = message.minutes
    n_vars = message.n_vars
    mult_offset_list = message.mult_offset

    if len(data) == 0:
        raise ValueError('decode_message_values >> Message data is empty')
    
    if n_vars <= 0:
        raise ValueError('decode_message_values >> Number of variables is 0')
    
    if (date is None):
        return ValueError('decode_message_values >> Initial date is None')

    new_datetime = date

    for i in range(int(3 * n_bytes), len(data), int(n_vars * n_bytes)):
        values: list[float] = []
        index: int = 0
        for j in range(i, i + (n_vars * n_bytes), n_bytes):
            end_index = j + n_bytes
            if end_index <= len(data):
                chunk = data[j:end_index]
                value_int = convert_pseudo_to_int(chunk)
                if value_int in app_config.NAN_VALUES: # check if value is in NAN_VALUES to set None
                    values.append(None)
                else:
                    (mult, offset) = get_mult_offset(mult_offset_list, index)
                    measure = int_to_measure(value_int, mult, offset)
                    values.append(measure)
            index += 1
        
        decode_values.append(MessageDecodeValueModel(new_datetime, values))
        new_datetime = new_datetime + timedelta(minutes=minutes)
    return decode_values

def decode_message(message: MessageEncodeModel, device_name: str | None, n_bytes=app_config.N_BYTES):
    '''Decodifica el objecto MessageEncodeModel.
    Valida que la fecha inicial (initial_date), la cantidad de variables (n_vars), minutos (minutes) y 
    los valores (mult_offset) se encuentren establecidos'''
    if message.initial_date is None or message.n_vars == 0:
        (initial_date, minutes, n_vars) = data_to_date_minutes_n_vars(message.data, n_bytes)

        message.initial_date = initial_date
        message.minutes = minutes
        message.n_vars = n_vars

    if (len(message.mult_offset) == 0):
        message.mult_offset = get_device_mult_offset_list(device_name)
    
    values = decode_message_values(message, n_bytes)
    message.message_values = values

def decode_messages(json_data, devices: list[DeviceModel], n_bytes = app_config.N_BYTES) -> list[MessageEncodeModel]:
    '''Retorna la respuesta JSON del servicio en una lista de objectos MessageEncodeModel con los valores decodificados'''
    result: list[MessageEncodeModel] = []
    if isinstance(json_data, list):
      for message in json_data: 
         if (isinstance(message, dict)):
            id = message['packetId']
            data = message['data']
            device_type = message['deviceType']
            device_id = message['deviceId']
            status = message['status']
            if (data is not None):
                device = find_device_by_id(devices, device_id)

                # decode base64 data
                decoded_bytes = base64.b64decode(data)
                decoded_string = decoded_bytes.decode('utf-8')

                device_name = None if device is None else device.get_device_name_without_prefix()

                message_model = MessageEncodeModel(id, decoded_string, device_type, device_id, device_name, status)
                decode_message(message_model, device_name, n_bytes)
                
                result.append(message_model)

    return result

def get_messages(start_date: datetime | None = None,
                 end_date: datetime | None = None,
                 device_id: str | None = None,) -> list[MessageEncodeModel]:
    '''Retorna los mensajes decodificados del servicio de swarm'''
    token = swarm_provider.login()
    if token:
        devices = swarm_provider.get_devices(token)
        messages = swarm_provider.get_messages(token, start_date=start_date, end_date=end_date, device_id=device_id)
        if messages is not None:
            return decode_messages(messages, devices)
        swarm_provider.logout(token)
    return []

def process_json_message(n_bytes = app_config.N_BYTES):
    result: list[MessageEncodeModel] = []
    #response_1713907924096.json
    # Opening JSON file
    f = open('response_1713907924096.json')
    
    # returns JSON object as 
    # a dictionary
    json_data = json.load(f)
    print(f'numero de mensajes= {len(json_data)}')

    for message in json_data:
        if (isinstance(message, dict)):
            id = message['packetId']
            data = message['data']
            device_type = message['deviceType']
            device_id = message['deviceId']
            status = message['status']
            hiveRxTime =message['hiveRxTime']
            decoded_bytes = base64.b64decode(data)
            decoded_string = decoded_bytes.decode('utf-8')
            device_name= "032e1"
            message_model = MessageEncodeModel(id, decoded_string, device_type, device_id, device_name, status, hiveRxTime)
            decode_message(message_model, device_name, n_bytes)
            result.append(message_model)
    return result



def print_decode_messages(messages: list[MessageEncodeModel]):
    '''Imprime los mensajes decodificados ordenados por la fecha inicial'''
    sorted_messages: list[MessageEncodeModel] = sorted(messages, key=lambda t: t.initial_date)
    n = len(sorted_messages)
    index = 0
    print('')
    for message in sorted_messages:
        print(f'device_id={message.device_id} | device_name={message.device_name} | fecha inicial={message.initial_date} | minutos={message.minutes} | n_vars={message.n_vars}')
        for message_value in message.message_values:
            print(message_value.date, message_value.values)
        print('')
        if (index < n - 1):
            print('*' * 100)
            print('')
        index += 1


def save_messages_csv(messages: list[MessageEncodeModel]):
    #sorted_messages: list[MessageEncodeModel] = sorted(messages, key=lambda t: t.initial_date)
    data = []
    data_time = []
    for message in messages:
        element = [message.initial_date, message.hiveRxTime, message.id]
        data_time.append(element)
        for message_value in message.message_values:
            element = [message_value.date]+message_value.values
            data.append(element)
            
    
    with open('messages_decode.csv','w', newline='') as file:
    # Create a CSV writer object
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Fecha", "Nivel de agua", "Temperatura de agua", "Conductividad Eléctrica", "Nivel de bateria"])
        csv_writer.writerows(data)


    with open('datatime_compare.csv','w', newline='') as file:
    # Create a CSV writer object
        csv_writer = csv.writer(file)
        csv_writer.writerow(["Fecha Inicial Dato", "Fecha registro mensaje", "idMessage"])
        csv_writer.writerows(data_time)




