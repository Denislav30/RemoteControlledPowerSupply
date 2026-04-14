import smbus
import time

# Конфигурация
I2C_BUS = 1
DEVICE_ADDR = 0x58
# ВАЖНО: 0x30 е първият вход (AIN1), 0x31 е вторият (AIN2)
AIN1_CMD = 0x30 

bus = smbus.SMBus(I2C_BUS)

def read_raw_adc(address, command):
    """Чете суровата 10-битова стойност от платката."""
    try:
        # 1. Изпращаме команда за избор на канал
        bus.write_byte(address, command)
        
        # Кратка пауза, за да може ADC-то на Olimex да се стабилизира
        time.sleep(0.05)
        
        # 2. Четем 2 байта (Block Read)
        # Повечето ревизии на MOD-IO връщат [Low Byte, High Byte]
        data = bus.read_i2c_block_data(address, command, 2)
        l_byte = data[0]
        h_byte = data[1]
        
        # 3. Сглобяваме 10-битовото число
        # Взимаме l_byte и добавяме 2-та бита от h_byte на позиции 8 и 9
        # (Стандартна Little Endian подредба)
        raw_value = l_byte | ((h_byte & 0x03) << 8)
        
        return raw_value
    except Exception as e:
        print(f"Грешка при комуникация: {e}")
        return None

def get_voltage(samples=10):
    """Прави няколко измервания и връща осреднено напрежение."""
    valid_readings = []
    
    for _ in range(samples):
        val = read_raw_adc(DEVICE_ADDR, AIN1_CMD)
        if val is not None:
            valid_readings.append(val)
        time.sleep(0.02) # Бързо вземане на проби
    
    if not valid_readings:
        return None, None
    
    # Осредняваме, за да премахнем шума (ония скокове от 128/256 единици)
    avg_raw = sum(valid_readings) / len(valid_readings)
    
    # Формула: (ADC * Vref) / Max_Steps
    # Използваме 1024 за 10-битово ADC
    voltage = (avg_raw * 3.3) / 1024
    
    return voltage, avg_raw

# ГЛАВЕН ЦИКЪЛ
print(f"--- MOD-IO ADC Четец ---")
print(f"Адрес на устройството: {hex(DEVICE_ADDR)}")
print(f"Използван канал: {hex(AIN1_CMD)}")
print("Натиснете Ctrl+C за спиране.\n")

try:
    while True:
        v, raw = get_voltage(samples=10)
        
        if v is not None:
            # При 770mV трябва да виждаш RAW около 239
            print(f"Стойност (RAW): {raw:6.1f} | Напрежение: {v:.3f} V")
        else:
            print("Грешка: Не мога да прочета данни от I2C шината.")
            
        time.sleep(5) # Изчакване 5 секунди преди следващото четене

except KeyboardInterrupt:
    print("\nСпиране на скрипта...")