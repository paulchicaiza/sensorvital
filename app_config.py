'''
App config parameters from config.ini file
'''

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

# Basic config

N_BYTES: int = int(config.get('Core', 'n_bytes'))
ROUND_DIGITS: int = eval(config.get('Core', 'round_digits'))
NAN_VALUES: list[int] = eval(config.get('Core', 'nan_values')) 

# Logs config

ENABLE_LOGS: bool = eval(config.get('Core', 'enable_logs'))
SHOW_LOGS_PRINT: bool = eval(config.get('Core', 'show_logs_print'))
LOG_DIR: str = config.get('Core', 'log_dir')

# Auth config

USERNAME = config.get('Auth', 'username')
PASSWORD = config.get('Auth', 'password')

'''
Custom logger with date file management
'''

import os
import logging
from datetime import datetime

if ENABLE_LOGS:
    os.makedirs(LOG_DIR, exist_ok=True)

class CustomLogger:
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG if ENABLE_LOGS else logging.NOTSET)
        
        if ENABLE_LOGS:
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(name)s): %(message)s')

            log_file = os.path.join(LOG_DIR, f'{datetime.now().strftime('%Y-%m-%d')}.log')

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)

        self.logger_name = logger_name

    def debug(self, message):
        if ENABLE_LOGS:
            self.logger.debug(message)
        if SHOW_LOGS_PRINT:
            print(f'📘 [DEBUG]', f'({self.logger_name})', message)

    def info(self, message):
        if ENABLE_LOGS:
            self.logger.info(message)
        if SHOW_LOGS_PRINT:
            print(f'📗 [INFO]', f'({self.logger_name})', message)

    def warning(self, message):
        if ENABLE_LOGS:
            self.logger.warning(message)
        if SHOW_LOGS_PRINT:
            print(f'📙 [WARNING]', f'({self.logger_name})', message)

    def error(self, message):
        if ENABLE_LOGS:
            self.logger.error(message)
        if SHOW_LOGS_PRINT:
            print(f'📕 [ERROR]', f'({self.logger_name})', message)

    def critical(self, message):
        if ENABLE_LOGS:
            self.logger.critical(message)
        if SHOW_LOGS_PRINT:
            print(f'😥 [CRITICAL]', f'({self.logger_name})', message)

'''
Devices configuration from files in ./devices directory
'''

device_logger = CustomLogger('device_config')

class DeviceConfig:
    def __init__(self):
        self.init_data_container()
        self.load_devices_config()

    def init_data_container(self):
        self.data: dict[str, list[tuple[float, float]]] = {}

    def add_data(self, device_id, item: list[tuple[float, float]]):
        self.data[device_id] = item
    
    def clear(self):
        self.data.clear()

    def load_devices_config(self, directory = 'devices'):
        device_logger.info('Loading devices config')
        self.clear()
        try:
            files = os.listdir(directory)

            for filename in files:
                file_path = os.path.join(directory, filename)
                device_id = filename.split('.')[0]

                if os.path.isfile(file_path):
                    with open(file_path, 'r') as file:
                        lines = file.readlines()
                        if len(lines) > 0:
                            first_line = int(lines[0])
                            first_line_split = str(round(first_line / 100.0, 2)).split('.')
                            if len(first_line_split) == 2:
                                n_vars = int(first_line_split[1])
                                
                                if len(lines) - 1 < n_vars:
                                    device_logger.warning(f'n_vars is {n_vars} and lines with values are {len(lines) - 1}')

                                values = lines[1:n_vars + 1]
                                item: list[tuple[float, float]] = []
                                for value in values:
                                    try:
                                        value_split = value.split(',')
                                        mult = float(value_split[0])
                                        offset = float(value_split[1])
                                        item.append((mult, offset))
                                    except Exception as e:
                                        device_logger.error(e)

                                self.add_data(device_id, item)
                        file.close()

        except FileNotFoundError:
            device_logger.error(f'The directory "{directory}" does not exist.')