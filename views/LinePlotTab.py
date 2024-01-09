from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

class NonScrollablePlotWidget(PlotWidget):
    def wheelEvent(self, event):
        event.ignore()

class LinePlotTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create the QScrollArea object
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        # Create the container widget for the PlotWidgets
        self.container = QWidget()
        self.containerLayout = QVBoxLayout()
        self.container.setLayout(self.containerLayout)

        # Set the container widget as the widget for the scroll area
        self.scrollArea.setWidget(self.container)

        # Create the Pause/Continue button
        self.pause_button = QPushButton('Pause')
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.setStyleSheet("background-color: #E0E0E0")

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.pause_button)
        layout.addWidget(self.scrollArea)
        self.setLayout(layout)

        self.lines = []
        self.plotWidgets = []
        self.paused = False

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.setText('Continue' if self.paused else 'Pause')
        if self.paused:
            self.pause_button.setStyleSheet("background-color: #00FF00")
        else:
            self.pause_button.setStyleSheet("background-color: #E0E0E0")

    def create_subplots(self, plot_data):
        # Clear the container and the lists
        for plotWidget in self.plotWidgets:
            self.containerLayout.removeWidget(plotWidget)
            plotWidget.deleteLater()
        self.lines.clear()
        self.plotWidgets.clear()

        # Create a new PlotWidget for each variable
        for i, infoDict in enumerate(plot_data.info):
            label = infoDict['label']
            plotWidget = NonScrollablePlotWidget()
            plotWidget.setMinimumHeight(300)
            plotWidget.setMouseEnabled(x=False, y=False)
            plotWidget.showGrid(x=True, y=True)
            plotWidget.setTitle(label)
            line = plotWidget.plot([], [], pen=pg.mkPen(color=(i, plot_data.info_len * 1.3)))
            self.containerLayout.addWidget(plotWidget)
            self.plotWidgets.append(plotWidget)
            self.lines.append(line)

    def update_plot(self, buffer, time, plot_data):
        if self.paused:
            return
        
        # Check if the number of subplots has changed
        if len(self.lines) != plot_data.info_len:
            # Clear the figure and recreate the subplots
            self.create_subplots(plot_data)

        for line, ydata in zip(self.lines, buffer):
            line.setData(time, ydata)