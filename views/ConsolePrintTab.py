from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QComboBox, QHBoxLayout, QLabel, QSpinBox
from PyQt5.QtCore import QTimer
from collections import deque

class ConsolePrintTab(QWidget):
    def __init__(self, serial_data):
        super().__init__()

        serial_data.on_data.connect(self.print_data)

        # Create the layout
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()

        # Create the text edit widget
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontFamily("Courier")
        layout.addLayout(hlayout)
        layout.addWidget(self.text_edit)

        # Create the clear button
        self.clear_button = QPushButton("Clear")
        hlayout.addWidget(self.clear_button)

        # Create the pause/continue button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setStyleSheet("background-color: #E0E0E0")
        hlayout.addWidget(self.pause_button)

        # Create a flag to indicate whether the GUI should be updated
        self.is_paused = False

        # Connect the pause button
        self.pause_button.clicked.connect(self.toggle_pause)

        # Create the dropdown menu
        self.format_dropdown = QComboBox()
        self.format_dropdown.addItem("ASCII")
        self.format_dropdown.addItem("HEX")
        self.format_dropdown.addItem("uint8_t")
        hlayout.addWidget(self.format_dropdown)

        # Create the spin box for max chars
        self.max_chars_label = QLabel("Max Chars:")
        hlayout.addWidget(self.max_chars_label)
        self.max_chars_spinbox = QSpinBox()
        self.max_chars_spinbox.setRange(1, 10000)  # Set the range
        self.max_chars_spinbox.setValue(1000)  # Set the default value
        hlayout.addWidget(self.max_chars_spinbox)

        # Create the deque for console output
        self.console_output = deque(maxlen=self.max_chars_spinbox.value())

        # Connect the clear button
        self.clear_button.clicked.connect(self.clear)

        # Connect the spin box value changed signal
        self.max_chars_spinbox.valueChanged.connect(self.update_max_chars)

        # Set the layout
        self.setLayout(layout)

        # Create a timer to update the GUI at a fixed interval
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_gui)
        self.update_timer.start(25)  # Update every 100 ms

    def clear(self):
        self.text_edit.clear()
        self.console_output.clear()

    def toggle_pause(self):
        # Toggle the pause flag
        self.is_paused = not self.is_paused

        # Update the text of the pause button
        if self.is_paused:
            self.pause_button.setText("Continue")
            self.pause_button.setStyleSheet("background-color: #00FF00")
        else:
            self.pause_button.setText("Pause")
            self.pause_button.setStyleSheet("background-color: #E0E0E0")

    def update_max_chars(self):
        # Create a new deque with the new maximum length
        new_console_output = deque(self.console_output, maxlen=self.max_chars_spinbox.value())
        self.console_output = new_console_output

    def print_data(self, data):
        # Print to the text edit
        if self.format_dropdown.currentText() == "ASCII":
            data_str = data.decode("ascii", "ignore")
        elif self.format_dropdown.currentText() == "HEX":
            data_str = data.hex()
        elif self.format_dropdown.currentText() == "uint8_t":
            data_str = ", ".join([str(x) for x in data])
        else:
            data_str = "Invalid Format"

        # Add the new data to the deque
        self.console_output.extend(data_str + '\n')

    def update_gui(self):
        # Only update the GUI if it is not paused
        if not self.is_paused:
            # Update the text edit with the contents of the deque
            self.text_edit.setPlainText(''.join(self.console_output))

            # Move the scrollbar to the end
            scrollbar = self.text_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())