import sys
import json
import smbus2

ADDRESS = 0x58
bus = smbus2.SMBus(1)

if len(sys.argv) > 4:
    # Map arguments to bits: Fan1=bit0, Fan2=bit1, Fan3=bit2, Auto/Man=bit3
    # Note: Using your logic where arg[1] is Auto/Man
    relay_mask = 0
    if sys.argv[1] == "1": relay_mask |= 0x08 # Auto/Man
    if sys.argv[2] == "1": relay_mask |= 0x01 # Fan 1
    if sys.argv[3] == "1": relay_mask |= 0x02 # Fan 2
    if sys.argv[4] == "1": relay_mask |= 0x04 # Fan 3
    # bit 0x08 could be used for a 4th relay or an indicator LED
    
    try:
        bus.write_byte_data(ADDRESS, 0x10, relay_mask)
        
        # Log the state to JSON for the backend
        data = {
            "mode": "Manual" if sys.argv[1] == "1" else "Auto",
            "fan1": sys.argv[2],
            "fan2": sys.argv[3],
            "fan3": sys.argv[4]
        }
        with open("hw_state.json", "w") as f:
            json.dump(data, f)
    except Exception as e:
        pass