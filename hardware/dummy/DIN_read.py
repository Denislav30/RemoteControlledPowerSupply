#!/usr/bin/env python3
"""Dummy DIN module - simulates digital input readings."""
import sys
import random

try:
    # Simulate 4 digital inputs (e.g., switches, status flags)
    # Format: "input1,input2,input3,input4" where each is 0 or 1
    din1 = str(random.randint(0, 1))
    din2 = str(random.randint(0, 1))
    din3 = str(random.randint(0, 1))
    din4 = str(random.randint(0, 1))
    
    # Output as CSV format for consistency with ADC_read
    print(f"{din1},{din2},{din3},{din4}")
    sys.exit(0)
    
except Exception as e:
    print(f"0,0,0,0", file=sys.stderr)
    sys.exit(1)