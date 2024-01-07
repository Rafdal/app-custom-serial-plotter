import sys
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QAction, QTabWidget, QToolBar, QComboBox, QPushButton, QLabel

import models as m
import views as v
import controllers as c

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # set models
        self.serial_data = m.SerialData()
        self.plot_data = m.PlotData()

        # Settings Popup
        self.port_settings_popup = v.PortSetupPopup(self.serial_data)
        self.plot_settings_popup = v.PlotSettingsPopup(self.plot_data)

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

        # TABS
        consoleTab = v.ConsolePrintTab(self.serial_data, self.plot_data)

        # TAB MENU
        tab = QTabWidget()
        self.setCentralWidget(tab)
        tab.addTab(consoleTab, 'Console')

        self.setGeometry(200, 200, 1200, 800)
        self.setWindowTitle('Custom Serial Plotter')
        self.show()

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

    def open_plot_settings(self):
        self.plot_settings_popup.popup()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.serial_data.close()
        print('App Closed')
        return super().closeEvent(a0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())