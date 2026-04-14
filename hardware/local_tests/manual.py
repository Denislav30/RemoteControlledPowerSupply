import smbus
import time

# --- КОНФИГУРАЦИЯ ---
I2C_BUS = 1
DEVICE_ADDR = 0x58
AIN1_CMD = 0x30  # 0x30 за AIN1, 0x31 за AIN2
V_REF = 3.3      # Референтно напрежение на платката
# Видяхме, че при 770mV платката отчита половината, затова слагаме фактор 2.
# Ако при 3.3V започнеш да виждаш 6.6V, промени това на 1.0
CALIBRATION_FACTOR = 2.0 

bus = smbus.SMBus(I2C_BUS)

def reverse_bits(n):
    """Обръща битовете на байта огледално (Bit Reversal)."""
    result = 0
    for i in range(8):
        bit = (n >> (7 - i)) & 1
        result |= (bit << i)
    return result

def read_mod_io_adc(address, command):
    try:
        # 1. Изпращаме команда за четене
        bus.write_byte(address, command)
        time.sleep(0.05)
        
        # 2. Четем 2 байта (LSB и MSB)
        data = bus.read_i2c_block_data(address, command, 2)
        l_byte = data[0]
        h_byte = data[1]
        
        # 3. Обръщаме битовете на l_byte (Olimex специфично)
        analog_low = reverse_bits(l_byte)
        
        # 4. Сглобяваме 10-битовата стойност от h_byte
        # Бит 1 на h_byte е позиция 8 (256), Бит 0 е позиция 9 (512)
        analog_high = 0
        if h_byte & 0x02: analog_high |= (1 << 8)
        if h_byte & 0x01: analog_high |= (1 << 9)
        
        analog_total = analog_low | analog_high
        
        # 5. Изчисляваме напрежението
        # Формула: (ADC * Vref / 1023) * Factor
        voltage = ((analog_total * V_REF) / 1023) * CALIBRATION_FACTOR
        
        return analog_total, voltage, l_byte, h_byte
    except Exception as e:
        print(f"Грешка при четене: {e}")
        return None

# --- ГЛАВЕН ЦИКЪЛ ---
print(f"{'RAW (Dec)':<10} | {'Binary (10bit)':<15} | {'Voltage':<10}")
print("-" * 45)

try:
    while True:
        result = read_mod_io_adc(DEVICE_ADDR, AIN1_CMD)
        
        if result:
            analog, v, l_raw, h_raw = result
            # Форматираме бинарното число за прегледност (2 бита + 8 бита)
            bin_str = f"{analog:010b}"
            formatted_bin = f"{bin_str[:2]} {bin_str[2:]}"
            
            print(f"{analog:<10d} | {formatted_bin:<15} | {v:.3f} V")
        
        time.sleep(2) # Четем на всеки 2 секунди

except KeyboardInterrupt:
    print("\nСкриптът е спрян.")