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
        time.sleep(0.1)  # Short delay to observe jogging
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


def write_speed(speed_value, run_time=10):
    speed_register = 342  # Zero-based address for 40343

    try:
        # Convert the 32-bit speed value to two 16-bit registers (high and low)
        high_word = (speed_value >> 16) & 0xFFFF  # Extract high 16 bits
        low_word = speed_value & 0xFFFF  # Extract low 16 bits

        # Write the 32-bit value as two consecutive 16-bit registers
        client.write_registers(speed_register, [high_word, low_word])

        print(f"Motor running at speed value {speed_value}.")

        # Run the motor for the specified time
        time.sleep(run_time)

        # Stop the motor by setting speed to 0
        high_word = 0
        low_word = 0
        client.write_registers(speed_register, [high_word, low_word])

        print("Motor stopped after 10 seconds.")
    except Exception as e:
        print(f"Error writing to speed register {speed_register}: {e}")


def write_accel(accel_value):
    accel_register = 338  # Zero-based address for 40339

    try:
        if 1 <= accel_value <= 30000:
            high_word = (accel_value >> 16) & 0xFFFF
            low_word = accel_value & 0xFFFF
            client.write_registers(accel_register, [high_word, low_word])
            print(f"Written accel value {accel_value} to registers 40339 and 40340 ")
            time.sleep(0.5)
        else:
            print(f"Acceleration value {accel_value} is out of the allowed range (1-30000)")
    except Exception as e:
        print(f"Error writing to accel register {accel_register}: {e}")

def write_decel(decel_value):
    decel_register = 340  # Zero-based address for 40339

    try:
        if 1 <= decel_value <= 30000:
            high_word = (decel_value >> 16) & 0xFFFF
            low_word = decel_value & 0xFFFF
            client.write_registers(decel_register, [high_word, low_word])
            print(f"Written accel value {decel_value} to registers 40339 and 40340 ")
            time.sleep(0.5)
        else:
            print(f"Acceleration value {decel_value} is out of the allowed range (1-30000)")
    except Exception as e:
        print(f"Error writing to accel register {decel_register}: {e}")


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
    enable_driver()
    start_jogging()
    write_accel(100)
    write_speed(10000, run_time=10)
    write_decel(100)
    stop_jogging()
    disable_driver()

    # read_register(40336)
    # read_register(40337)
    # read_register(40294)

    # Close the connection
    client.close()
