from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QComboBox, QLineEdit, QSpinBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QSizePolicy, QFrame, QTextEdit

from PyQt5.QtGui import QIntValidator
import struct

# Define a mapping from string names to Python types
type_mapping = {
    "int32": int,
    "float": float,
    "uint8_t": bytes,  # Assuming uint8_t corresponds to bytes
}

key_to_format = {
    "int32": 'i',
    "float": 'f',
    "uint8_t": 'B',  # Assuming uint8_t corresponds to bytes
}

type_to_format = {
    float: 'f',
    int: 'i',
    bytes: 'B',
}

class PlotSettingsPopup(QDialog):
    def __init__(self, plot_data):
        super().__init__()

        self.plot_data = plot_data
        self.plot_data_info = []

        self.setWindowTitle("Plot Symbols Settings")
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.variable_name_input = QLineEdit(self)
        self.variable_name_input.setPlaceholderText("Variable Name")

        self.data_type_selector = QComboBox(self)
        self.data_type_selector.addItems(list(type_mapping.keys()))

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_variables)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_variable)

        self.pop_button = QPushButton("Remove Last")
        self.pop_button.clicked.connect(self.pop_last_variable)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_settings)

        self.buffer_size_selector = QSpinBox(self)
        self.buffer_size_selector.setRange(1, 3000)
        self.buffer_size_selector.setValue(10)

        self.info_display = QTextEdit(self)
        self.info_display.setReadOnly(True)
        self.info_display.setFontFamily("Courier")

        add_var_layout = QHBoxLayout()
        add_var_layout.addWidget(self.variable_name_input)
        add_var_layout.addWidget(self.data_type_selector)
        add_var_layout.addWidget(self.add_button)
        add_var_layout.addWidget(self.pop_button)

        clear_sub_layout = QHBoxLayout()
        clear_sub_layout.addWidget(QLabel("Buffer Size (data points):"))
        clear_sub_layout.addWidget(self.buffer_size_selector)
        clear_sub_layout.addWidget(self.clear_button)
        clear_sub_layout.addWidget(self.submit_button)

        layout = QVBoxLayout()
        layout.addLayout(add_var_layout)
        layout.addWidget(QLabel("Current Variables:"))
        layout.addWidget(self.info_display)
        layout.addLayout(clear_sub_layout)
        self.setLayout(layout)

    def clear_variables(self):
        self.plot_data_info = []
        self.update_info_display()

    def pop_last_variable(self):
        if len(self.plot_data_info) > 0:
            self.plot_data_info.pop()
        self.update_info_display()

    def add_variable(self):
        variable_name = self.variable_name_input.text()
        data_type = type_mapping[self.data_type_selector.currentText()]
        self.plot_data_info.append({'type': data_type, 'label': variable_name})
        self.variable_name_input.clear()
        self.update_info_display()

    def submit_settings(self):
        # Save changes to the data model
        data_structure = [info['type'] for info in self.plot_data_info]
        data_labels = [info['label'] for info in self.plot_data_info]
        self.plot_data.setup(data_structure, data_labels, self.buffer_size_selector.value())
        self.close()

    def update_info_display(self):
        total_size = 0
        lines = ["Name:\t(Type),\tSize\n"]
        for info in self.plot_data_info:
            fmt = info['type']
            fmt = type_to_format[fmt]
            size = struct.calcsize(fmt)
            total_size += size
            lines.append(f"{info['label']}:\t({info['type'].__name__}),\t{size} bytes")
        lines.append(f"\nTotal Size: {total_size} bytes")
        text = "\n".join(lines)
        self.info_display.setText(text)

    def popup(self):
        # Load the current settings from the data model
        self.plot_data_info = [{'type': info['type'], 'label': info['label']} for info in self.plot_data.info]
        self.buffer_size_selector.setValue(self.plot_data.buffer_size)
        self.update_info_display()

        # Display the dialog
        self.show()