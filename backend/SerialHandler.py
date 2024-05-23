from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from dataclasses import dataclass

@dataclass
class SerialSettings:
    baudrate: int = 250000
    timeout: int = 50 / 1000
    port: str = ""
    header: bytes = b""
    expected_size: int = 0


class SerialPortThread(QThread):
    portClosed = pyqtSignal()
    errorOcurred = pyqtSignal(str)
    dataReceived = pyqtSignal(bytes)
    emittingData = True
    buffer = bytearray()


    def __init__(self, port, baudrate, header=b"", expected_size=0):
        self.settings = SerialSettings(baudrate=baudrate, port=port, header=header, expected_size=expected_size)
        self.connect()
        super().__init__()
        
    @property
    def port(self):
        return self.settings.port

    def run(self):
        while True:
            if self.ser.bytesAvailable():
                data = self.ser.readAll()  # Read all available bytes
                self.buffer.extend(data)  # Add the data to the buffer

                # Process the buffer in packets
                if len(self.settings.header) > 0:
                    while self.settings.header in self.buffer:
                        try:
                            index = self.buffer.index(self.settings.header)

                            psize = self.settings.expected_size
                            if psize > 0:
                                if len(self.buffer) >= index + psize:
                                    packet = bytes(self.buffer[:index])
                                    self.buffer = self.buffer[index + psize:]  # Adjust for the length of the header
                            else:
                                packet = bytes(self.buffer[:index])
                                self.buffer = self.buffer[index + len(self.settings.header):]

                            if self.emittingData and packet:  # Ignore empty packets
                                self.dataReceived.emit(packet)
                        except ValueError as e:
                            print(e)
                            self.close()
                            return
                        except Exception as e:
                            print(e)
                            self.errorOcurred.emit(str(e))
                            self.close()
                            return
                else:
                    if self.emittingData:
                        self.dataReceived.emit(bytes(self.buffer))
                    self.buffer.clear()


    def connect(self):
        try:
            if self.ser is not None:          # Port exists
                if self.ser.isOpen():
                    self.ser.close()
                    self.wait(2)
                self.ser.setPortName(self.settings.port)
                self.ser.setBaudRate(self.settings.baudrate)
                self.ser.open(QSerialPort.OpenModeFlag.ReadWrite)

            else:
                self.ser = QSerialPort()
                self.ser.errorOccurred.connect(self.errorOcurred)
                self.ser.error.connect(self.errorOcurred)
                self.ser.setPortName(self.settings.port)
                self.ser.setBaudRate(self.settings.baudrate)
                self.ser.open(QSerialPort.OpenModeFlag.ReadWrite)
        except Exception as e:
            self.errorOcurred.emit(str(e))
            print(e)
            self.close()


    def pause(self):
        self.emittingData = False

    def resume(self):
        self.emittingData = True

    def send(self, data):
        self.ser.write(data)

    def set_header(self, header, size=None):
        self.expected_header = header
        self.expected_size = size

    def close(self):
        self.portClosed.emit()
        self.ser.close()
        self.terminate()



class SerialPortsHandler(QObject):
    def __init__(self):
        super().__init__()

        self.available_ports = {}
        self.port_threads = {}

        self.portStatusCheck = QTimer()
        self.portStatusCheck.timeout.connect(self.scan_interval)
        self.portStatusCheck.start(1000)



    def open_port(self, port, baudrate, header=b"", expected_size=0) -> SerialPortThread:
        thread = SerialPortThread(port, baudrate, header, expected_size)
        thread.start()
        self.port_threads[port] = thread
        return thread
    
    
    def close_port(self, name):
        for thread in self.port_threads:
            if thread.port == name:
                thread.close()
                self.port_threads.remove(thread)
                return True
        return False


    def port_list(self):
        for port in QSerialPortInfo.availablePorts():
            port_info = {}
            port_info['description'] = port.description()
            port_info['manufacturer'] = port.manufacturer()
            port_info['serial_number'] = port.serialNumber()
            # port_info
            port_info['product_id'] = port.productIdentifier() if port.hasProductIdentifier() else None
            port_info['vendor_id'] = port.vendorIdentifier() if port.hasVendorIdentifier() else None
            port_info['busy'] = port.isBusy()
            port_info['baudrates'] = [int(baudrate) for baudrate in port.standardBaudRates()]

            self.available_ports[port.portName()] = port_info
        return self.available_ports



    def scan_interval(self):
        self.port_list()
        for port in self.port_threads.keys():
            if port not in self.available_ports:
                self.port_threads[port].close()
                self.port_threads.pop(port)