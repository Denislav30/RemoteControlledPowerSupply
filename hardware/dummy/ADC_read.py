#!/usr/bin/env python3
"""Dummy ADC module - simulates temperature and voltage readings."""
import sys
import random

try:
    # Generate realistic temperature (20-45°C) and voltage (10-14V) readings
    # These ranges simulate normal operation and potential overheating scenarios
    temp = round(random.uniform(20.0, 45.0), 2)
    voltage = round(random.uniform(10.0, 14.0), 2)
    
    # Output as CSV for the backend to parse: "temperature,voltage"
    print(f"{temp},{voltage}")
    sys.exit(0)
except Exception as e:
    print(f"0.0,0.0", file=sys.stderr)
    sys.exit(1)