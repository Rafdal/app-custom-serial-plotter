from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot, QTimer
import serial
from serial.tools import list_ports

class SerialData(QObject):
    on_data = pyqtSignal(bytes)

    def __init__(self):
        super().__init__()
        self.ser = serial.Serial()
        self.buffer = bytearray()
        self.port_is_open = False
        self.read_thread = QThread()
        self.moveToThread(self.read_thread)
        self.read_thread.started.connect(self.read_data)
        self.read_thread.start()

    def setup(self, port, baudrate=250000, timeout_ms=50, header=b'\xFF\x00'):
        self.serial_settings = {
            'header': header,
            'port': port,
            'baudrate': baudrate,
            'timeout': timeout_ms / 1000  # pyserial expects seconds
        }
    
    def port_list(self):
        ports = list_ports.comports()
        return [port.device for port in ports]

    def open(self):
        # Stop thread to avoid errors
        if self.ser.is_open:
            self.close()
        
        self.ser.port = self.serial_settings['port']
        self.ser.baudrate = self.serial_settings['baudrate']
        self.ser.timeout = self.serial_settings['timeout']
        self.ser.open()
        self.port_is_open = True

    def close(self):
        self.port_is_open = False
        self.ser.close()

    @pyqtSlot()
    def read_data(self):
        while True:
            if self.port_is_open and self.ser.in_waiting:
                data = self.ser.read(self.ser.in_waiting)  # Read all available bytes
                self.buffer.extend(data)  # Add the data to the buffer

                # Process the buffer in packets
                while self.serial_settings['header'] in self.buffer:
                    index = self.buffer.index(self.serial_settings['header'])
                    packet = bytes(self.buffer[:index])  # Convert bytearray to bytes
                    self.buffer = self.buffer[index+len(self.serial_settings['header']):]  # Adjust for the length of the header
                    if packet:  # Ignore empty packets
                        self.on_data.emit(packet)