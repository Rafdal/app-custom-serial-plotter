import struct
from collections import deque
from PyQt5.QtCore import QObject, pyqtSignal
import time

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
        self.buffer = None
        self.time_buffer = None
        self.buffer_size = 0
        self.info = []
        self.data_structure = []
        self.expected_byte_count = 0

    def setup(self, data_structure=[], data_labels=[], buffer_size=0):
        self.buffer_size = buffer_size
        self.buffer = deque(maxlen=buffer_size)
        self.time_buffer = np.arange(-buffer_size + 1, 1)

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
        packet = self.decode(data)
        self.buffer.append(packet)
        if len(self.buffer) > len(self.time_buffer):
            self.time_buffer = np.arange(-len(self.buffer) + 1, 1)

    def get(self):
        # Return the data as a list of lists
        if self.buffer is None or len(self.buffer) == 0:
            return [[] for _ in range(len(self.info))], []
        
        # Make the time relative to the current time
        current_time = self.time_buffer[-1]
        relative_time = [t - current_time for t in self.time_buffer]

        return list(zip(*self.buffer)), relative_time