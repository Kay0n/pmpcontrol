# Platform M+ MIDI Controller

This Python package provides an interface for interacting with the iCON Platform M+ MIDI control surface.


## Features

- Get and set fader positions
- Get and set button light states
- Add and remove event listeners for encoder, fader and button events
- Sync fader positions with user movement, preventing them from dropping


## Installation

To install the package, use pip:

```
pip install pmpcontrol
```

## Example Usage

```python
from controller import PMPController, PMPEvent

# Initialize the controller
controller = PMPController(sync_faders=True)

# Connect to the device
try:
    controller.connect()
    print("Connected to Platform M+")
except OSError as error:
    print(error)

# Define event handler to flash buttons when pressed
def on_button_press(button_number, is_pressed, state):
    controller.set_button(button_number, not state)
    print(f"Button {button_number} {'pressed' if is_pressed else 'released'}")

# Add event listener
controller.add_event_listener(PMPEvent.BUTTON, on_button_press)

# Set a fader position
controller.set_fader(0, 0.5)  # Set fader 0 to 50%

# Keep the script running to handle events
try:
    print("Press Ctrl+C to exit.")
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Disconnect when done
    controller.reset()
    controller.disconnect()
```


## API Reference

### `PMPController`

The main controller class:

- `__init__(sync_faders: bool = False)`: Initialize the controller.
- `connect() -> Tuple[int, int]`: Connect to the Platform M+ device. (Raises `OSError` if Platform M+ device not found)
- `disconnect()`: Disconnect from the device.
- `set_fader(fader_number: int, normalized_position: float)`: Set a fader position.
- `get_fader(fader_number: int) -> float`: Get a fader position.
- `set_button(button_number: int, state: bool)`: Set a button state.
- `get_button(button_number: int) -> bool`: Get a button state.
- `reset()`: Reset all faders and buttons to their default states.
- `set_fader_sync(sync_faders: bool)`: Enable or disable fader syncing.
- `add_event_listener(event_type: PMPEvent, callback: Callable)`: Add an event listener callback.
- `remove_event_listener(event_type: PMPEvent, callback: Callable)`: Remove an event listener callback.



### `PMPEvent`

An enum representing different types of events:

- `FADER`
- `BUTTON`
- `ENCODER`


### Event Listener Callbacks 
- Fader:    `callback(fader_number: int, normalized_value: float)`
- Button:    `callbacks(button_number: int, is_pressed: bool, button_state: bool)`
- Encoder:    `callback(encoder_number: int, value: int)`

The fader callback's `normalized_value` argument is a float between 0 and 1 representing position.<br>
The encoder callback's `value` is a number from 1 to 7 when turned right, and 65 to 71 when turned left, with a higher value representing a faster speed. 
