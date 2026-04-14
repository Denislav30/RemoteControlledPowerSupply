import smbus
import time

print("I2C Bus opened...")

def decode_adc(raw):
    """
    Simulates correct vs broken shift decoding.
    """

    # ❗ SIMULATED RAW EXTENSION (8-bit → 12-bit style)
    # ако device реално връща 12-bit в 2 bytes, а ти четеш само 1 byte,
    # тук просто разширяваме за тест
    raw_12bit_like = raw << 4   # симулация на "пълен ADC frame"

    # ❗ КЛАСИЧЕСКИ BUG (грешен shift)
    wrong_shift = raw_12bit_like >> 4   # или >> 3 (както каза)

    # ✔️ правилен вариант (ако беше 12-bit ADC)
    correct = (raw_12bit_like >> 0) & 0x0FFF

    return wrong_shift, correct


def read_all_analog():
    bus_number = 1
    device_address = 0x58
    commands = [0x30, 0x31, 0x32, 0x33]

    try:
        bus = smbus.SMBus(bus_number)

        print(f"{'CH':<6} | {'RAW8':<6} | {'WRONG':<8} | {'CORRECT':<8} | {'V_wrong':<8}")
        print("-"*60)

        for i, cmd in enumerate(commands):
            bus.write_byte(device_address, cmd)
            time.sleep(0.05)

            raw = bus.read_byte(device_address)

            wrong, correct = decode_adc(raw)

            # voltage based on WRONG interpretation (buggy system)
            voltage_wrong = (wrong / 4095.0) * 3.3

            print(f"AIN{i:<3} | {raw:<6} | {wrong:<8} | {correct:<8} | {voltage_wrong:.2f}V")

    except Exception as e:
        print(f"Error reading I2C: {e}")


if __name__ == "__main__":
    read_all_analog()