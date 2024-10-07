from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from utils.ParamList import ParameterList, NumParam, ChoiceParam, BoolParam, TextParam

from dataclasses import dataclass
import typing

from .Structures import PortInfo, SerialSettings
# from Structures import PortInfo, SerialSettings

from .Port import SerialPort

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
                for baudrate in port.standardBaudRates():
                    portInfo.baudrates.append(str(baudrate))
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
            self.sleep(self.time_interval)  # sleep for time_interval seconds



class SerialPortsHandler(QObject):

    portScanned = pyqtSignal(dict)
    activePortsChanged = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.available_ports: typing.Dict[str, PortInfo] = {}
        self._active_ports: typing.Dict[str, SerialPort] = {}

        self.portScannerThread = SerialPortScannerThread()
        self.portScannerThread.portScanned.connect(self._handle_scanned_ports)
        self.portScannerThread.portScanned.connect(self.portScanned)
        self.portScannerThread.onScanInterval.connect(self.check_byte_rate)
        self.portScannerThread.start()

    def on_port_data_received(self, port: str, callback: typing.Callable[[bytearray], None]):
        """ 
        Connect or disconnect a callback function to the dataReceived signal of a port.
        - port: str
        - callback: callable function or None
            - If None, disconnect the signal
            - If a function, connect the signal to a callback function that receives a bytearray
        """
        if port in self._active_ports:
            try:
                if callback is None:
                    self._active_ports[port].dataReceived.disconnect()
                else:
                    self._active_ports[port].dataReceived.connect(callback)
            except:
                pass

    def is_port_active(self, port: str) -> bool:
        return (port in self._active_ports)

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

    def port_info(self, port) -> PortInfo:
        if port not in self.available_ports:
            return None
        return self.available_ports[port]

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
            
    def _handle_scanned_ports(self, available_ports: typing.Dict[str, PortInfo]):
        self.available_ports = available_ports
        for port in list(self._active_ports.keys()):  # create a copy of keys for iteration
            if port not in self.available_ports:
                self._active_ports[port].close()
                self._active_ports.pop(port, None)
                self.activePortsChanged.emit(self._active_ports)


    # [ ] (3) open_port: Use the SerialSettings class for configuration
    def open_port(self, settings: SerialSettings) -> SerialPort:
        '''
        Open a serial port with the specified settings.
        - returns: SerialPort if connection successful, otherwise None
        '''
        port = settings['port']
        print(f"Opening port {port}")
        if port in self._active_ports:
            serialPort = self._active_ports[port]
            serialPort.settings  = settings         
            serialPort.connect()
            return serialPort
        
        serialPort = SerialPort(settings)
        if serialPort.connect():
            self._active_ports[port] = serialPort
            self.activePortsChanged.emit(self._active_ports)
            return serialPort
        else:
            return None

    def close_port(self, name):
        if name in self._active_ports and self._active_ports[name].ser.isOpen():
            self._active_ports[name].close()
            self._active_ports.pop(name, None)
            self.activePortsChanged.emit(self._active_ports)
            return True
        return False

    def info2settings(self, port_info: PortInfo) -> SerialSettings:
        return SerialSettings(port_info)