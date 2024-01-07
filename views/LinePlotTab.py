import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class LinePlotTab(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize the data
        self.data = []

        # Initialize the parameters
        self.symbols = []
        self.labels = []
        self.colors = []

        # Create the figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Create the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # Create a timer to update the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(100)  # Update every 100 milliseconds

    def setup_parameters(self, symbols, labels, colors):
        self.symbols = symbols
        self.labels = labels
        self.colors = colors

    def update_plot(self):
        # Clear the previous plot
        self.figure.clear()

        # Create a subplot
        ax = self.figure.add_subplot(111)

        # Plot the data
        for i, symbol in enumerate(self.symbols):
            ax.plot(self.data, symbol, label=self.labels[i], color=self.colors[i])

        # Add legend and labels
        ax.legend()
        ax.set_xlabel('Time')
        ax.set_ylabel('Value')

        # Redraw the canvas
        self.canvas.draw()