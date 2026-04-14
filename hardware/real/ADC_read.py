import smbus2
import time

# Mod-IO I2C адрес
ADDRESS = 0x58
bus = smbus2.SMBus(1)    

def read_analog_simple(channel_cmd):
    try:
        reg = 0x30 + channel_cmd
        bus.write_byte(ADDRESS, reg)
        time.sleep(0.1)
        data = bus.read_i2c_block_data(ADDRESS, reg, 2)
        raw_value = (data[1] << 8) | data[0]
        
        voltage = (raw_value * 3.3) / 1023
        return raw_value, voltage
    except:
        return None, None

def get_safe_adc(channel, retries=3):
    for _ in range(retries):
        raw, voltage = read_analog_simple(channel)
        
        if raw is not None and raw < 1024:
            return voltage
        
        # Ако данните са грешни, изчакваме малко и опитваме пак
        time.sleep(0.1)
    
    return None

try:
    # Опитваме се да прочетем двата канала безопасно
    voltage_0 = get_safe_adc(0)
    voltage_1 = get_safe_adc(1)
    
    # Ако след опитите все още нямаме валидни данни, прекратяваме
    if voltage_0 is None or voltage_1 is None:
        raise ValueError("Invalid data or I2C error")

    temp = (voltage_0/0.01) - 273.15
    
    voltage = voltage_1

    # Краен изход
    print(f"{temp},{voltage}")

except Exception:
    # При окончателна грешка връщаме занулени стойности
    print("0.0,0.0")
finally:
    bus.close()