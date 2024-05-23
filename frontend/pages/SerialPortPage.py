from PyQt5.QtWidgets import QToolBar, QComboBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout


from frontend.pages.BaseClassPage import BaseClassPage
from frontend.widgets.BasicWidgets import DropDownMenu, Button

class SerialPortPage(BaseClassPage):

    title = "Serial Port"

    def initUI(self, layout):
        pass

        self.portMenu = DropDownMenu('Port', onChoose=self.on_port_selected)

        self.model.serial.portScanned.connect(self.portMenu.set_options)

        scanButton = Button('Scan')
        scanButton.clicked.connect(self.on_tab_focus)
        
        openButton = Button('Open')
        openButton.clicked.connect(self.open_port)
        
        closeButton = Button('Close')
        closeButton.clicked.connect(self.close_port)
        
        # settingsButton = QPushButton('Settings')
        # settingsButton.clicked.connect(self.open_port_settings)

        # self.variables_button = QPushButton('Variables')
        # self.variables_button.clicked.connect(self.open_plot_settings)

        self.connectionStatus = QLabel('Not Connected')

        hlayout = QHBoxLayout()

        hlayout.addWidget(scanButton)
        hlayout.addSpacing(20)
        hlayout.addWidget(self.portMenu)
        hlayout.addWidget(openButton)
        hlayout.addWidget(closeButton)
        hlayout.addSpacing(20)
        # hlayout.addWidget(settingsButton)
        hlayout.addSpacing(20)
        hlayout.addWidget(self.connectionStatus)

        layout.addLayout(hlayout)


    def open_port(self):
        selected_port = self.portMenu.selected  # dict
        print(selected_port)

    def close_port(self):
        pass

    # def open_port_settings(self):
    #     self.port_settings_popup.popup()

    def on_port_selected(self, name: str, info: dict):
        print(name, info)

    def on_tab_focus(self):
        print("on_tab_focus")
        self.model.serial.scan_ports()
        port_list = self.model.serial.port_list()
        self.portMenu.set_options(port_list)