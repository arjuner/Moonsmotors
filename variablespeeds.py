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


# Function to write speed values to register 40049 (Jog Speed Control)
def write_speed(speed_value):
    speed_register = 342  # Zero-based address for 40049
    try:
        client.write_register(speed_register, speed_value)
        print(f"Written speed value {speed_value} to register {speed_register}")
        time.sleep(0.5)  # Short delay to observe any physical change
    except Exception as e:
        print(f"Error writing to speed register {speed_register}: {e}")


# Function to enable jogging
def enable_jogging():
    command_register = 124  # 40125 - 40001 = 124 (Zero-based address)
    jogging_opcode = 0x0096  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, jogging_opcode)
        print("Jogging mode enabled.")
        time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error enabling jogging: {e}")


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


# Function to run motor with jogging enabled/disabled for each speed
def run_motor_variable_speed_with_jogging(speeds, delay_between_speeds=10):
    # For each speed, enable jogging, run at the speed, then stop jogging
    for speed in speeds:
        print(f"Enabling jogging for speed {speed}")
        enable_jogging()

        # Set the speed while jogging
        write_speed(speed)

        # Run for a specified delay at the given speed
        time.sleep(delay_between_speeds)

        # Stop jogging after each speed is set
        print(f"Stopping jogging for speed {speed}")
        stop_jogging()


# Example usage:
if connect_modbus():
    # Example speed values (adjust these based on your motor's specs)
    variable_speeds = [4000, 5000, 6000, 7000]  # Example speeds for jogging (in counts or RPM based on system scaling)

    # Run motor in jogging mode with enable/disable for each speed
    run_motor_variable_speed_with_jogging(variable_speeds)

    # Close the connection
    client.close()
