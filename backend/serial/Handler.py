from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from ...utils.ParamList import ParameterList, NumParam, ChoiceParam, BoolParam, TextParam

from dataclasses import dataclass
import typing

from Structures import PortInfo, SerialSettings

from Port import SerialPort

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


    # [ ] (3) open_port: Use the SerialSettings class for configuration
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
        