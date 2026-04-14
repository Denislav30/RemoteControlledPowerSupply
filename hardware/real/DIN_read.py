import smbus2

ADDRESS = 0x58
bus = smbus2.SMBus(1)

try:
    # Read Digital Input register
    din_state = bus.read_byte_data(ADDRESS, 0x20)
    
    # Extract bits 0-3
    d1 = 1 if (din_state & 0x01) else 0
    d2 = 1 if (din_state & 0x02) else 0
    d3 = 1 if (din_state & 0x04) else 0
    d4 = 1 if (din_state & 0x08) else 0
    
    print(f"{d1},{d2},{d3},{d4}")
except Exception:
    print("0,0,0,0")