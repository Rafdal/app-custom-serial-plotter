import serial.tools.list_ports

# Scan for available serial ports
ports = serial.tools.list_ports.comports()
print("Available serial ports:")
for port in ports:
    print(port.device)

# Select a port to open
port_name = input("Enter the name of the port to open: ")
baudrate = 115200
ser = serial.Serial(port_name, baudrate, timeout=0.01)

# Read and print incoming bytes
while True:
    if ser.in_waiting > 0:
        incoming_bytes = ser.read(ser.in_waiting)
        incoming_ascii = incoming_bytes.decode("ascii")
        incoming_hex = incoming_bytes.hex()
        print(f"ASCII: {incoming_ascii}")
        print(f"Hex: {incoming_hex}")