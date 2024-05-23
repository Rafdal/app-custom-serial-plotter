from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from dataclasses import dataclass
import typing

@dataclass
class SerialSettings:
    baudrate: int = 250000
    timeout: int = 50 / 1000
    port: str = ""
    header: bytes = b""
    expected_size: int = 0

class SerialBuffer:
    def __init__(self, max_size=16 * 1024):
        self.max_size = max_size
        self.buffer = bytearray()

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
        index = self.buffer.index(self.settings.header)
        if size > 0:
            if len(self.buffer) >= index + size:
                output = bytearray(self.buffer[:index])
                self.buffer = self.buffer[index + size:]  # Adjust for the length of the header
                return output
            else:
                raise ValueError("The buffer does not contain enough data to pop the specified size")
        else:
            output = bytes(self.buffer[:index])
            self.buffer = self.buffer[index + len(self.settings.header):]
            return output
            
    def count(self, item: bytes) -> int:
        """ Count the number of occurrences of an item in the buffer """
        return self.buffer.count(item)

    def __contains__(self, item):
        return item in self.buffer



class SerialPortThread(QThread):
    portClosed = pyqtSignal()
    errorOcurred = pyqtSignal(str)
    dataReceived = pyqtSignal(bytes)
    emittingData = True
    buffer = SerialBuffer()

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
                data = self.ser.readAll().data()    # Read all available bytes

                self.buffer.push(data)              # Add the data to the buffer

                # Process the buffer in packets (if a header is set)
                if len(self.settings.header) > 0:
                    if self.settings.header in self.buffer:
                        while self.buffer.count(self.settings.header) > 1:

                            try:
                                psize = self.settings.expected_size
                                packet = self.buffer.pop_from(self.settings.header, psize)

                                if self.emittingData and packet:  # Ignore empty packets
                                    self.dataReceived.emit(packet)
                            except ValueError as e:
                                self.errorOcurred.emit(str(e))
                                print(e)
                                self.close()
                                return
                            except Exception as e:
                                self.errorOcurred.emit(str(e))
                                print(e)
                                self.close()
                                return
                else:
                    if self.emittingData:
                        self.dataReceived.emit(self.buffer.pop_all())
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





class SerialPortScannerThread(QThread):
    portScanned = pyqtSignal(dict)

    def run(self):
        while True:
            available_ports = self.scan_ports()
            self.portScanned.emit(available_ports)
            self.sleep(1)  # sleep for 1 second

    def scan_ports(self):
        available_ports = {}
        for port in QSerialPortInfo.availablePorts():
            port_info = {}
            port_info['description'] = port.description()
            port_info['manufacturer'] = port.manufacturer()
            port_info['serial_number'] = port.serialNumber()
            port_info['product_id'] = port.productIdentifier() if port.hasProductIdentifier() else None
            port_info['vendor_id'] = port.vendorIdentifier() if port.hasVendorIdentifier() else None
            port_info['busy'] = port.isBusy()
            port_info['baudrates'] = [int(baudrate) for baudrate in port.standardBaudRates()]

            available_ports[port.portName()] = port_info
        return available_ports


class SerialPortsHandler(QObject):

    portScanned = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.available_ports = {}
        self.port_threads = {}

        self.portScannerThread = SerialPortScannerThread()
        self.portScannerThread.portScanned.connect(self._handle_scanned_ports)
        self.portScannerThread.portScanned.connect(self.portScanned)
        self.portScannerThread.start()


    def scan_ports(self):
        ports = self.portScannerThread.scan_ports()
        self._handle_scanned_ports(ports)


    def port_list(self):
        """ Returns a dictionary of available ports with their information.
        
        Main dict:
        - key = port name
        - value = dict with port info
        
        Port info dict:
        - "description" = str
        - "manufacturer" = str
        - "serial_number" = str
        - "product_id" = int or None
        - "vendor_id" = int or None
        - "busy" = bool
        - "baudrates" = list of int
        """
        return self.available_ports

    def _handle_scanned_ports(self, available_ports):
        self.available_ports = available_ports
        for port in list(self.port_threads.keys()):  # create a copy of keys for iteration
            if port not in self.available_ports:
                self.port_threads[port].close()
                self.port_threads.pop()
                del self.port_threads[port]

    def open_port(self, port, baudrate, header=b"", expected_size=0) -> SerialPortThread:
        if port in self.port_threads:
            thread = self.port_threads[port]
            thread.connect()
            return thread
        
        thread = SerialPortThread(port, baudrate, header, expected_size)
        thread.start()
        self.port_threads[port] = thread
        return thread

    def close_port(self, name):
        if name in self.port_threads:
            self.port_threads[name].close()
            self.port_threads.pop(name)
            return True
        return False