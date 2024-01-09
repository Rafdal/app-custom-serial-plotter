import struct
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal

import numpy as np

# Define a mapping from Python types to struct format codes
type_to_format = {
    float: 'f',
    int: 'i',
    bytes: 'B',
}

class PlotData(QObject):
    def __init__(self):
        super().__init__()
        self.buffer = []
        self.time_buffer = None
        self.buffer_size = 0
        self.info = []
        self.info_len = 0
        self.data_structure = []
        self.expected_byte_count = 0

    def setup(self, data_structure=None, data_labels=None, buffer_size=100):
        if data_structure is None:
            data_structure = []
        if data_labels is None:
            data_labels = []

        self.buffer_size = buffer_size
        self.buffer = []
        for _ in range(len(data_structure)):
            d = deque([0]*buffer_size, maxlen=buffer_size)
            self.buffer.append(d)
        self.time_buffer = np.arange(-buffer_size + 1, 1)

        # Initialize the data structure
        self.info = []
        for type_, label in zip(data_structure, data_labels):
            self.info.append({'type': type_, 'label': label})
        self.info_len = len(self.info)

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
            return None

        # Process the raw data according to the packet structure
        # and return the high-level variables
        packet = []
        for fmt, size, offset in self.data_structure:
            value, = struct.unpack_from(fmt, data, offset)
            packet.append(value)
        return packet

    def push(self, data):
        packet = self.decode(data)
        if packet is None:
            return
        for i, value in enumerate(packet):
            self.buffer[i].append(value)

    def get(self):
        # Return the data as a list of lists
        if self.buffer[0] is None or len(self.buffer[0]) == 0:
            return None

        return self.buffer, self.time_buffer