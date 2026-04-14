import smbus2
import time

# Конфигурация
ADDRESS = 0x58
bus = smbus2.SMBus(1)

def read_modio_adc(channel):
    # Регистрите започват от 0x30 (AIN1 = 0x30, AIN2 = 0x31 и т.н.)
    reg = 0x30 + channel
    
    # 1. Изпращаме командата към платката
    bus.write_byte(ADDRESS, reg)
    # Малка пауза за стабилност на ADC-то
    time.sleep(0.05)
    
    # 2. Четем 2 байта
    data = bus.read_i2c_block_data(ADDRESS, reg, 2)
    
    # ВАЖНО: Използваме доказано работещата подредба за твоята платка
    # Low byte е data[0], High byte е data[1]
    return (data[1] << 8) | data[0]

try:
    # Четене на двата канала
    raw_adc0 = read_modio_adc(0) # AIN1
    raw_adc1 = read_modio_adc(1) # AIN2
    
    # Скалиране (използваме 1023 за 10-битова резолюция)
    # Формулите са по твоя пример, но с коригирана резолюция 1023
    temp = round((raw_adc0 * 3.3 / 1023) * 10, 2)
    voltage = round((raw_adc1 * 3.3 / 1023) * 4, 2)

    # Принтираме само резултата в желания формат
    print(f"{temp},{voltage}")

except Exception:
    # При грешка връщаме занулени стойности
    print("0.0,0.0")
finally:
    bus.close()