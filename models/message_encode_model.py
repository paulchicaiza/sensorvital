from datetime import datetime

class MessageDecodeValueModel:
    '''Set date and values of decode message. Values can be float or None.'''

    def __init__(self, date: datetime, values: list[float | None]):
        self.date = date
        self.values = values

class MessageEncodeModel:
    def __init__(self, id, data, device_type, device_id, device_name, status, hiveRxTime,
                 mult_offset: list[tuple[float, float]] = [],
                 minutes: int = 0, 
                 n_vars: int = 0,
                 initial_date: datetime | None = None,
                 message_values: list[MessageDecodeValueModel] = []):
        self._id = id
        self._device_type = device_type
        self._device_id = device_id
        self._device_name = device_name
        self._data = data
        self._status = status
        self._hiveRxTime = hiveRxTime

        self.mult_offset = mult_offset
        self.minutes = minutes
        self.n_vars = n_vars
        self.initial_date = initial_date
        self.message_values = message_values
    
    @property
    def id(self):
        '''Message id'''
        return self._id

    @property
    def device_type(self):
        return self._device_type

    @property
    def device_id(self):
        return self._device_id

    @property
    def device_name(self):
        return self._device_name

    @property
    def data(self):
        return self._data

    @property
    def status(self):
        return self._status
    
    @property
    def hiveRxTime(self):
        return self._hiveRxTime

    def __str__(self):
        return f"MessageEncodeModel(id={self.id}, deviceType={self.device_type}, deviceId={self.device_id}, data={self.data}, status={self.status}, device_name={self.device_name})"
