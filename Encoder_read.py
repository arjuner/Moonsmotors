from pymodbus.client import ModbusSerialClient

# Modbus Configuration
PORT = 'COM4'  # Replace with your serial port
BAUDRATE = 9600
TIMEOUT = 5
UNIT_ID = 1  # Replace with your Modbus device ID

# Define register names based on the reference provided
REGISTER_NAMES = {
    #1: "Status Code (SC)",
    #3: "Digital Output Status (IO)",
    #5: "Digital Input Status (IS)",
    #6: "Immediate Absolute Position (IP)",
    #7: "Secondary Encoder Position (EQ)",
    9: "Encoder Position (EP)",
    11: "Encoder Position (EP)",
    #13: "Internal Use",
}

# Function to combine two consecutive 16-bit register values into a single 32-bit long value
def combine_registers(high, low):
    return (high << 16) | low

# Function to read and display registers as long-type values
def read_registers_as_long(client, start_address, count):
    try:
        # Read the specified number of registers starting at `start_address`
        result = client.read_holding_registers(start_address, count, slave=UNIT_ID)

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
                print(f"  {register_name}: {combined_value} ({40000 + register_number})")
        else:
            print(f"Unexpected response format: {result}")
    except Exception as e:
        print(f"Exception occurred while reading registers: {e}")

# Main Execution
if __name__ == "__main__":
    # Initialize Modbus client
    client = ModbusSerialClient(port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT, parity='N', stopbits=1, bytesize=8)

    if client.connect():
        print("Modbus Connection Successful")
        try:
            # Read registers from 1 to 20 as long type (each long spans two registers)
            read_registers_as_long(client, start_address=11, count=2)
        finally:
            client.close()
            print("Connection closed.")
    else:
        print("Failed to connect to Modbus device")
