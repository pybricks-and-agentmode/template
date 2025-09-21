# Quickly get started with Pybricks

Create a new virtual environment, install the dependencies from `requirements.txt`, and open thefolder in VS Code.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Robot Blink Script

This repository includes a simple MicroPython script for Pybricks hubs:

### `robot_blink.py` - Robot Face Animation
A script that prints "Hello World" and displays a blinking robot face using Matrix patterns on the LED display. The robot has sensors, eyes, and features that create a friendly animated face with periodic blinking.

### `.vscode/launch.json` - VS Code Debug Configuration
A sample configuration for debugging Pybricks scripts directly from VS Code using the `pybricksdev` tool.

## How to Run

- F5 to start debugging in VS Code (ensure that you updated the launch.json with your hub name)
- In terminal: ```pybricksdev run ble robot_blink.py -n "John"```
- Or run via USB connection: ```pybricksdev run usb robot_blink.py```

### Expected Behavior
- Console prints "Hello World!" and animation status messages
- LED matrix displays a robot face with sensors, eyes, and features
- Eyes blink periodically (closed eyes are dimmer)
- Pattern loops continuously with "Blink!" messages until stopped

### Compatible Hubs

- LEGO SPIKE Prime Hub
- Not tested on other hubs but should work with minor adjustments

### Note
- Make sure your hub is powered on and connected before running the scripts.
- Check the Pybricks documentation for more information on supported features and limitations.
- When using Bluetooth, the Spike Prime Hub should be blinking blue to indicate it is in pairing mode.

The import errors shown in VS Code are normal - these scripts are designed to run on the MicroPython environment on the Pybricks hub, not in your local Python environment.
