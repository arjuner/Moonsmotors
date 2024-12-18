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
DEFAULT_SPEED = 5000
DEFAULT_ACCEL = 100
DEFAULT_DECEL = 100
REGISTER_NAMES = {
    9: "Encoder Position (EP)",
    11: "Encoder Position (EP)",
}

# Function to connect Modbus
def connect_modbus():
    if client.connect():
        print("Modbus Connection Successful")
        return True
    else:
        print("Modbus Connection Failed")
        return False

# Function to read registers
def read_registers(start_address, count):
    try:
        result = client.read_holding_registers(start_address, count)
        if result.isError():
            print(f"Error reading registers starting at {start_address}.")
        else:
            return result.registers
    except Exception as e:
        print(f"Exception occurred while reading registers: {e}")
        return None

# Function to enable driver
def enable_driver(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["enable"])
        print(f"Driver enabled for Axis {axis}.")
    except Exception as e:
        print(f"Error enabling driver for Axis {axis}: {e}")

# Function to disable driver
def disable_driver(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["disable"])
        print(f"Driver disabled for Axis {axis}.")
    except Exception as e:
        print(f"Error disabling driver for Axis {axis}: {e}")

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
        print(f"Motor {axis} running at speed value {speed_value}.")
    except Exception as e:
        print(f"Error writing to speed register for Axis {axis}: {e}")

# Function to stop motor
def stop_motor(axis):
    try:
        client.write_registers(SPEED_REGISTERS[axis], [0, 0])
        print(f"Motor {axis} stopped.")
    except Exception as e:
        print(f"Error stopping motor for Axis {axis}: {e}")

# Function to write acceleration
def write_accel(accel_value, axis):
    accel_register = ACCEL_REGISTERS[axis]
    try:
        if 1 <= accel_value <= 30000:
            high_word = (accel_value >> 16) & 0xFFFF
            low_word = accel_value & 0xFFFF
            client.write_registers(accel_register, [high_word, low_word])
            print(f"Written accel value {accel_value} to Axis {axis}.")
        else:
            print(f"Acceleration value {accel_value} is out of the allowed range (1-30000).")
    except Exception as e:
        print(f"Error writing to accel register for Axis {axis}: {e}")

# Function to write deceleration
def write_decel(decel_value, axis):
    decel_register = DECEL_REGISTERS[axis]
    try:
        if 1 <= decel_value <= 30000:
            high_word = (decel_value >> 16) & 0xFFFF
            low_word = decel_value & 0xFFFF
            client.write_registers(decel_register, [high_word, low_word])
            print(f"Written decel value {decel_value} to Axis {axis}.")
        else:
            print(f"Deceleration value {decel_value} is out of the allowed range (1-30000).")
    except Exception as e:
        print(f"Error writing to decel register for Axis {axis}: {e}")


def combine_registers(high, low):
    return (high << 16) | low


def read_registers_as_long(client, start_address, count):
    try:
        # Read the specified number of registers starting at `start_address`
        result = client.read_holding_registers(start_address, count)

        if result.isError():
            print(f"Error in Modbus response: {result}")
            return

        if hasattr(result, 'registers'):
            print(f"Reading registers {start_address} to {start_address + count - 1}:")
            registers = result.registers
            for i in range(0, len(registers), 2):
                if i + 1 >= len(registers):  # Ensure we have a pair
                    print(f"  Register {start_address + i}: Invalid pair")
                    continue
                high = registers[i]
                low = registers[i + 1]
                register_number = start_address + i
                register_name = REGISTER_NAMES.get(register_number, f"Register {register_number}")

                combined_value = combine_registers(high, low)
                #print(f"  {register_name}: {combined_value} ({40000 + register_number})")
                return combined_value
        else:
            print(f"Unexpected response format: {result}")
    except Exception as e:
        print(f"Exception occurred while reading registers: {e}")

# Function to move motor
def move_motor(direction, duration=0.1, accel_value=DEFAULT_ACCEL, decel_value=DEFAULT_DECEL):
    if direction in ["right", "left", "front", "back"]:
        start_jogging(1)
        start_jogging(2)
        write_accel(accel_value, 1)
        write_accel(accel_value, 2)
        write_decel(decel_value, 1)
        write_decel(decel_value, 2)

        if direction == "right":
            write_speed(DEFAULT_SPEED, 1)
            write_speed(DEFAULT_SPEED, 2)
        elif direction == "left":
            write_speed(-DEFAULT_SPEED, 1)
            write_speed(-DEFAULT_SPEED, 2)
        elif direction == "front":
            write_speed(DEFAULT_SPEED, 1)
            write_speed(-DEFAULT_SPEED, 2)
        elif direction == "back":
            write_speed(-DEFAULT_SPEED, 1)
            write_speed(DEFAULT_SPEED, 2)

        time.sleep(duration)
        stop_jogging(1)
        stop_jogging(2)
        stop_motor(1)
        stop_motor(2)
    else:
        print("Invalid direction!")

# Main execution
if connect_modbus():
    enable_driver(1)
    enable_driver(2)

    try:
        # Read registers 40011, 40012 (2 consecutive registers) and 40019
        ref = read_registers_as_long(client, start_address=11, count=2)
        directions = ["front", "back", "right", "left"]
        for direction in directions:
            print(f"Moving {direction}...")
            new_ref = read_registers_as_long(client, start_address=11, count=2)
            print(f"diff {(new_ref-ref)}...")
            ref = new_ref
            move_motor(direction)
            print(f"Stopped moving {direction}.")

    finally:
        stop_jogging(1)
        stop_jogging(2)
        disable_driver(1)
        disable_driver(2)
        client.close()
        print("Motors stopped and connection closed.")
