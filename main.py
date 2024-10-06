# main.py
import sys
from PyQt5.QtWidgets import QApplication

print("Running main.py")

from backend.MainModel import MainModel
from frontend.MainWindow import *
from frontend.pages.SerialPortPage import SerialPortPage
from frontend.pages.MonitorPage import MonitorPage

import faulthandler

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

    # create a Data Model
    mainModel = MainModel()

    # create pages
    pages = [
        SerialPortPage(),
        MonitorPage(),
    ]

    print("Pages created, creating main window")
    ex = MainWindow(pages=pages, model=mainModel)

    faulthandler.enable()
    sys.exit(app.exec_())