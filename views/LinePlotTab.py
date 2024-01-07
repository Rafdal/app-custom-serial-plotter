from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import QTimer, QThread, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from matplotlib.lines import Line2D

from PyQt5.QtCore import Qt

class PlotWorker(QThread):
    data_ready = pyqtSignal(list)

    def __init__(self, plot_data):
        super().__init__()
        self.plot_data = plot_data

    def run(self):
        # Get the data buffer and the relative time
        data_buffer, relative_time = self.plot_data.get()

        # Prepare the data for the plot
        plot_data = [(relative_time[:len(data)], data) for data in data_buffer]

        self.data_ready.emit(plot_data)

from PyQt5.QtWidgets import QScrollArea

class LinePlotTab(QWidget):
    def __init__(self, plot_data):
        super().__init__()

        self.plot_data = plot_data

        # Create the layout
        layout = QVBoxLayout()

        # Create the Figure and FigureCanvas objects
        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow the FigureCanvas to expand
        self.canvas.setMinimumHeight(1400)  # Set the minimum height
        self.figure.subplots_adjust(left=0.1, right=0.98, bottom=0.02, top=0.97, hspace=0.3)  # Adjust the spacing between subplots
        self.figure.tight_layout()  # Make the plot fit the Figure area

        # Create a scroll area and a container widget for the canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow the child widget to resize
        self.canvas_container = QWidget()
        self.canvas_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.canvas_container_layout = QVBoxLayout()
        self.canvas_container.setLayout(self.canvas_container_layout)
        self.canvas_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.canvas_container_layout.addWidget(self.canvas)
        self.canvas_container_layout.setStretch(0, 1)  # Set the vertical stretch factor to 1
        self.canvas_container_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas_container_layout.setSpacing(0)
        self.scroll_area.setWidget(self.canvas_container)

        # Add the scroll area to the layout
        layout.addWidget(self.scroll_area)

        # Create the subplots and Line2D objects
        self.lines = []
        for i in range(len(self.plot_data.info)):
            ax = self.figure.add_subplot(len(self.plot_data.info), 1, i + 1)
            line = Line2D([], [])
            line.axes = ax  # Link the Line2D object to the axes
            self.lines.append(line)
            ax.add_line(line)
            ax.set_ylabel(self.plot_data.info[i]['label'])

        # Create a button to start/stop the plot update
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.toggle_plot_update)
        layout.addWidget(self.start_stop_button)

        # Set the layout
        self.setLayout(layout)

        # Create a timer to update the plot at a fixed interval
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.start_plot_worker)

        # Create the plot worker
        self.plot_worker = PlotWorker(self.plot_data)
        self.plot_worker.data_ready.connect(self.update_canvas)

        self.is_plotting = False

    def toggle_plot_update(self):
        if self.is_plotting:
            self.update_timer.stop()
            self.start_stop_button.setText("Start")
        else:
            self.update_timer.start(100)  # Update at 10 Hz
            self.start_stop_button.setText("Stop")
        self.is_plotting = not self.is_plotting

    def start_plot_worker(self):
        if not self.plot_worker.isRunning():
            self.plot_worker.start()

    def update_canvas(self, plot_data):
        for line, data in zip(self.lines, plot_data):
            line.set_data(*data)
            line.axes.relim()
            line.axes.autoscale_view()
        self.canvas.updateGeometry()
        self.canvas.draw_idle()