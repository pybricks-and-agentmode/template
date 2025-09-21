#!/usr/bin/env pybricks-micropython
"""
Simple MicroPython script for Pybricks hub
- Prints "Hello World" 
- Shows a blinking robot face pattern on the LED matrix
"""

from pybricks.hubs import PrimeHub
from pybricks.tools import wait, Matrix

# Initialize the hub
hub = PrimeHub()

# Print Hello World to console
print("Hello World!")

# Define a simple robot face pattern (5x5 matrix)
# This represents a simple robot face with sensors, eyes, and features
ROBOT_ON = Matrix([
    [100,   0, 100,   0, 100],  # Sensors and top features
    [  0, 100, 100, 100,   0],  # Head outline
    [100, 100,   0, 100, 100],  # Eyes and side features  
    [  0, 100,  50, 100,   0],  # Mouth and center area
    [  0,   0, 100,   0,   0]   # Bottom features
])

# Define an "off" pattern (all LEDs off)
ROBOT_OFF = Matrix([
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
])

# Alternative: just show robot eyes blinking
ROBOT_EYES_CLOSED = Matrix([
    [100,   0, 100,   0, 100],  # Sensors and top features
    [  0, 100, 100, 100,   0],  # Head outline
    [100,  50,   0,  50, 100],  # Closed eyes (dimmer) and side features  
    [  0, 100,  50, 100,   0],  # Mouth and center area
    [  0,   0, 100,   0,   0]   # Bottom features
])

print("Starting robot animation...")

# Main animation loop - blink the robot
try:
    while True:
        # Show the robot
        hub.display.icon(ROBOT_ON)
        wait(1000)  # Show for 1 second
        
        # Quick blink - eyes closed
        hub.display.icon(ROBOT_EYES_CLOSED)
        wait(150)   # Brief blink
        
        # Back to eyes open
        hub.display.icon(ROBOT_ON) 
        wait(1000)  # Show for 1 second
        

        
        print("Blink!")  # Print to console each blink cycle

except KeyboardInterrupt:
    # Clean exit when stopped
    print("Animation stopped")
    hub.display.off()
