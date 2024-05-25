from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from ...utils.ParamList import ParameterList, NumParam, ChoiceParam, BoolParam, TextParam

import typing


from backend.serial.Structures import SerialBuffer, SerialSettings

class SerialPort(QObject):
    portClosed = pyqtSignal()
    errorOcurred = pyqtSignal(str)
    dataReceived = pyqtSignal(bytearray)
    emittingDataFlag = True
    buffer = SerialBuffer()
    bytesRead = 0

    # [ ] (2) SerialPort: Rewrite the __init__ method to use the SerialSettings class for configuration
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