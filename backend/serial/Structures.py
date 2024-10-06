import typing

from utils.ParamList import ParameterList, NumParam, ChoiceParam, BoolParam, TextParam, ConstParam



class PortInfo:
    name: str = ""
    description: str = ""
    manufacturer: str = ""
    baudrates: typing.List[str] = []
    busy: bool = False
    bytesPerSecond: int = 0


# [ ] (1) SerialSettings: Use ParameterList as base class and take a PortInfo object
class SerialSettings(ParameterList):

    def __init__(self, portInfo: PortInfo):
        defaultBaudrate = portInfo.baudrates[0]
        if "115200" in portInfo.baudrates:
            defaultBaudrate = "115200"
        super().__init__([
            ConstParam("port", portInfo.name, "Port"),
            TextParam("title", portInfo.name + ' ' + portInfo.description, "Device title"),
            ChoiceParam("baudrate", portInfo.baudrates, defaultBaudrate, "Baudrate"),
            NumParam("timeout", (0, 1), step=.001, value=.05, text="Timeout (s)"),
            TextParam("header", "", "Header"),
            TextParam("footer", "", "Footer"),
            NumParam("expected_size", (0, 1024), value=0, text="Expected Size")
        ])


class SerialBuffer:
    def __init__(self, max_size=1024):
        self.max_size = max_size
        self.buffer = bytearray()

    def clear(self):
        self.buffer.clear()

    def push(self, data: bytes) -> None:
        """ Add data to the buffer """
        self.buffer.extend(data)
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]

    def to_ascii(self) -> str:
        """ Convert the buffer to an ASCII string """
        return self.buffer.decode("ascii")

    def pop_all(self) -> bytearray:
        """ Pop all data from the buffer """
        data = bytearray(self.buffer)
        self.buffer.clear()
        return data

    def pop_bytes(self, size: int) -> bytearray:
        """ Pop a specific amount of bytes from the buffer """
        if len(self.buffer) >= size:
            data = bytearray(self.buffer[:size])
            self.buffer = self.buffer[size:]
            return data
        else:
            raise ValueError("The buffer does not contain enough data to pop the specified size")
    
    def pop_from(self, header: bytes, size: int = 0) -> bytearray:
        """ Pop data from the buffer starting from a specific header 

        Args:
        - header: bytes
        - size: int (optional)
        """
        if header not in self.buffer:
            raise ValueError("The buffer does not contain the specified header")
        index = self.buffer.index(header)
        if size > 0:
            if len(self.buffer) >= index + size:
                output = bytearray(self.buffer[:index])
                self.buffer = self.buffer[index + size:]  # Adjust for the length of the header
                return output
            else:
                raise ValueError("The buffer does not contain enough data to pop the specified size")
        else:
            output = bytearray(self.buffer[:index])
            self.buffer = self.buffer[index + len(header):]
            return output
        
    def pop_from_to(self, header: bytes, footer: bytes) -> bytearray:
        """ Pop data from the buffer starting from a specific header and ending at a specific footer 

        Args:
        - header: bytes
        - footer: bytes
        """
        if header not in self.buffer or footer not in self.buffer:
            raise ValueError("The buffer does not contain the specified header or footer")
        index0 = self.buffer.index(header)
        index1 = self.buffer.index(footer, index0 + len(header))
        if index0 < index1:
            output = bytearray(self.buffer[index0:index1])
            self.buffer = self.buffer[index1 + len(footer):]
            return output
        else:
            raise ValueError("The buffer does not contain the specified header or footer")
            
    def count(self, item: bytes) -> int:
        """ Count the number of occurrences of an item in the buffer """
        return self.buffer.count(item)

    def __contains__(self, item):
        return item in self.buffer

    def __len__(self):
        return len(self.buffer)