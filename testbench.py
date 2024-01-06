from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QLabel
from models import SerialData

from PyQt5.QtCore import QTimer, QThread, pyqtSignal, pyqtSlot

class SerialApp(QWidget):
    def __init__(self):
        super().__init__()

        self.serial_data = SerialData()
        self.serial_data.on_data.connect(self.print_data)

        self.layout = QVBoxLayout()

        self.port_dropdown = QComboBox()
        self.layout.addWidget(self.port_dropdown)

        self.scan_button = QPushButton('Scan')
        self.scan_button.clicked.connect(self.scan_ports)
        self.layout.addWidget(self.scan_button)

        self.open_button = QPushButton('Open')
        self.open_button.clicked.connect(self.open_port)
        self.layout.addWidget(self.open_button)

        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close_port)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)


    def scan_ports(self):
        self.port_dropdown.clear()
        ports = self.serial_data.port_list()
        self.port_dropdown.addItems(ports)

    def open_port(self):
        port = self.port_dropdown.currentText()
        self.serial_data.setup(port)
        self.serial_data.open()

    def close_port(self):
        self.serial_data.close()

    def print_data(self, data):
        # Print raw bytes in HEX
        print(f'Raw: {data.hex()}')


if __name__ == '__main__':
    app = QApplication([])
    window = SerialApp()
    window.show()
    app.exec_()