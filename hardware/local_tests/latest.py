import smbus
import time

def reverse_bits(n):
    """Обръща битовете на 8-битово число огледално (bit reversal)."""
    return int('{:08b}'.format(n)[::-1], 2)

def read_analog(bus, address, channel_cmd):
    try:
        # 1. Изпращаме команда към платката кой канал искаме да четем
        bus.write_byte(address, channel_cmd)
        
        # Малко закъснение, за да може ADC-то да обработи заявката
        time.sleep(0.05)
        
        # 2. Четем 2 байта (Word)
        # Връща се като [Low Byte, High Byte] в SMBus
        raw_word = bus.read_word_data(address, channel_cmd)
        
        l_byte = raw_word & 0xFF
        h_byte = (raw_word >> 8) & 0xFF
        
        # 3. Прилагаме логиката на Olimex:
        # Обръщаме огледално битовете на ниския байт
        analog_low = reverse_bits(l_byte)
        
        # Взимаме само бит 0 и бит 1 от високия байт за позиции 8 и 9
        analog_high = 0
        if h_byte & 0x01: analog_high |= (1 << 9) # Бит 9
        if h_byte & 0x02: analog_high |= (1 << 8) # Бит 8
        
        # Сглобяваме крайната 10-битова стойност
        analog_value = analog_low | analog_high
        
        # Превръщаме в напрежение (по формула от мануала)
        voltage = (analog_value * 3.3) / 1023
        return voltage, analog_value

    except Exception as e:
        print(f"Грешка при четене: {e}")
        return None, None

# Настройки
I2C_BUS = 1
DEVICE_ADDR = 0x58
AIN1_CMD = 0x31  # Променете на 0x31 за AIN2 и т.н.1

bus = smbus.SMBus(I2C_BUS)

print(f"Започва четене на AIN1 (0x30) на всеки 5 секунди...")
print("-" * 40)

try:
    while True:
        v, raw = read_analog(bus, DEVICE_ADDR, AIN1_CMD)
        
        if v is not None:
            print(f"Стойност (RAW): {raw:4d} | Напрежение: {v:.3f} V")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("\nСкриптът е спрян от потребителя.")