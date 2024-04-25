import requests

from datetime import datetime, timezone

from models.device_model import DeviceModel

import app_config

API_HOST = 'https://bumblebee.hive.swarm.space'

LOGIN_URL = f'{API_HOST}/hive/login'

LOGOUT_URL = f'{API_HOST}/hive/logout'

DEVICES_URL = f'{API_HOST}/hive/api/v1/devices'

MESSAGES_URL = f'{API_HOST}/hive/api/v1/messages'

logger = app_config.CustomLogger('swarm_provider')

def _get_auth_headers(token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {token}'}

def _get_utc_ISO_8601_datetime_str(date: datetime | None) -> str | None:
    if date is None:
        return None
    utc_time = date.astimezone(timezone.utc)
    return utc_time.isoformat()

def login(username=app_config.USERNAME, password=app_config.PASSWORD):
    session = requests.Session()
    login_data = {
        'username': username,
        'password': password
    }
    try:
        response = session.post(LOGIN_URL, data=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data['token']
            if token is not None:
                logger.info('Login successful!')
                return token
            return None
        else:
            logger.warning("Login failed. Status code:", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred during login:", e)
        return None
    
def logout(token):
    headers = _get_auth_headers(token)
    try:
        response = requests.post(LOGOUT_URL, headers=headers)
        if response.status_code == 204:
            logger.info("Logout successful!")
            return True
        else:
            logger.warning("Logout failed. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred during logout:", e)
    return False

def make_authenticated_request(url, token, method='GET', data=None, params=None) -> requests.Response:
    '''Función genérica para realizar request a servicios swarm'''
    headers = _get_auth_headers(token)
    headers['accept'] = 'application/json'
    
    response = requests.Response()
    response.status_code = 500
    response.reason = 'Internal error'

    logger.debug(f'make_authenticated_request url={url}, method={method}, data={data}, params={params}')

    try:
        if (method == 'GET'):
            response = requests.get(url, headers=headers, params=params)
        if (method == 'POST'):
            response = requests.post(url, headers=headers, data=data, params=params)
        if (method == 'PUT'):
            response = requests.put(url, headers=headers, data=data, params=params)
        return response
    except requests.exceptions.RequestException as e:
        logger.error("Request error:", e)
        return response

def get_devices(token: str) -> list[DeviceModel]:
    '''Retorna los dispositivos registrados'''
    response = make_authenticated_request(DEVICES_URL, token)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            return [DeviceModel(**item) for item in data]
        elif isinstance(data, dict):
            return [DeviceModel(**data)]
        else:
            return []
    else:
        response_message = response.json()['message']
        if (response_message is None):
            logger.error(f'get messages error status_code={response.status_code} response={response} json={response.json()}')
        raise ValueError(response_message if response_message is not None else f'request get messages error {response.reason}')

def get_messages(token: str, start_date: datetime | None = None, end_date: datetime | None = None, device_id: str | None = None,):
    '''Retorna los mensajes de los dispositivos. Retorna todos los registros dentro
    de un rango de 30 días, documentación por swarm https://bumblebee.hive.swarm.space/apiDocs'''
    params = {
        'startDate': _get_utc_ISO_8601_datetime_str(start_date),
        'endDate': _get_utc_ISO_8601_datetime_str(end_date),
        'deviceid': device_id,
    }
    response = make_authenticated_request(MESSAGES_URL, token, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response_message = response.json()['message']
        if (response_message is None):
            logger.error(f'get messages error status_code={response.status_code} response={response} json={response.json()}')
        raise ValueError(response_message if response_message is not None else f'request get messages error {response.reason}')

