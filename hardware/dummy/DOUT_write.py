import sys
import json

if len(sys.argv) > 1:
    data = {
        "led_dout1": sys.argv[1],  # 1 = Manual, 0 = Auto
        "fan1_dout2": sys.argv[2],
        "fan2_dout3": sys.argv[3],
        "fan3_dout4": sys.argv[4]
    }
    with open("hw_state.json", "w") as f:
        json.dump(data, f)