import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QAction

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('File')
        editMenu = menubar.addMenu('Edit')
        viewMenu = menubar.addMenu('View')
        searchMenu = menubar.addMenu('Search')
        toolsMenu = menubar.addMenu('Tools')
        helpMenu = menubar.addMenu('Help')

        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)

        fileMenu.addAction(exitButton)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Custom Serial Plotter')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())