from PyQt5.QtWidgets import QToolBar, QComboBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QStyle, QSizePolicy
from PyQt5.QtCore import QSize


from frontend.pages.BaseClassPage import BaseClassPage
from frontend.widgets.BasicWidgets import DropDownMenu, Button
from frontend.widgets.CardWidgets import CardWidget, CardListWidget

class SerialPortPage(BaseClassPage):

    title = "Serial Ports"

    def initUI(self, layout):

        self.initTopLayout(layout)

        self.cardList = CardListWidget()
        layout.addWidget(self.cardList)


    def initTopLayout(self, layout):
        scanButton = Button('Scan')
        scanButton.clicked.connect(self.on_tab_focus)

        self.portMenu = DropDownMenu('Port', onChoose=self.on_port_selected)
        self.model.serial.portScanned.connect(self.on_ports_scanned)
        
        openButton = Button('Open')
        openButton.clicked.connect(self.open_port)
                
        hTopLayout = QHBoxLayout()

        hTopLayout.addWidget(scanButton)
        hTopLayout.addSpacing(20)
        hTopLayout.addWidget(self.portMenu)
        hTopLayout.addWidget(openButton)
        layout.addLayout(hTopLayout)


    def on_ports_scanned(self, portListInfo: dict):
        portsMenuDict = {}
        for item in portListInfo.items():
            k, v = item
            manufacturer = v.get('manufacturer', '')
            k = (k + f"  ({manufacturer})") if len(manufacturer) > 0 else k
            description = v.get('description', '')
            k = (k + f"  {description}") if len(description) > 0 else k
            portsMenuDict[k] = v

        self.portMenu.set_options(portsMenuDict)
        self.cardList.clear()
        for port in self.model.serial.active_ports():
            title = ""
            title += self.model.serial.description(port)
            if len(title) == 0:
                title = port

            child = QLabel(f"B/s: {portListInfo[port].get('B/s', 0)}\n")

            btnSizePolicy = (QSizePolicy.Expanding, QSizePolicy.Expanding)
            closeBtn = Button('Close', background_color='red', color='white', hover_color='lightcoral',     
                              text_size=20, sizePolicy=btnSizePolicy)
            closeBtn.clicked.connect(lambda: self.model.serial.close_port(port))

            iconPath = "frontend/assets/usb_icon.png"
            card = CardWidget(title=title, subtitle=f"port: {port}", icon=iconPath, iconSize=64,
                              child=child, tail=closeBtn)
            self.cardList.addCard(card)


    def open_port(self):
        selected_port_name = self.portMenu.selected["name"]  # dict
        port = self.model.serial.open_port(selected_port_name, baudrate=115200)
        if port is not None:
            port.settings.header = b'\xFF\x00'
            self.on_ports_scanned(self.model.serial.port_list())
            # port.settings.expected_size = 26
            # port.dataReceived.connect(lambda data: print(f"Data received: {data.hex(':')}\n"))

    def on_port_selected(self, name: str, info: dict):
        print(name, info)

    def on_tab_focus(self):
        print("on_tab_focus")
        self.model.serial.scan_ports()
        port_list = self.model.serial.port_list()
        self.on_ports_scanned(port_list)