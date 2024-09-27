from pymodbus.client import ModbusSerialClient
import time

# Configuration for Modbus Client (adjust according to your setup)
client = ModbusSerialClient(port='COM7', baudrate=9600, timeout=5, parity='N', stopbits=1, bytesize=8)


def connect_modbus():
    if client.connect():
        print("Modbus Connection Successful")
        return True
    else:
        print("Modbus Connection Failed")
        return False


# Function to write opcode values to register 40125
def write_opcodes(register, opcodes):
    try:
        for opcode in opcodes:
            client.write_register(register, opcode)
            print(f"Written opcode 0x{opcode:04X} to register {register}")
            time.sleep(0.5)  # Short delay to observe any physical change

        print("Opcode test completed.")
    except Exception as e:
        print(f"Error writing to register {register}: {e}")


# Example usage:
if connect_modbus():
    # Register 40125 needs to be adjusted for Modbus zero-based addressing (40125 - 40001 = 124)
    control_register = 124  # Zero-based address for 40125

    # List of opcodes to test (add or modify based on your documentation)
    opcodes = [
        0x00D8,  # Example opcode for forward motion
        0x00A3,  # Example opcode for reverse motion
        0x009E,  # Example opcode for stopping the motor
        # 0x0001,  # Example opcode
        # 0x009E,  # Another possible opcode
        # Add more opcodes as necessary based on your manual
    ]

    print(f"Testing opcodes on register {control_register}")
    write_opcodes(control_register, opcodes)

    # Close the connection
    client.close()
