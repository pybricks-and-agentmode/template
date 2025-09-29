# Quickly get started with Pybricks

Create a new virtual environment, install the dependencies from `requirements.txt`, and open thefolder in VS Code.

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

## Robot Blink Script

This repository includes a simple MicroPython script for Pybricks hubs:

### `robot_blink.py` - Matrix Animation & GIF Playback
- Prints "Hello World" in the console when the hub program starts.
- Plays animated GIFs on the 5x5 matrix by scaling each frame down and mapping pixel intensity to LED brightness.
- **New:** Ships with an embedded animation so the hub can play a GIF even when no external files are transferred.
- Falls back to the original blinking robot face if no GIF is provided or an error occurs while loading the GIF.

### `.vscode/launch.json` - VS Code Debug Configuration
A sample configuration for debugging Pybricks scripts directly from VS Code using the `pybricksdev` tool.

## How to Run

- F5 to start debugging in VS Code (ensure that you updated the launch.json with your hub name)
- In terminal: ```pybricksdev run ble robot_blink.py -n "John"```
- Or run via USB connection: ```pybricksdev run usb robot_blink.py```

### Expected Behavior
- Console prints "Hello World!" and animation status messages
- LED matrix plays the requested GIF at 5 FPS (one frame every 200 ms)
- LED brightness represents grayscale intensity from the GIF
- If no GIF is found, the LED matrix displays the classic blinking robot face with "Blink!" messages until stopped

### Playing a GIF on the Matrix

1. Place your animated GIF in the project directory (for example `robot_animation.gif`) or reference an existing GIF elsewhere.
2. Launch the script, passing the GIF path as a positional argument or with the `--gif` option:

	```bash
		# Default GIF in the project folder via Bluetooth ("John" is your hub name)
		pybricksdev run ble robot_blink.py -n "John"

		# USB connection
		pybricksdev run usb robot_blink.py
	```

### Choosing Which GIF Plays

`pybricksdev run` does not pass additional command-line arguments to your script. The renderer will therefore look for a GIF in this order:

1. The path specified by the `PYBRICKS_GIF` environment variable.
2. A file named `robot_animation.gif` in the project directory.
3. A file named `giphy-downsized.gif` in the project directory.
4. The first `*.gif` file found in the project directory.
5. **If none of the above exist but the script contains embedded frames, those frames will be used automatically.**

To select a specific file without renaming it, set the environment variable before running the command (PowerShell example):

```pwsh
$env:PYBRICKS_GIF = "C:\\path\\to\\my_animation.gif"
pybricksdev run ble robot_blink.py -n "John"
```

> ℹ️ The environment variable shortcut only applies when the host Python runtime provides the `os` module (e.g., running from your computer). On the hub itself the script simply continues to the default file search.

When the variable is unset, the script will automatically pick the first available GIF or fall back to the blinking robot animation if none are found.

### How GIF decoding works

- When the script runs on your computer (where Pillow is available), it uses Pillow to scale the GIF frames down to the 5×5 matrix.
- When Pillow is **not** available (for example on the hub), the script falls back to a built-in pure MicroPython GIF decoder that supports global/local palettes, transparency, and interlaced frames.
- Debug printouts (prefixed with “Debug”) describe which path is taken and why; they show up in the VS Code debug console or the terminal running `pybricksdev`.

3. To skip GIF playback and use the blink animation explicitly, add `--blink`.
4. To force the internally embedded animation regardless of available files, add `--embedded`.

### Embedding a GIF directly into the script

For Bluetooth transfers, only the Python source reaches the hub. To bake an animation into `robot_blink.py`:

1. Place your source GIF (default: `giphy-downsized.gif`) in the project root.
2. Run `python scripts/generate_embedded_frames.py` from an activated virtual environment.
	 - The script uses the same pure-Python GIF decoder found in `robot_blink.py`, so it has **no Pillow dependency**.
	 - It emits two helper files:
		 - `embedded_frames.json` – raw brightness matrices for inspection.
		 - `embedded_frames_snippet.py` – a ready-to-paste `EMBEDDED_FRAMES_DATA = [...]` literal.
3. Copy the literal from `embedded_frames_snippet.py` into `robot_blink.py` (replacing the existing `EMBEDDED_FRAMES_DATA`).
4. Optionally adjust `EMBEDDED_SOURCE` and `EMBEDDED_FPS` to describe your animation.
5. Deploy the updated `robot_blink.py`—the hub can now render the baked animation with no external assets.

The renderer converts each frame to grayscale, scales it down to 5×5 pixels, and maps brightness to the hub's 0-100 LED intensity range so you can perceive shades on the matrix.

### Compatible Hubs

- LEGO SPIKE Prime Hub
- Not tested on other hubs but should work with minor adjustments

### Note
- Make sure your hub is powered on and connected before running the scripts.
- Check the Pybricks documentation for more information on supported features and limitations.
- When using Bluetooth, the Spike Prime Hub should be blinking blue to indicate it is in pairing mode.

The import errors shown in VS Code are normal - these scripts are designed to run on the MicroPython environment on the Pybricks hub, not in your local Python environment.
