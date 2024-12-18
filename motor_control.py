from pymodbus.client import ModbusSerialClient
import time

# Initialize Modbus Serial Client
client = ModbusSerialClient(port='COM3', baudrate=9600, timeout=5, parity='N', stopbits=1, bytesize=8)

# Constants
JOGGING_OPCODES = {"enable": 0x009F, "disable": 0x009E, "start": 0x0096, "stop": 0x00D8}
AXIS_COMMAND_REGISTERS = {1: 124, 2: 1124}
SPEED_REGISTERS = {1: 342, 2: 1342}
ACCEL_REGISTERS = {1: 338, 2: 1338}
DECEL_REGISTERS = {1: 340, 2: 1340}
DEFAULT_SPEED = 5000
DEFAULT_ACCEL = 100
DEFAULT_DECEL = 100


# Functions
def connect_modbus():
    if client.connect():
        print("Modbus Connection Successful")
        return True
    else:
        print("Modbus Connection Failed")
        return False


def enable_driver(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["enable"])
        print(f"Driver enabled for Axis {axis}.")
    except Exception as e:
        print(f"Error enabling driver for Axis {axis}: {e}")


def disable_driver(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["disable"])
        print(f"Driver disabled for Axis {axis}.")
    except Exception as e:
        print(f"Error disabling driver for Axis {axis}: {e}")


def start_jogging(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["start"])
    except Exception as e:
        print(f"Error starting jogging for Axis {axis}: {e}")


def stop_jogging(axis):
    try:
        client.write_register(AXIS_COMMAND_REGISTERS[axis], JOGGING_OPCODES["stop"])
    except Exception as e:
        print(f"Error stopping jogging for Axis {axis}: {e}")


def write_speed(speed_value, axis):
    speed_register = SPEED_REGISTERS[axis]
    try:
        high_word = (speed_value >> 16) & 0xFFFF
        low_word = speed_value & 0xFFFF
        client.write_registers(speed_register, [high_word, low_word])
        print(f"Motor {axis} running at speed value {speed_value}.")
    except Exception as e:
        print(f"Error writing to speed register for Axis {axis}: {e}")


def stop_motor(axis):
    try:
        client.write_registers(SPEED_REGISTERS[axis], [0, 0])
        print(f"Motor {axis} stopped.")
    except Exception as e:
        print(f"Error stopping motor for Axis {axis}: {e}")


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


def move_motor(direction, duration=5, accel_value=DEFAULT_ACCEL, decel_value=DEFAULT_DECEL):
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
        directions = ["front", "back", "right", "left"]
        for direction in directions:
            print(f"Moving {direction}...")
            move_motor(direction)
            print(f"Stopped moving {direction}.")

    finally:
        stop_jogging(1)
        stop_jogging(2)
        disable_driver(1)
        disable_driver(2)
        client.close()
        print("Motors stopped and connection closed.")
