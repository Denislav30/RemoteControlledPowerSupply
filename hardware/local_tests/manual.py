import smbus
import time

# Настройки
I2C_BUS = 1
DEVICE_ADDR = 0x58
AIN1_CMD = 0x31

bus = smbus.SMBus(I2C_BUS)

def read_analog_olimex_way(address, command):
    try:
        # 1. i2cStart() + i2cSend(0xb0) + i2cSend(0x30) + i2cStop()
        bus.write_byte(address, command)
        time.sleep(0.05) # Пауза за обработка
        
        # 2. i2cStart() + i2cSend(0xb1) + четене на 2 байта
        # data[0] е l_byte, data[1] е h_byte
        data = bus.read_i2c_block_data(address, command, 2)
        l_byte = data[0]
        h_byte = data[1]
        
        # --- СТАРТ НА АЛГОРИТЪМА ОТ МАНУАЛА ---
        analog = 0
        
        # "Since l_byte is (LSB:MSB) we need to convert it to (MSB:LSB)"
        # Този цикъл обръща битовете огледално
        temp_l = l_byte
        for index in range(8):
            # (l_byte & 0x80) ? 1 : 0
            bit = 1 if (temp_l & 0x80) else 0
            analog |= (bit << index)
            temp_l = (temp_l << 1) & 0xFF # l_byte <<= 1
            
        # "Now add the high 2 bit to the value"
        # Бит 1 на h_byte отива на позиция 8
        if h_byte & 0x02:
            analog |= (1 << 8)
        # Бит 0 на h_byte отива на позиция 9
        if h_byte & 0x01:
            analog |= (1 << 9)
            
        # Изчисляване на напрежението по формулата от мануала
        voltage = (analog * 3.3) / 1023
        # --- КРАЙ НА АЛГОРИТЪМА ---
        
        return analog, voltage, l_byte, h_byte

    except Exception as e:
        print(f"Грешка: {e}")
        return None, None, None, None

# Принт заглавия
print(f"{'RAW (Dec)':<10} | {'Binary (10bit)':<15} | {'L-Byte (Raw)':<12} | {'Voltage':<10}")
print("-" * 65)

try:
    while True:
        analog, voltage, l_raw, h_raw = read_analog_olimex_way(DEVICE_ADDR, AIN1_CMD)
        
        if analog is not None:
            # Показваме десетичната стойност, бинарната и напрежението
            bin_str = f"{analog:010b}"
            formatted_bin = f"{bin_str[:2]} {bin_str[2:]}" # Разделяме на 2 + 8 бита
            
            print(f"{analog:<10d} | {formatted_bin:<15} | {l_raw:08b}   | {voltage:.3f} V")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("\nСпряно.")