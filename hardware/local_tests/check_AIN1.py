import smbus
import time

bus = smbus.SMBus(1)
addr = 0x58
cmds = [0x30, 0x31, 0x32, 0x33]

print("CH | RAW | VOLT")

for i, cmd in enumerate(cmds):
    bus.write_byte(addr, cmd)
    time.sleep(0.05)

    data = bus.read_i2c_block_data(addr, cmd, 2)

    raw = (data[0] << 8) | data[1]

    voltage = (raw / 4095.0) * 3.3   # 12-bit assumption

    print(f"AIN{i} | {raw} | {voltage:.3f} V")