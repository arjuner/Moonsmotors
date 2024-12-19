from pymodbus.client import ModbusSerialClient
import time

# Initialize Modbus Serial Client
client = ModbusSerialClient(port='COM4', baudrate=9600, timeout=5, parity='N', stopbits=1, bytesize=8)

# Constants
JOGGING_OPCODES = {"enable": 0x009F, "disable": 0x009E, "start": 0x0096, "stop": 0x00D8}
AXIS_COMMAND_REGISTERS = {1: 124, 2: 1124}
SPEED_REGISTERS = {1: 342, 2: 1342}
ACCEL_REGISTERS = {1: 338, 2: 1338}
DECEL_REGISTERS = {1: 340, 2: 1340}
DEFAULT_SPEED = 10000
DEFAULT_ACCEL = 100
DEFAULT_DECEL = 100

# Function to connect Modbus
def connect_modbus():
    if client.connect():
        print("Modbus Connection Successful")
        return True
    else:
        print("Modbus Connection Failed")
        return False

# Function to read registers as long
def combine_registers(high, low):
    return (high << 16) | low

def read_registers_as_long(client, start_address, count):
    try:
        result = client.read_holding_registers(start_address, count)
        if hasattr(result, 'registers') and len(result.registers) >= 2:
            high, low = result.registers[:2]
            return combine_registers(high, low)
    except Exception as e:
        print(f"Exception occurred while reading registers: {e}")
    return None

# Function to start jogging
def start_jogging(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["start"])
    except Exception as e:
        print(f"Error starting jogging for Axis {axis}: {e}")

# Function to stop jogging
def stop_jogging(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["stop"])
    except Exception as e:
        print(f"Error stopping jogging for Axis {axis}: {e}")

# Function to write speed
def write_speed(speed_value, axis):
    speed_register = SPEED_REGISTERS[axis]
    try:
        high_word = (speed_value >> 16) & 0xFFFF
        low_word = speed_value & 0xFFFF
        client.write_registers(speed_register, [high_word, low_word])
    except Exception as e:
        print(f"Error writing to speed register for Axis {axis}: {e}")

# Main execution
if connect_modbus():
    try:
        # Enable driver for Axis 1
        client.write_register(AXIS_COMMAND_REGISTERS[1], JOGGING_OPCODES["enable"])
        start_jogging(1)
        write_speed(DEFAULT_SPEED, 1)

        ref = read_registers_as_long(client, start_address=10, count=2)
        print("Starting motor movement in one direction with encoder monitoring...")

        while True:
            # Read encoder value
            new_ref = read_registers_as_long(client, start_address=10, count=2)
            if new_ref is not None:
                diff = new_ref - ref
                print(f"Encoder Value: {new_ref}, Difference: {diff}")
                ref = new_ref
            else:
                print("Failed to read encoder value.")

            time.sleep(1)  # Pause for 1 second
    except KeyboardInterrupt:
        print("Stopping motor movement and encoder monitoring...")
    finally:
        stop_jogging(1)
        client.write_register(AXIS_COMMAND_REGISTERS[1], JOGGING_OPCODES["disable"])
        client.close()
        print("Motor stopped and connection closed.")
