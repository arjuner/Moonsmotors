#This script runs the motors in all directions.
#Edit the run_time for duration 
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
    command_register = 124 if axis == 1 else 1124
    driver_enable_opcode = 0x009F  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, driver_enable_opcode)
        print(f"Driver enabled for Axis {axis}.")
    except Exception as e:
        print(f"Error enabling jogging for Axis {axis}: {e}")

def disable_driver(axis):
    command_register = 124 if axis == 1 else 1124
    driver_disable_opcode = 0x009E  # Disable Jogging (DJ) opcode
    try:
        client.write_register(command_register, driver_disable_opcode)
        print(f"Driver disabled for Axis {axis}.")
    except Exception as e:
        print(f"Error disabling jogging for Axis {axis}: {e}")

def start_jogging(axis):
    command_register = 124 if axis == 1 else 1124
    start_jogging_opcode = 0x0096  # Start Jogging (CJ) opcode
    try:
        client.write_register(command_register, start_jogging_opcode)
        print(f"Jogging mode enabled for Axis {axis}.")
    except Exception as e:
        print(f"Error starting jogging for Axis {axis}: {e}")

def stop_jogging(axis):
    command_register = 124 if axis == 1 else 1124
    stop_jogging_opcode = 0x00D8  # Stop Jogging (SJ) opcode
    try:
        client.write_register(command_register, stop_jogging_opcode)
        print(f"Jogging mode stopped for Axis {axis}.")
    except Exception as e:
        print(f"Error stopping jogging for Axis {axis}: {e}")

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

def control_motor(axis, speed_value, run_time=10):
    # enable_driver(axis)
    # start_jogging(axis)
    write_speed(speed_value, axis, run_time)
    # stop_jogging(axis)
    # disable_driver(axis)

if connect_modbus():
    # Use threading to control both motors simultaneously
    enable_driver(axis_1)
    enable_driver(axis_2)
    start_jogging(axis_1)
    start_jogging(axis_2)

    motor1_thread = threading.Thread(target=control_motor, args=(axis_1, 5000, 5))
    motor2_thread = threading.Thread(target=control_motor, args=(axis_2, 5000, 5))
    motor1_thread1 = threading.Thread(target=control_motor, args=(axis_1, -5000, 5))
    motor2_thread1 = threading.Thread(target=control_motor, args=(axis_2, -5000, 5))
    motor1_thread2 = threading.Thread(target=control_motor, args=(axis_1, 5000, 5))
    motor2_thread2 = threading.Thread(target=control_motor, args=(axis_2, -5000, 5))
    motor1_thread3 = threading.Thread(target=control_motor, args=(axis_1, -5000, 5))
    motor2_thread3= threading.Thread(target=control_motor, args=(axis_2, 5000, 5))


    # Start both threads
    motor1_thread.start()
    motor2_thread.start()

    # Wait for both threads to complete
    motor1_thread.join()
    motor2_thread.join()

    print("Both motors have stopped.")
    # Start both threads
    motor1_thread1.start()
    motor2_thread1.start()

    # Wait for both threads to complete
    motor1_thread1.join()
    motor2_thread1.join()

    print("Both motors have stopped.")
    # Start both threads
    motor1_thread2.start()
    motor2_thread2.start()

    # Wait for both threads to complete
    motor1_thread2.join()
    motor2_thread2.join()

    print("Both motors have stopped.")
    # Start both threads
    motor1_thread3.start()
    motor2_thread3.start()

    # Wait for both threads to complete
    motor1_thread3.join()
    motor2_thread3.join()

    stop_jogging(axis_1)
    stop_jogging(axis_2)
    disable_driver(axis_1)
    disable_driver(axis_2)
# Close the client connection
client.close()
