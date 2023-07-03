

class SerialSettingsModel:
    def __init__(self, port, baudrate = 115200, timeout_ms = 10):
        self.port = port
        self.baudrate = baudrate
        self.timeout_ms = timeout_ms