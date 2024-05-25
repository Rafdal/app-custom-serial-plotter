from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from .ParamList import ParameterList, NumParam, ChoiceParam, BoolParam, TextParam

from dataclasses import dataclass
import typing

@dataclass
class SerialSettings:
    baudrate: int = 250000
    timeout: int = 50 / 1000
    port: str = ""
    header: bytes = b""
    footer: bytes = b""
    expected_size: int = 0


class SerialBuffer:
    def __init__(self, max_size=1024):
        self.max_size = max_size
        self.buffer = bytearray()

    def clear(self):
        self.buffer.clear()

    def push(self, data: bytes) -> None:
        """ Add data to the buffer """
        self.buffer.extend(data)
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]

    def pop_all(self) -> bytearray:
        """ Pop all data from the buffer """
        data = bytearray(self.buffer)
        self.buffer.clear()
        return data

    def pop_bytes(self, size: int) -> bytearray:
        """ Pop a specific amount of bytes from the buffer """
        if len(self.buffer) >= size:
            data = bytearray(self.buffer[:size])
            self.buffer = self.buffer[size:]
            return data
        else:
            raise ValueError("The buffer does not contain enough data to pop the specified size")
    
    def pop_from(self, header: bytes, size: int = 0) -> bytearray:
        """ Pop data from the buffer starting from a specific header 

        Args:
        - header: bytes
        - size: int (optional)
        """
        if header not in self.buffer:
            raise ValueError("The buffer does not contain the specified header")
        index = self.buffer.index(header)
        if size > 0:
            if len(self.buffer) >= index + size:
                output = bytearray(self.buffer[:index])
                self.buffer = self.buffer[index + size:]  # Adjust for the length of the header
                return output
            else:
                raise ValueError("The buffer does not contain enough data to pop the specified size")
        else:
            output = bytearray(self.buffer[:index])
            self.buffer = self.buffer[index + len(header):]
            return output
        
    def pop_from_to(self, header: bytes, footer: bytes) -> bytearray:
        """ Pop data from the buffer starting from a specific header and ending at a specific footer 

        Args:
        - header: bytes
        - footer: bytes
        """
        if header not in self.buffer or footer not in self.buffer:
            raise ValueError("The buffer does not contain the specified header or footer")
        index0 = self.buffer.index(header)
        index1 = self.buffer.index(footer, index0 + len(header))
        if index0 < index1:
            output = bytearray(self.buffer[index0:index1])
            self.buffer = self.buffer[index1 + len(footer):]
            return output
        else:
            raise ValueError("The buffer does not contain the specified header or footer")
            
    def count(self, item: bytes) -> int:
        """ Count the number of occurrences of an item in the buffer """
        return self.buffer.count(item)

    def __contains__(self, item):
        return item in self.buffer

    def __len__(self):
        return len(self.buffer)



class SerialPort(QObject):
    portClosed = pyqtSignal()
    errorOcurred = pyqtSignal(str)
    dataReceived = pyqtSignal(bytearray)
    emittingDataFlag = True
    buffer = SerialBuffer()
    bytesRead = 0

    def __init__(self, port, baudrate, header=b"", footer=b"", expected_size=0, timeout=50 / 1000):
        super().__init__()
        self.ser = QSerialPort()
        self.ser.errorOccurred.connect(self._serial_error_handler)
        self.ser.readyRead.connect(self._handle_read)
        self.settings = SerialSettings(baudrate, timeout, port, header, footer, expected_size)


    def connect(self) -> bool:
        """ Connect to the serial port. Returns True if the connection was successful, otherwise False."""
        print("SerialPort::connect()")
        try:
            self.ser.setPortName(self.settings.port)
            self.ser.setBaudRate(self.settings.baudrate)

            if self.ser.open(QSerialPort.OpenModeFlag.ReadWrite):
                return True
            else:
                self.errorOcurred.emit(f"Error opening {self.settings.port}")
                print(f"Error opening {self.settings.port}")
                return False

            # self.ser.setDataTerminalReady(True)
        except Exception as e:
            self.errorOcurred.emit(str(e))
            print(e)
            return False
        

    def _serial_error_handler(self, error):
        match error:
            case QSerialPort.SerialPortError.NoError:
                return
            case QSerialPort.SerialPortError.DeviceNotFoundError:
                self.errorOcurred.emit(f"Device {self.settings.port} not found")
            case QSerialPort.SerialPortError.PermissionError:
                self.errorOcurred.emit(f"Permission error on {self.settings.port}")
            case QSerialPort.SerialPortError.OpenError:
                self.errorOcurred.emit(f"Error opening {self.settings.port}")
            case QSerialPort.SerialPortError.ParityError:
                self.errorOcurred.emit(f"Error on {self.settings.port} ParityError")
            case QSerialPort.SerialPortError.FramingError:
                self.errorOcurred.emit(f"Error on {self.settings.port} FramingError")
            case QSerialPort.SerialPortError.BreakConditionError:
                self.errorOcurred.emit(f"Error on {self.settings.port} BreakConditionError")
            case QSerialPort.SerialPortError.WriteError:
                self.errorOcurred.emit(f"Error on {self.settings.port} WriteError")
            case QSerialPort.SerialPortError.ReadError:
                self.errorOcurred.emit(f"Error on {self.settings.port} ReadError")
            case QSerialPort.SerialPortError.ResourceError:
                self.errorOcurred.emit(f"Error on {self.settings.port} ResourceError")
            case QSerialPort.SerialPortError.UnsupportedOperationError:
                self.errorOcurred.emit(f"Error on {self.settings.port} UnsupportedOperationError")
            case QSerialPort.SerialPortError.TimeoutError:
                self.errorOcurred.emit(f"Error on {self.settings.port} TimeoutError")
            case QSerialPort.SerialPortError.NotOpenError:
                self.errorOcurred.emit(f"Error on {self.settings.port} NotOpenError")
            case QSerialPort.SerialPortError.UnknownError:
                self.errorOcurred.emit(f"Error on {self.settings.port} UnknownError")
            case _:
                self.errorOcurred.emit(f"Undefined Error {str(error)} on {self.settings.port}")


    def pause(self):
        self.emittingDataFlag = False

    def resume(self):
        self.emittingDataFlag = True

    def send(self, data):
        self.ser.write(data)

    def close(self):
        self.portClosed.emit()
        del self.ser

    @property
    def port(self):
        return self.settings.port

    def _handle_read(self):
        if self.ser.bytesAvailable():
            try:
                newData = self.ser.readAll()
                output = None

                if len(newData) > 0:
                    self.bytesRead += len(newData)
                    self.buffer.push(newData)              # Add the data to the buffer

                # Process the buffer in packets (if a header is set)
                if len(self.settings.header) > 0 and len(self.settings.footer) == 0:
                    while self.buffer.count(self.settings.header) > 1:
                        psize = self.settings.expected_size
                        output = self.buffer.pop_from(self.settings.header, psize)
                # Process the buffer in packets (if a header and footer are set)
                elif len(self.settings.header) > 0 and len(self.settings.footer) > 0:
                    while self.settings.header in self.buffer and self.settings.footer in self.buffer:
                        output = self.buffer.pop_from_to(self.settings.header, self.settings.footer)
                # Process the buffer in raw data
                else:
                    if len(self.buffer) > 0:
                        output = self.buffer.pop_all()

                if output is not None and self.emittingDataFlag and len(output) > 0:  # Ignore empty packets
                    self.dataReceived.emit(output)


            except ValueError as e:
                self.errorOcurred.emit(str(e))
                print(e)
                return
            except Exception as e:
                self.errorOcurred.emit(str(e))
                print(e)
                return

class PortInfo:
    def __init__(self):
        print("PortInfo::__init__", id(self))

    name: str = ""
    description: str = ""
    manufacturer: str = ""
    baudrates: typing.List[int] = []
    busy: bool = False
    bytesPerSecond: int = 0

class SerialPortScannerThread(QThread):
    portScanned = pyqtSignal(dict)
    onScanInterval = pyqtSignal()

    available_ports: typing.Dict[str, PortInfo] = {}

    time_interval = 1

    def __init__(self):
        super().__init__()
        self.mutex = QMutex()

    def scan_ports(self) -> typing.Dict[str, PortInfo]:
        with QMutexLocker(self.mutex):
            self.__scan_ports()
        return self.available_ports

    def __scan_ports(self) -> typing.Dict[str, PortInfo]:
        scannedPorts = []
        for port in QSerialPortInfo.availablePorts():

            # If the port is already in the available_ports dict, update the busy status
            if port.portName() in self.available_ports:
                self.available_ports[port.portName()].busy = port.isBusy()
            
            # If the port is not in the available_ports dict, add it
            else:
                portInfo = PortInfo()
                portInfo.name = port.portName()
                portInfo.description = port.description()
                portInfo.manufacturer = port.manufacturer()
                portInfo.baudrates = port.standardBaudRates()
                portInfo.busy = port.isBusy()
                self.available_ports[port.portName()] = portInfo
            scannedPorts.append(port.portName())

        # Remove ports that are no longer available
        for port in list(self.available_ports.keys()):
            if port not in scannedPorts:
                self.available_ports.pop(port, None)

        return self.available_ports

    def run(self):
        while True:
            with QMutexLocker(self.mutex):
                available_ports = self.__scan_ports()
                self.portScanned.emit(available_ports)
                self.onScanInterval.emit()
                print()
            self.sleep(self.time_interval)  # sleep for time_interval seconds

class PortDynamicSettings(ParameterList):
    def __init__(self):

class SerialPortsHandler(QObject):

    portScanned = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.available_ports: typing.Dict[str, PortInfo] = {}
        self._active_ports: typing.Dict[str, SerialPort] = {}

        self.portScannerThread = SerialPortScannerThread()
        self.portScannerThread.portScanned.connect(self._handle_scanned_ports)
        self.portScannerThread.portScanned.connect(self.portScanned)
        self.portScannerThread.onScanInterval.connect(self.check_byte_rate)
        self.portScannerThread.start()


    def scan_ports(self):
        ports = self.portScannerThread.scan_ports()
        self._handle_scanned_ports(ports)

    def active_ports(self) -> typing.Dict[str, SerialPort]:
        """ Returns a dicts of active ports"""
        return dict(self._active_ports)

    def description(self, port) -> str:
        return self.available_ports[port].description
    
    def manufacturer(self, port) -> str:
        return self.available_ports[port].manufacturer
    
    def baudrates(self, port) -> typing.List[int]:
        return self.available_ports[port].baudrates
    
    def is_busy(self, port) -> bool:
        return self.available_ports[port].busy

    def port_list(self) -> typing.Dict[str, PortInfo]:
        """ Returns a dictionary of available ports with their information.
        
        Main dict:
        - key = port name (str)
        - value = dict of port information (PortInfo)
        """
        return dict(self.available_ports)

    def check_byte_rate(self):
        for port in list(self._active_ports.keys()):
            if port in self.available_ports:
                bytesRead = self._active_ports[port].bytesRead
                self.available_ports[port].bytesPerSecond = bytesRead / self.portScannerThread.time_interval
                self._active_ports[port].bytesRead = 0
            
    def _handle_scanned_ports(self, available_ports):
        self.available_ports = available_ports
        for port in list(self._active_ports.keys()):  # create a copy of keys for iteration
            if port not in self.available_ports:
                self._active_ports[port].close()
                self._active_ports.pop(port, None)


    def open_port(self, port, baudrate, header=b"", footer=b"", expected_size=0) -> SerialPort:
        print(f"Opening port {port}")
        if port in self._active_ports:
            serialPort = self._active_ports[port]
            serialPort.settings.baudrate = baudrate
            serialPort.settings.header = header
            serialPort.settings.footer = footer
            serialPort.settings.expected_size = expected_size            
            serialPort.connect()
            return serialPort
        
        serialPort = SerialPort(port=port, baudrate=baudrate)
        serialPort.settings.header = header
        serialPort.settings.footer = footer
        serialPort.settings.expected_size = expected_size
        if serialPort.connect():
            self._active_ports[port] = serialPort
            return serialPort
        else:
            return None

    def close_port(self, name):
        if name in self._active_ports and self._active_ports[name].ser.isOpen():
            self._active_ports[name].close()
            self._active_ports.pop(name, None)
            return True
        return False
        