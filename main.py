# main.py
import sys
from PyQt5.QtWidgets import QApplication

print("Running main.py")

from backend.MainModel import *
from frontend.MainWindow import *


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('frontend/assets/icon.png'))

    # create a Data Model
    mainModel = MainModel()

    # create pages
    pages = [
    ]

    print("Pages created, creating main window")
    ex = MainWindow(pages=pages, model=mainModel)

    sys.exit(app.exec_())