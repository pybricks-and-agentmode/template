# Pybricks Robotics Development Guide

## Project Overview
This is a **Pybricks MicroPython robotics project** for LEGO SPIKE Prime Hub. Code runs on the hub's MicroPython environment, not local Python - expect import errors in VS Code (this is normal).

## Critical Architecture Knowledge

### Dual-Environment Setup
- **Local Environment**: VS Code with `pybricksdev` tooling for development/debugging
- **Target Environment**: MicroPython on LEGO SPIKE Prime Hub where code actually executes
- **Key Insight**: Local Python is only for tooling; robot scripts use hub's MicroPython runtime

### Hardware Configuration
See `architecture/robot_wiring.md` for current port mappings and sensor configurations. Always check this file before writing hardware-specific code.

## Essential Development Workflows

### Environment Setup (Required First Step)
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Agent Mode Automation Rules

### Robot Name Discovery (REQUIRED PROCESS)
When running code via terminal commands, the agent MUST:
1. **ALWAYS check `.vscode/launch.json` FIRST** to extract the robot name
2. **Parse the `-n` argument** from the "args" array in the Pybricks configuration
3. **Use that exact name** in terminal commands automatically
4. **Never ask user for robot name** if it's already in launch.json
5. **If not found** try the same command again up to 2 more times

### Example Workflow:
```bash
# Agent should automatically extract robot name from launch.json and use:
pybricksdev run ble script_name.py -n "ExtractedName"
# NOT: pybricksdev run ble script_name.py (missing name)
```

### Mandatory Pre-Run Checklist
Before running ANY code, agent must verify:
- [ ] Virtual environment activated (`source venv/bin/activate`)
- [ ] Hub powered and in pairing mode (blinking blue)
- [ ] Robot name extracted from `.vscode/launch.json` if using terminal
- [ ] Hardware ports match `architecture/robot_wiring.md`

### Debug Configuration
Update `.vscode/launch.json` with your hub's actual name in the `-n` argument. The debugger uses the virtual environment's Python to run `pybricksdev` module.

## Project-Specific Patterns

### Script Structure Convention (REQUIRED PATTERN)
Every robot script MUST include:
```python
#!/usr/bin/env pybricks-micropython
from pybricks.hubs import PrimeHub
from pybricks.tools import wait, Matrix

hub = PrimeHub()  # ALWAYS initialize first

try:
    # Main logic here
    # Define patterns as constants
    # Main loop logic
    pass
except KeyboardInterrupt:
    print("Program interrupted")
finally:
    hub.display.off()  # ALWAYS cleanup
```

### MANDATORY ACTIONS (Never Skip)
1. **ALWAYS read `architecture/robot_wiring.md` FIRST** before writing hardware code
2. **ALWAYS suggest F5 debug BEFORE terminal commands**
3. **ALWAYS check launch.json for robot name** before BLE terminal commands
4. **ALWAYS mention retry attempts** (BLE discovery often fails first try)
5. **ALWAYS use absolute paths** for file operations

## Dependencies & Integration
- **Core**: `pybricks` (hub runtime) + `pybricksdev` (development tools)
- **No external services**: Self-contained robotics project
- **Hardware dependency**: Requires physical LEGO SPIKE Prime Hub

## Common Gotchas
- Import errors in VS Code are **expected** - code runs on hub's MicroPython, not locally
- Hub must be in pairing mode for Bluetooth connections
- NEVER use USB connection or try to connect to any hub while debugging via Bluetooth always suggest to retry a few times if the robot is not discovered the first time