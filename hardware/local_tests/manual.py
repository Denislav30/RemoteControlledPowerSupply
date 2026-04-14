import smbus
import time

bus = smbus.SMBus(1)
address = 0x58

def read_analog_simple(channel_cmd):
    try:
        # Изпращаме команда (напр. 0x30 за AIN1)
        bus.write_byte(address, channel_cmd)
        time.sleep(0.05)
        
        # Четем 2 байта стандартно
        data = bus.read_i2c_block_data(address, channel_cmd, 2)
        
        # Сглобяваме без никакви цикли и обръщания!
        # Low byte е data[0], High byte е data[1]
        raw_value = (data[1] << 8) | data[0]
        
        voltage = (raw_value * 3.3) / 1023
        return raw_value, voltage
    except:
        return None, None

print("Четене по стандартен метод (без Bit Reversal)...")
try:
    while True:
        raw, v = read_analog_simple(0x30)
        if raw is not None:
            print(f"RAW: {raw:4d} | Бинарно: {raw:010b} | Напрежение: {v:.3f} V")
        time.sleep(2)
except KeyboardInterrupt:
    print("Край.")