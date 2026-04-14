import smbus2
import time

# Mod-IO I2C address
ADDRESS = 0x58
bus = smbus2.SMBus(1) # Usually I2C-1 on A20

def read_modio_adc(channel):
    # Mod-IO registers for ADC start at 0x30
    # Returns 10-bit value (high byte, low byte)
    reg = 0x30 + channel
    data = bus.read_i2c_block_data(ADDRESS, reg, 2)
    return (data[0] << 8) | data[1]

try:
    # Reading Mod-IO ADC0 (e.g., Temperature) and ADC1 (e.g., Voltage)
    raw_temp = read_modio_adc(0)
    raw_volt = read_modio_adc(1)
    
    # Scaling (Example: 10-bit 3.3V ref or 10V divider - adjust to your sensors)
    temp = round((raw_temp * 3.3 / 255) * 10, 2) 
    voltage = round((raw_volt * 3.3 / 255) * 4, 2)

    print(f"{temp},{voltage}")
except Exception:
    print("0.0,0.0")