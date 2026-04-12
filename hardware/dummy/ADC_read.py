import sys
import random

# Generate random temp (24-31) and random voltage (0-14)
temp = round(random.uniform(24.0, 41.0), 2)
voltage = round(random.uniform(0.0, 14.0), 2)

# Output for the backend to read
print(f"{temp},{voltage}")