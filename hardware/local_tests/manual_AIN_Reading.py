import smbus
import time

bus = smbus.SMBus(1)
address = 0x58

def read_analog_simple(channel_cmd):
    try:
        bus.write_byte(address, channel_cmd)
        time.sleep(0.1)
        data = bus.read_i2c_block_data(address, channel_cmd, 2)
        raw_value = (data[1] << 8) | data[0]
        
        voltage = (raw_value * 3.3) / 1023
        return raw_value, voltage
    except:
        return None, None

print("Четене по стандартен метод...")
try:
    while True:
        raw, v = read_analog_simple(0x30)
        if raw is not None:
            if raw < 1024:
                print(f"RAW: {raw:4d} | Бинарно: {raw:010b} | Напрежение: {v:.3f} V")
        time.sleep(2)
except KeyboardInterrupt:
    print("Край.")