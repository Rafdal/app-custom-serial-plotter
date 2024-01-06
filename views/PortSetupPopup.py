from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QComboBox, QLineEdit, QSpinBox
from PyQt5.QtWidgets import QVBoxLayout

class PortSetupPopup(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Port Setup")

        self.scan_button = QPushButton("Scan Ports", self)
        self.scan_button.clicked.connect(self.scan_ports)

        self.port_dropdown = QComboBox(self)

        self.sync_bytes_input = QLineEdit(self)

        self.packet_size_selector = QSpinBox(self)
        self.packet_size_selector.setMinimum(1)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Port:"))
        layout.addWidget(self.port_dropdown)
        layout.addWidget(QLabel("Sync Bytes Header:"))
        layout.addWidget(self.sync_bytes_input)
        layout.addWidget(QLabel("Packet Size (bytes):"))
        layout.addWidget(self.packet_size_selector)
        layout.addWidget(self.scan_button)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def scan_ports(self):
        # TODO: Implement port scanning logic
        pass

    def connect(self):
        # TODO: Implement connection logic
        pass
