from pymodbus.client import ModbusSerialClient
import time
import threading  # Import threading module for parallel execution

# Initialize Modbus Serial Client
client = ModbusSerialClient(port='COM7', baudrate=9600, timeout=5, parity='N', stopbits=1, bytesize=8)
axis_1 = 1
axis_2 = 2
def connect_modbus():
    if client.connect():
        print("Modbus Connection Successful")
        return True
    else:
        print("Modbus Connection Failed")
        return False

def enable_driver(axis):
    # Register for Axis 1 is 124, for Axis 2 it would be 124 + 1000 = 1124
    command_register = 124 if axis == 1 else 1124
    driver_enable_opcode = 0x009F  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, driver_enable_opcode)
        print(f"Driver enabled for Axis {axis}.")
        # time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error enabling jogging for Axis {axis}: {e}")

def disable_driver(axis):
    command_register = 124 if axis == 1 else 1124
    driver_disable_opcode = 0x009E  # Disable Jogging (DJ) opcode
    try:
        client.write_register(command_register, driver_disable_opcode)
        print(f"Driver disabled for Axis {axis}.")
        # time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error disabling jogging for Axis {axis}: {e}")

def start_jogging(axis):
    command_register = 124 if axis == 1 else 1124
    start_jogging_opcode = 0x0096  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, start_jogging_opcode)
        print(f"Jogging mode enabled for Axis {axis}.")
        # time.sleep(0.5)  # Short delay to observe jogging
    except Exception as e:
        print(f"Error starting jogging for Axis {axis}: {e}")

def stop_jogging(axis):
    command_register = 124 if axis == 1 else 1124
    stop_jogging_opcode = 0x00D8  # Stop Jogging (SJ) opcode
    try:
        client.write_register(command_register, stop_jogging_opcode)
        print(f"Jogging mode stopped for Axis {axis}.")
        # time.sleep(0.5)  # Short delay to observe stopping
    except Exception as e:
        print(f"Error stopping jogging for Axis {axis}: {e}")


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


def write_speed(speed_value, axis, run_time=5):
    speed_register = 342 if axis == 1 else 1342

    try:
        high_word = (speed_value >> 16) & 0xFFFF  # Extract high 16 bits
        low_word = speed_value & 0xFFFF  # Extract low 16 bits

        # Write the 32-bit value as two consecutive 16-bit registers
        client.write_registers(speed_register, [high_word, low_word])

        print(f"Motor {axis} running at speed value {speed_value}.")

        # Run the motor for the specified time
        time.sleep(run_time)

        # Stop the motor by setting speed to 0
        high_word = 0
        low_word = 0
        client.write_registers(speed_register, [high_word, low_word])

        print(f"Motor {axis} stopped after {run_time} seconds.")
    except Exception as e:
        print(f"Error writing to speed register for Axis {axis}: {e}")

def write_accel(accel_value, axis):
    accel_register = 338 if axis == 1 else 1338  # Adjust for axis 2 if needed

    try:
        if 1 <= accel_value <= 30000:
            high_word = (accel_value >> 16) & 0xFFFF
            low_word = accel_value & 0xFFFF
            client.write_registers(accel_register, [high_word, low_word])
            print(f"Written accel value {accel_value} to Axis {axis} ")
            # time.sleep(0.5)
        else:
            print(f"Acceleration value {accel_value} is out of the allowed range (1-30000)")
    except Exception as e:
        print(f"Error writing to accel register for Axis {axis}: {e}")


def write_decel(decel_value, axis):
    decel_register = 340 if axis == 1 else 1340  # Adjust for axis 2 if needed

    try:
        if 1 <= decel_value <= 30000:
            high_word = (decel_value >> 16) & 0xFFFF
            low_word = decel_value & 0xFFFF
            client.write_registers(decel_register, [high_word, low_word])
            print(f"Written accel value {decel_value} to Axis {axis} ")
            # time.sleep(0.5)
        else:
            print(f"Acceleration value {decel_value} is out of the allowed range (1-30000)")
    except Exception as e:
        print(f"Error writing to decel register for Axis {axis}: {e}")

def control_motor(axis, speed_value, accel_value, decel_value, run_time):
    enable_driver(axis)
    start_jogging(axis)
    write_speed(speed_value, axis, run_time)
    write_accel(accel_value,axis)
    write_decel(decel_value,axis)
    stop_jogging(axis)
    disable_driver(axis)

if connect_modbus():
    motor1_thread = threading.Thread(target=control_motor, args=(axis_1, 10000,100,100, 8))
    motor2_thread = threading.Thread(target=control_motor, args=(axis_2, 10000,100,100, 8))
    motor1_thread.start()
    motor2_thread.start()

    # Wait for both threads to complete
    motor1_thread.join()
    motor2_thread.join()
    print("Motor has been stopped")
client.close() #Close the client connection
