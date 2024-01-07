import struct
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal

# Define a mapping from Python types to struct format codes
type_to_format = {
    float: 'f',
    int: 'i',
    bytes: 'B',
}

class PlotData(QObject):
    def __init__(self):
        super().__init__()
        self.buffer = None
        self.buffer_size = 0
        self.info = []
        self.data_structure = []
        self.expected_byte_count = 0

    def setup(self, data_structure=[], data_labels=[], buffer_size=0):
        self.buffer_size = buffer_size
        self.buffer = deque(maxlen=buffer_size)

        # Initialize the data structure
        self.info = []
        for type_, label in zip(data_structure, data_labels):
            self.info.append({'type': type_, 'label': label})

        # Pre-calculate the sizes and offsets
        self.data_structure = []
        offset = 0
        for type_ in data_structure:
            fmt = type_to_format[type_]
            size = struct.calcsize(fmt)
            self.data_structure.append((fmt, size, offset))
            offset += size
        self.expected_byte_count = offset

    def decode(self, data):
        # Check if the byte count is correct
        if len(data) != self.expected_byte_count:
            raise ValueError(f'Expected {self.expected_byte_count} bytes, got {len(data)} bytes')

        # Process the raw data according to the packet structure
        # and return the high-level variables
        packet = []
        for fmt, size, offset in self.data_structure:
            value, = struct.unpack_from(fmt, data, offset)
            packet.append(value)
        return packet

    def push(self, data):
        packet = self.decode_data(data)
        self.buffer.append(packet)

    def get(self):
        # Return the data as a list of lists
        return list(zip(*self.buffer))

# Create a PlotData object
plot_data = PlotData()

# Set up the PlotData object with a packet structure and a buffer size of 100
data_structure = [float, float, float]
data_labels = ['ax', 'ay', 'az']
plot_data.setup(data_structure, data_labels, 100)