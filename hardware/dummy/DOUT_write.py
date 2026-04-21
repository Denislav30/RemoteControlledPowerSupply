#!/usr/bin/env python3
"""Dummy DOUT module - simulates digital output control."""
import sys
import json
from pathlib import Path

try:
    if len(sys.argv) < 5:
        print("Error: requires 4 arguments (led, fan1, fan2, fan3)", file=sys.stderr)
        sys.exit(1)
    
    # Parse command line arguments: LED state and 3 fan states
    led_state = sys.argv[1]      # "0" = Auto mode, "1" = Manual mode
    fan1_state = sys.argv[2]     # "0" = Off, "1" = On
    fan2_state = sys.argv[3]     # "0" = Off, "1" = On
    fan3_state = sys.argv[4]     # "0" = Off, "1" = On
    
    # Validate inputs are binary
    for val, name in [(led_state, 'led'), (fan1_state, 'fan1'), (fan2_state, 'fan2'), (fan3_state, 'fan3')]:
        if val not in ('0', '1'):
            raise ValueError(f"Invalid {name} state: {val}. Must be 0 or 1")
    
    # Track state in JSON file
    data = {
        "led_dout1": led_state,
        "fan1_dout2": fan1_state,
        "fan2_dout3": fan2_state,
        "fan3_dout4": fan3_state
    }
    
    # Write state to hw_state.json
    state_file = Path("hw_state.json")
    with open(state_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print("OK")
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)