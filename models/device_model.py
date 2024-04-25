class DeviceModel:
    def __init__(self, deviceType, deviceId, deviceName, comments, hiveCreationTime, hiveFirstheardTime,
                 hiveLastheardTime, firmwareVersion, hardwareVersion, lastTelemetryReportPacketId,
                 lastHeardByDeviceType, lastHeardByDeviceId, counter, dayofyear, lastHeardCounter,
                 lastHeardDayofyear, lastHeardByGroundstationId, status, twoWayEnabled,
                 dataEncryptionEnabled, metadata):
        self.deviceType = deviceType
        self.deviceId = deviceId
        self.deviceName = deviceName
        self.comments = comments
        self.hiveCreationTime = hiveCreationTime
        self.hiveFirstheardTime = hiveFirstheardTime
        self.hiveLastheardTime = hiveLastheardTime
        self.firmwareVersion = firmwareVersion
        self.hardwareVersion = hardwareVersion
        self.lastTelemetryReportPacketId = lastTelemetryReportPacketId
        self.lastHeardByDeviceType = lastHeardByDeviceType
        self.lastHeardByDeviceId = lastHeardByDeviceId
        self.counter = counter
        self.dayofyear = dayofyear
        self.lastHeardCounter = lastHeardCounter
        self.lastHeardDayofyear = lastHeardDayofyear
        self.lastHeardByGroundstationId = lastHeardByGroundstationId
        self.status = status
        self.twoWayEnabled = twoWayEnabled
        self.dataEncryptionEnabled = dataEncryptionEnabled
        self.metadata = metadata

    def get_device_name_without_prefix(self) -> str:
        '''Check if the device name starts with "F-0x" and remove it if it does'''
        deviceName = str(self.deviceName)

        if deviceName.startswith('F-0x'):
            return self.deviceName[4:]
        else:
            return self.deviceName

    def __str__(self):
        return (
            f'DeviceModel(\n'
            f'  deviceType: {self.deviceType},\n'
            f'  deviceId: {self.deviceId},\n'
            f'  deviceName: {self.deviceName},\n'
            f'  comments: {self.comments},\n'
            f'  hiveCreationTime: {self.hiveCreationTime},\n'
            f'  firmwareVersion: {self.firmwareVersion},\n'
            f'  lastTelemetryReportPacketId: {self.lastTelemetryReportPacketId},\n'
            f'  status: {self.status},\n'
            f'  twoWayEnabled: {self.twoWayEnabled},\n'
            f'  dataEncryptionEnabled: {self.dataEncryptionEnabled},\n'
            f')'
        )