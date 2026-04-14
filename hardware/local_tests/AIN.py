import smbus
import time

BUS = smbus.SMBus(1)
ADDR = 0x58

def get_voltage(channel):
    # Командите за PCF8591 са 0x40 (AIN0), 0x41 (AIN1) и т.н.
    BUS.write_byte(ADDR, 0x40 + channel)
    BUS.read_byte(ADDR) # Празно четене (изчистване на стария байт)
    raw = BUS.read_byte(ADDR) # Реално четене
    return (raw / 255.0) * 3.3

if __name__ == "__main__":
    try:
        while True:
            v = get_voltage(0) # Четем AIN0
            temp_c = (v * 100) - 273.15
            print(f"Voltage: {v:.2f}V | Temp: {temp_c:.1f}°C")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")