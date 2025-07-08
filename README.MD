# OBS RGB Reactive Visuals 

This project creates a reactive RGB overlay for OBS (Open Broadcaster Software) using WebSockets and OSC (Open Sound Control). The overlay consists of a grid of hexagonal tiles that change color based on incoming RGB values.

## Features

- Real-time color updates via WebSocket
- OSC support for receiving RGB values
- Hexagonal tile layout for a unique visual effect

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Omnired7/obs_rgb_reactive_visuals.git
   cd obs_rgb_reactive_visuals
   ```

2. Install the required Python packages:
   ```bash
   pip install fastapi uvicorn python-osc
   ```

3. Open `rgb_overlay.html` in a web browser to view the overlay.

## Usage

1. Start the Python server:
   ```bash
   python main.py
   ```

2. Send RGB values to the OSC server (e.g., using an OSC client):
   ```
   /rgb 255 0 0
   ```

3. The WebSocket client in `rgb_overlay.html` will receive the RGB values and update the hex tiles accordingly.

## Customization

- Modify the hex tile colors by changing the CSS in `rgb_overlay.html`.
- Adjust the OSC server settings in `main.py` as needed.

## License

This project is licensed under the MIT License.