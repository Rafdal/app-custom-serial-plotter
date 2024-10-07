from PyQt5.QtWidgets import QToolBar, QComboBox, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QStyle, QSizePolicy, QDialog
from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt


from frontend.pages.BaseClassPage import BaseClassPage
from frontend.widgets.BasicWidgets import DropDownMenu, Button
from frontend.widgets.CardWidgets import CardWidget, CardListWidget
from frontend.widgets.DynamicSettingsWidget import DynamicSettingsWidget

from backend.serial.Handler import SerialPortsHandler
from backend.serial.Structures import SerialSettings, PortInfo
from backend.serial.Port import SerialPort

import typing


# [ ] (4) OpenPortDialog: Implement the class

class OpenPortDialog(QDialog):
    """ Popup dialog for configuring and opening a serial port """
    def __init__(self, portInfo: PortInfo, openCallback: typing.Callable[[SerialSettings], bool], parent=None):
        super(OpenPortDialog, self).__init__(parent)
        self.setWindowTitle("Port Settings Dialog")
        self.setModal(True)
        self.setMinimumHeight(400)
        self.portInfo = portInfo
        self.openCallback = openCallback
        self.initUI()    

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.settings = SerialSettings(self.portInfo)

        self.dynamicSettingsWidget = DynamicSettingsWidget(self.settings, title=self.portInfo.name + " Port Settings")
        layout.addWidget(self.dynamicSettingsWidget)

        openButton = QPushButton("Open")
        openButton.clicked.connect(self.open_port)
        layout.addWidget(openButton)

    def open_port(self):
        # if self.settings.validate():
        if True:    # TODO: Implement the validation
            self.openCallback(self.settings)
            self.close()


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

        settingsButton = Button('Settings')
        settingsButton.clicked.connect(self.open_port_settings_dialog)

        hTopLayout = QHBoxLayout()

        hTopLayout.addWidget(scanButton)
        hTopLayout.addSpacing(20)
        hTopLayout.addWidget(self.portMenu)
        hTopLayout.addSpacing(20)
        hTopLayout.addWidget(openButton)
        hTopLayout.addWidget(settingsButton)
        hTopLayout.addStretch(1)
        layout.addLayout(hTopLayout)


    def on_ports_scanned(self, portListInfo: typing.Dict[str, PortInfo]):
        portsMenuDict = {}
        for item in portListInfo.items():
            k, v = item
            k = (k + f"  ({v.manufacturer})") if len(v.manufacturer) > 0 else k
            k = (k + f"  {v.description}") if len(v.description) > 0 else k
            portsMenuDict[k] = v

        self.portMenu.set_options(portsMenuDict)
        self.cardList.clear()
        for port in self.model.serial.active_ports():
            title = ""
            title += self.model.serial.description(port)
            if len(title) == 0:
                title = port

            child = QLabel(f"B/s: {portListInfo[port].bytesPerSecond}\n")

            btnSizePolicy = (QSizePolicy.Expanding, QSizePolicy.Expanding)
            closeBtn = Button('Close', background_color='red', color='white', hover_color='lightcoral',     
                              text_size=20, sizePolicy=btnSizePolicy)
            closeBtn.clicked.connect(lambda: self.model.serial.close_port(port))

            iconPath = "frontend/assets/usb_icon.png"
            card = CardWidget(title=title, subtitle=f"port: {port}", icon=iconPath, iconSize=64,
                              child=child, tail=closeBtn)
            self.cardList.addCard(card)


    def open_port(self, serialSettings: SerialSettings):
        if self.portMenu.selected is None:
            return
        
        port_info = self.portMenu.selected
        port_settings = self.model.serial.info2settings(port_info)

        port = self.model.serial.open_port(port_settings)
        if port is not None:
            pass

    def open_port_settings_dialog(self):
        if self.portMenu.selected is None:
            return
        port_name = self.portMenu.selected.name
        portInfo = self.model.serial.port_info(port_name)
        if portInfo is None:
            # TODO Implement the error handling or popup
            return
        dialog = OpenPortDialog(portInfo, openCallback=self.model.serial.open_port)
        dialog.exec_()

    def on_port_selected(self, name: str, info: PortInfo):

        # [ ] (5) Implement the OpenPortDialog with a SerialSettings object as parameter
        pass


    def on_tab_focus(self):
        print("on_tab_focus")
        self.model.serial.scan_ports()
        port_list = self.model.serial.port_list()
        self.on_ports_scanned(port_list)