from PyQt5.QtWidgets import QToolBar, QComboBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout


from frontend.pages.BaseClassPage import BaseClassPage
from frontend.widgets.BasicWidgets import DropDownMenu, Button
from frontend.widgets.CardWidgets import CardWidget, CardListWidget

class SerialPortPage(BaseClassPage):

    title = "Serial Port"

    def initUI(self, layout):

        self.initTopLayout(layout)

        # self.cardList = CardListWidget()
        # layout.addWidget(self.cardList)

        self.active_ports = self.model.serial.active_ports()
        self.model.serial.portScanned.connect(self.on_port_scanned)


    def initTopLayout(self, layout):
        scanButton = Button('Scan')
        scanButton.clicked.connect(self.on_tab_focus)

        self.portMenu = DropDownMenu('Port', onChoose=self.on_port_selected)
        self.model.serial.portScanned.connect(self.portMenu.set_options)
        
        openButton = Button('Open')
        openButton.clicked.connect(self.open_port)
                
        hTopLayout = QHBoxLayout()

        hTopLayout.addWidget(scanButton)
        hTopLayout.addSpacing(20)
        hTopLayout.addWidget(self.portMenu)
        hTopLayout.addWidget(openButton)
        layout.addLayout(hTopLayout)


    def on_port_scanned(self, ports):
        self.portMenu.set_options(ports)
        if self.model.serial.active_ports() != self.active_ports:
            self.active_ports = self.model.serial.active_ports()
            # self.cardList.clear()
            for port in self.active_ports:
                card = CardWidget(title=port, subtitle="Serial Port")
                # self.cardList.addWidget(card)


    def open_port(self):
        selected_port_name = self.portMenu.selected_title  # dict
        print(f"{selected_port_name} selected\n\tDATA: {self.portMenu.selected}")
        thread = self.model.serial.open_port(selected_port_name, baudrate=115200)
        # thread.dataReceived.connect(lambda data: print(f"Data received: {data}\n"))

    def on_port_selected(self, name: str, info: dict):
        print(name, info)

    def on_tab_focus(self):
        print("on_tab_focus")
        self.model.serial.scan_ports()
        port_list = self.model.serial.port_list()
        self.portMenu.set_options(port_list)