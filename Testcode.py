from pymodbus.client import ModbusSerialClient
import time

# Configuration for Modbus Client
client = ModbusSerialClient(port='COM7', baudrate=9600, timeout=5, parity='N', stopbits=1, bytesize=8)


def connect_modbus():
    if client.connect():
        print("Modbus Connection Successful")
        return True
    else:
        print("Modbus Connection Failed")
        return False

def enable_driver():
    command_register = 124  # 40125 - 40001 = 124 (Zero-based address)
    driver_enable_opcode = 0x009F  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, driver_enable_opcode)
        print("Driver enabled.")
        time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error enabling jogging: {e}")

def disable_driver():
    command_register = 124  # 40125 - 40001 = 124 (Zero-based address)
    driver_disable_opcode = 0x009E  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, driver_disable_opcode)
        print("Driver disabled.")
        time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error disabling jogging: {e}")

# Function to enable jogging
def start_jogging():
    command_register = 124  # 40125 - 40001 = 124 (Zero-based address)
    start_jogging_opcode = 0x0096  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, start_jogging_opcode)
        print("Jogging mode enabled.")
        time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error Starting jogging: {e}")


# Function to stop jogging
def stop_jogging():
    command_register = 124  # 40125 - 40001 = 124 (Zero-based address)
    stop_jogging_opcode = 0x00D8  # Stop Jogging (SJ) opcode
    try:
        client.write_register(command_register, stop_jogging_opcode)
        print("Jogging mode stopped.")
        time.sleep(0.5)  # Short delay to observe stopping
    except Exception as e:
        print(f"Error stopping jogging: {e}")

# Function to write speed values to register 40049 (Jog Speed Control)
def write_speed(speed_value):
    speed_register = 336  # Zero-based address for 40049
    try:
        client.write_register(speed_register, speed_value)
        print(f"Written speed value {speed_value} to register {speed_register}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error writing to speed register {speed_register}: {e}")

# Function to write acceleration values to register 40339
def write_accel(accel_value):
    accel_register = 338  # Zero-based address for 40339
    try:
        if 1 <= accel_value <= 30000:  # Ensure the value is within the valid range
            client.write_register(accel_register, accel_value)
            print(f"Written accel value {accel_value} to register 40339 (address {accel_register})")
            time.sleep(0.5)
        else:
            print(f"Acceleration value {accel_value} is out of the allowed range (1-30000)")
    except Exception as e:
        print(f"Error writing to accel register {accel_register}: {e}")


# Function to run motor with jogging enabled/disabled for each speed
def run_motor_variable_speed_with_jogging(speeds, delay_between_speeds=10):
    for speed in speeds:
        print(f"Enabling jogging for speed {speed}")
        start_jogging()
        write_speed(speed)
        time.sleep(delay_between_speeds)
        print(f"Stopping jogging for speed {speed}")
        stop_jogging()

def read_register(register_address):
    zero_based_address = register_address - 40001  # Convert to zero-based address
    try:
        result = client.read_holding_registers(zero_based_address, 1)
        if result.isError():
            print(f"Error reading register {register_address}")
        else:
            print(f"Value at register {register_address}: {result.registers[0]}")
            return result.registers[0]
    except Exception as e:
        print(f"Error reading register {register_address}: {e}")


# Example usage:
if connect_modbus():
    # enable_driver()
    # write_accel(1234)
    # variable_speeds = [1000]
    # run_motor_variable_speed_with_jogging(variable_speeds)
    # disable_driver()

    read_register(40338)

    # Close the connection
    client.close()
