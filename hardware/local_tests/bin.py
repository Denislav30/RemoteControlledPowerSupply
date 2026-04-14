import smbus
import time

# Конфигурация
I2C_BUS = 1
DEVICE_ADDR = 0x58
AIN1_CMD = 0x30  # Използвай 0x30 за AIN1

bus = smbus.SMBus(I2C_BUS)

def read_raw_adc(address, command):
    try:
        # 1. Заявка към платката
        bus.write_byte(address, command)
        time.sleep(0.05)
        
        # 2. Четем LSB и MSB
        data = bus.read_i2c_block_data(address, command, 2)
        l_byte = data[0]
        h_byte = data[1]
        
        # 3. Сглобяваме 10-битовото число (Little Endian)
        # Взимаме l_byte и добавяме 2 бита от h_byte
        raw_value = l_byte | ((h_byte & 0x03) << 8)
        
        return raw_value
    except Exception as e:
        return None

try:
    print(f"{'RAW (Dec)':<10} | {'RAW (Binary)':<12} | {'Voltage':<10}")
    print("-" * 40)

    while True:
        # Взимаме една моментална стойност за бинарния принт
        raw = read_raw_adc(DEVICE_ADDR, AIN1_CMD)
        
        if raw is not None:
            # Превръщаме в напрежение
            voltage = (raw * 3.3) / 1024
            
            # ФОРМАТИРАНЕ:
            # :4d   -> десетично число с 4 символа разстояние
            # :010b -> бинарно число, запълнено с нули до 10-ия бит
            binary_str = f"{raw:010b}"
            
            # Разделяме бинарното число на [2 бита] и [8 бита] за по-лесно четене
            # Това съответства на High Byte и Low Byte
            formatted_bin = f"{binary_str[:2]} {binary_str[2:]}"
            
            print(f"{raw:<10d} | {formatted_bin:<12} | {voltage:.3f} V")
        else:
            print("Грешка при четене!")

        # Четем бързо (на всеки 1 секунда), за да хванем разликите
        time.sleep(1)

except KeyboardInterrupt:
    print("\nСпиране...")