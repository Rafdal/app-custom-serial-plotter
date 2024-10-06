from PyQt5.QtWidgets import QHBoxLayout

from frontend.pages.BaseClassPage import BaseClassPage
from frontend.widgets.BasicWidgets import DropDownMenu, Button, NumberInput
from frontend.widgets.ConsoleWidget import ConsoleWidget

class MonitorPage(BaseClassPage):

    title = "Monitor"

    def initUI(self, layout):
        self.initTopLayout(layout)
    
    def initTopLayout(self, layout):

        # add a dropdown menu to select the serial port
        self.portMenu = DropDownMenu("Select Port", firstSelected=True, onChoose=self.on_port_selected)
        self.model.serial.activePortsChanged.connect(self.on_active_ports_changed)

        # add a button to open the serial port settings dialog
        openButton = Button("Open Monitor", on_click=self.open_monitor)
        closeButton = Button("Close Monitor", on_click=self.close_monitor)

        maxLines = NumberInput("Max Lines", interval=(1, 10000), step=1, default=1000, on_change=self.on_max_lines_changed)

        # add a console widget to display the serial port data
        self.consoleWidget = ConsoleWidget()

        # add the widgets to the layout
        hTopLayout = QHBoxLayout()
        hTopLayout.addWidget(self.portMenu)
        hTopLayout.addSpacing(20)
        hTopLayout.addWidget(openButton)
        hTopLayout.addWidget(closeButton)
        hTopLayout.addSpacing(20)
        hTopLayout.addWidget(maxLines)
        hTopLayout.addStretch(1)

        layout.addLayout(hTopLayout)
        layout.addWidget(self.consoleWidget)

    def close_monitor(self):
        port = self.portMenu.selected_title
        if self.model.serial.is_port_active(port):
            self.model.serial.on_port_data_received(port, None) # remove the callback

    def open_monitor(self):
        port = self.portMenu.selected_title
        if self.model.serial.is_port_active(port):
            self.model.serial.on_port_data_received(port, self.on_data_received)

    def on_data_received(self, data: bytearray):
        self.consoleWidget.appendText(data.decode())

    def on_active_ports_changed(self, active_ports):
        self.portMenu.set_options(active_ports)

    def on_port_selected(self, port: str, _):
        pass

    def on_max_lines_changed(self, value):
        self.consoleWidget.consoleOutput.document().setMaximumBlockCount(value)

    def on_tab_focus(self):
        print("on_tab_focus")
        self.model.serial.scan_ports()
        self.portMenu.set_options(self.model.serial.active_ports())