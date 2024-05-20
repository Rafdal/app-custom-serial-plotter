from PyQt5.QtCore import QObject, pyqtSignal, QThread, pyqtSlot
import serial
from serial.tools import list_ports

class SerialReadThread(QThread):
    on_data = pyqtSignal(bytes)

    def __init__(self, serial_obj):
        super().__init__()
        self.ser = serial_obj
        self.buffer = bytearray()
        self.settings = {
            'header': b'\xFF\x00',
        }
        self.port_is_open = False

    def run(self):
        while True:
            try:
                if self.port_is_open and self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting)  # Read all available bytes
                    self.buffer.extend(data)  # Add the data to the buffer

                    # Process the buffer in packets
                    while self.settings['header'] in self.buffer:
                        index = self.buffer.index(self.settings['header'])
                        packet = bytes(self.buffer[:index])  # Convert bytearray to bytes
                        self.buffer = self.buffer[index+len(self.settings['header']):]  # Adjust for the length of the header

                        if packet:  # Ignore empty packets
                            self.on_data.emit(packet)
            except serial.SerialException as e:
                print(e)
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()
                self.port_is_open = False
                self.ser.close()
                self.ser = serial.Serial()




class SerialData(QObject):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial()
        self.port_is_open = False

        self.settings = {
            'baudrate': 250000,
            'timeout': 50 / 1000,  # pyserial expects seconds
        }

        self.port = ""

        self.read_thread = SerialReadThread(self.ser)
        self.read_thread.port_is_open = self.port_is_open
        self.read_thread.start()

    def port_list(self):
        ports = list_ports.comports()
        return [port.device for port in ports]

    def open(self):
        if not self.ser.is_open and self.port != "":
            self.ser.port = self.port
            self.ser.baudrate = self.settings['baudrate']
            self.ser.timeout = self.settings['timeout']
            self.ser.open()
            self.port_is_open = True
            self.read_thread.port_is_open = True

    def close(self):
        self.port_is_open = False
        self.read_thread.port_is_open = False
        self.ser.close()