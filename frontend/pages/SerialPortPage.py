from PyQt5.QtWidgets import QToolBar, QComboBox, QPushButton, QLabel


from frontend.pages.BaseClassPage import BaseClassPage
from backend.serial_data import SerialData


class SerialPortPage(BaseClassPage):

    title = "Serial Port"

    def initUI(self, layout):
        pass


        self.serial_data = SerialData()

        self.serial_data.on_data.connect(self.on_new_data)

        self.port_settings_popup = v.PortSetupPopup(self.serial_data)

        consoleTab = v.ConsolePrintTab(self.serial_data, self.plot_data)

        # TOOL BAR
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        self.port_selector = QComboBox()
        
        self.scan_button = QPushButton('Scan')
        self.scan_button.clicked.connect(self.scan_ports)
        
        self.open_button = QPushButton('Open')
        self.open_button.clicked.connect(self.open_port)
        
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.close_port)
        
        self.settings_button = QPushButton('Settings')
        self.settings_button.clicked.connect(self.open_port_settings)

        self.variables_button = QPushButton('Variables')
        self.variables_button.clicked.connect(self.open_plot_settings)

        self.connection_status = QLabel('Not Connected')
        toolbar.addWidget(self.scan_button)
        toolbar.addWidget(self.port_selector)
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.close_button)
        toolbar.addSeparator()
        toolbar.addWidget(self.settings_button)
        toolbar.addWidget(self.variables_button)
        toolbar.addSeparator()
        toolbar.addWidget(self.connection_status)




    def scan_ports(self):
        self.port_selector.clear()
        ports = self.serial_data.port_list()
        self.port_selector.addItems(ports)

    def open_port(self):
        try:
            self.serial_data.port = self.port_selector.currentText()
            self.serial_data.open()
            self.connection_status.setText('Connected')
        except Exception as e:
            self.connection_status.setText('Failed to Connect')
            
            print(e)

    def close_port(self):
        self.serial_data.close()
        self.connection_status.setText('Not Connected')

    def open_port_settings(self):
        self.port_settings_popup.popup()





    def on_tab_focus(self):
        pass