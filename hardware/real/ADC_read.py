import smbus2
import time

# Mod-IO I2C адрес
ADDRESS = 0x58
bus = smbus2.SMBus(1)

def read_modio_adc_raw(channel):
    """Изпълнява алгоритъма на Olimex за четене на сурови данни."""
    try:
        reg = 0x30 + channel
        bus.write_byte(ADDRESS, reg)
        time.sleep(0.05)
        
        data = bus.read_i2c_block_data(ADDRESS, reg, 2)
        l_byte = data[0]
        h_byte = data[1]
        
        # Bit Reversal на Low Byte (от първия файл)
        analog = 0
        temp_l = l_byte
        for index in range(8):
            bit = 1 if (temp_l & 0x80) else 0
            analog |= (bit << index)
            temp_l = (temp_l << 1) & 0xFF
            
        # Мапиране на High Byte (от първия файл)
        if h_byte & 0x02:
            analog |= (1 << 8)
        if h_byte & 0x01:
            analog |= (1 << 9)
            
        return analog
    except Exception:
        return None

def get_safe_adc(channel, retries=3):
    """Проверява дали стойността е валидна (< 1024) и опитва отново при грешка."""
    for _ in range(retries):
        raw = read_modio_adc_raw(channel)
        
        # Проверка: стойността трябва да е число и да е в границите на 10 бита
        if raw is not None and raw < 1024:
            return raw
        
        # Ако данните са грешни, изчакваме малко и опитваме пак
        time.sleep(0.1)
    
    return None

try:
    # Опитваме се да прочетем двата канала безопасно
    raw_0 = get_safe_adc(0)
    raw_1 = get_safe_adc(1)
    
    # Ако след опитите все още нямаме валидни данни, прекратяваме
    if raw_0 is None or raw_1 is None:
        raise ValueError("Invalid data or I2C error")

    # Изчисляване на напрежението (0-3.3V)
    v_base_0 = (raw_0 * 3.3) / 1023
    v_base_1 = (raw_1 * 3.3) / 1023

    # Скалиране според твоите нужди (x10 и x4)
    temp = round(v_base_0 * 10, 2) 
    voltage = round(v_base_1 * 4, 2)

    # Краен изход
    print(f"{temp},{voltage}")

except Exception:
    # При окончателна грешка връщаме занулени стойности
    print("0.0,0.0")
finally:
    bus.close()