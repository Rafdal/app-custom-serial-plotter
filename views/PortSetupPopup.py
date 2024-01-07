from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QComboBox, QLineEdit, QSpinBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QSizePolicy, QFrame

from PyQt5.QtGui import QIntValidator

class PortSetupPopup(QDialog):
    def __init__(self, serial_data_model):
        super().__init__()

        self.serial_data_model = serial_data_model

        self.setWindowTitle("Port Setup")
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        # self.setMinimumSize(500, 300)

        self.sync_bytes_input = QLineEdit(self)

        self.baudrate_num_input = QLineEdit(self)
        self.baudrate_num_input.setText("")
        self.baudrate_num_input.setValidator(QIntValidator())

        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("Baudrate:"))
        baud_layout.addWidget(self.baudrate_num_input)

        sync_layout = QHBoxLayout()
        sync_layout.addWidget(QLabel("Sync Bytes Header:"))
        sync_layout.addWidget(self.sync_bytes_input)

        subimt_button = QPushButton("Submit")
        subimt_button.clicked.connect(self.subimit_settings)

        # add layouts
        layout = QVBoxLayout()
        layout.addLayout(baud_layout)
        layout.addLayout(sync_layout)
        layout.addSpacing(10)
        layout.addWidget(subimt_button)
        layout.addStretch()
        self.setLayout(layout)

    def popup(self):
        port_settings = self.serial_data_model.settings
        self.baudrate_num_input.setText(str(port_settings['baudrate']))
        self.sync_bytes_input.setText(port_settings['header'].hex().upper())
        self.show()

    def subimit_settings(self):
        try:
            self.serial_data_model.settings['baudrate'] = int(self.baudrate_num_input.text())
            self.serial_data_model.settings['header'] = bytes.fromhex(self.sync_bytes_input.text())
            self.close()
        except Exception as e:
            dialog = QDialog()
            dialog.setWindowTitle("Error")
            dialog.setMinimumSize(200, 100)
            dialog.setLayout(QVBoxLayout())
            dialog.layout().addWidget(QLabel(str(e)))
            dialog.exec_()
            print(e)
