import rtmidi
from typing import Callable, Dict, List, Tuple
from enum import Enum, auto

PORT_NAME = "Platform M+"
NOTE_ON = 0x90
CONTROL_CHANGE = 0xB0
PITCH_BEND = 0xE0
VELOCITY_ON = 127
VELOCITY_OFF = 0
MAX_7BIT = 0x7F
MAX_14BIT = 16383

class PMPEvent(Enum):
    """
    Enum representing different Platform M+ event types.
    """
    FADER = auto()
    BUTTON = auto()
    ENCODER = auto()

class PMPController:
    """
    A class to interact with the Icon Platform M+ MIDI control surface.
    """

    def __init__(self, sync_faders: bool = False):
        """
        Initialize the Platform M+ Controller.

        Args:
            `sync_faders (bool, optional)`: Whether the fader positions should sync with user movement. Defaults to False.
        """
        self.sync_faders = sync_faders
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.fader_positions = [0] * 9
        self.button_states = {}
        self.event_callbacks: Dict[PMPEvent, List[Callable]] = {
            PMPEvent.FADER: [],
            PMPEvent.BUTTON: [],
            PMPEvent.ENCODER: []
        }

    def connect(self) -> Tuple[int, int]:
        """
        Connect to the Platform M+ MIDI device.

        Returns:
            `in_port, out_port (Tuple[int, int])`: A tuple containing the input and output port numbers.

        Raises:
            `OSError`: If the Platform M+ device is not found.
        """
        in_port = self.find_port(self.midi_in)
        out_port = self.find_port(self.midi_out)
        if in_port is None or out_port is None:
            raise OSError("Platform M+ not found. Make sure it's connected and recognized by your system.")
        self.midi_in.open_port(in_port)
        self.midi_out.open_port(out_port)
        self.midi_in.set_callback(self.process_midi_message)
        return (in_port, out_port)

    def find_port(self, midi_obj) -> int:
        for i, port in enumerate(midi_obj.get_ports()):
            if PORT_NAME in port:
                return i
        return None

    def process_midi_message(self, message, timestanp):
        midi_message, _ = message
        if len(midi_message) != 3:
            return
        status_byte, data1, data2 = midi_message
        if PITCH_BEND <= status_byte <= PITCH_BEND + 8:
            fader_number = status_byte - PITCH_BEND
            value = (data2 << 7) | data1
            self.handle_fader(fader_number, value)
        elif status_byte == NOTE_ON:
            self.handle_button(data1, data2 > 0)
        elif status_byte == CONTROL_CHANGE:
            self.handle_encoder(data1, data2)

    def handle_fader(self, fader_number: int, value: int):
        if 0 <= fader_number < 9:
            normalized_value = value / MAX_14BIT
            if self.sync_faders:
                self.set_fader(fader_number, normalized_value)
            for callback in self.event_callbacks[PMPEvent.FADER]:
                callback(fader_number, normalized_value)

    def handle_button(self, button_number: int, is_pressed: bool):
        button_state = self.button_states.get(button_number, False)
        for callback in self.event_callbacks[PMPEvent.BUTTON]:
            callback(button_number, is_pressed, button_state)

    def handle_encoder(self, encoder_number: int, value: int):
        for callback in self.event_callbacks[PMPEvent.ENCODER]:
            callback(encoder_number, value)

    def set_fader(self, fader_number: int, normalized_position: float):
        """
        Set the position of a fader.

        Args:
            `fader_number (int)`: The number of the fader (0-8).
            `normalized_position (float)`: The position of the fader, between 0 and 1.
        """
        if 0 <= fader_number < 9:
            value = int(normalized_position * MAX_14BIT)
            msb = (value >> 7) & MAX_7BIT
            lsb = value & MAX_7BIT
            self.midi_out.send_message([PITCH_BEND + fader_number, lsb, msb])
            self.fader_positions[fader_number] = normalized_position

    def set_button(self, button_number: int, button_state: bool):
        """
        Set the state of a button.

        Args:
            `button_number (int)`: The number of the button.
            `button_state (bool)`: The state to set the button to (True for on, False for off).
        """
        self.button_states[button_number] = button_state
        velocity = VELOCITY_ON if button_state else VELOCITY_OFF
        self.midi_out.send_message([NOTE_ON, button_number, velocity])

    def set_fader_sync(self, sync_faders: bool):
        """
        Set whether faders should sync with user movement.

        Args:
            `sync_faders (bool)`: True to enable syncing, False to disable.
        """
        self.sync_faders = sync_faders

    def get_fader(self, fader_number: int) -> float:
        """
        Get the current position of a fader.

        Args:
            `fader_number (int)`: The number of the fader (0-8).

        Returns:
            `fader_position (float)`: The current position of the fader, between 0 and 1.
        """
        return self.fader_positions[fader_number]

    def get_button(self, button_number: int) -> bool:
        """
        Get the current state of a button.

        Args:
            `button_number (int)`: The number of the button.

        Returns:
            `button_state (bool)`: The current state of the button (True for on, False for off).
        """
        button_state = self.button_states.get(button_number, False)
        self.button_states[button_number] = button_state
        return button_state

    def reset(self):
        """
        Reset all faders to 0 and all buttons to off.
        """
        for i in range(0, 9):
            self.set_fader(i, 0)
        for i in range(0, 100):
            self.set_button(i, False)

    def add_event_listener(self, event_type: PMPEvent, callback: Callable):
        """
        Add an event listener for a specific event type.

        Args:
            `event_type (PMPEvent)`: The type of event to listen for.
            `callback (Callable)`: The function to call when the event occurs.

        Callback Signatures:
            - Fader:    `callback(fader_number: int, normalized_value: float)`
            - Button:    `callbacks(button_number: int, is_pressed: bool, button_state: bool)`
            - Encoder:    `callback(encoder_number: int, value: int)`
        """
        self.event_callbacks[event_type].append(callback)

    def remove_event_listener(self, event_type: PMPEvent, callback: Callable):
        """
        Remove an event listener for a specific event type.

        Args:
            `event_type (PMPEvent)`: The type of event the listener was registered for.
            `callback (Callable)`: The function to remove from the event listeners.
        """
        self.event_callbacks[event_type].remove(callback)

    def disconnect(self):
        """
        Disconnect from the Platform M+ device and close MIDI ports.
        """
        self.midi_in.cancel_callback()
        self.midi_in.close_port()
        self.midi_out.close_port()

__all__ = ['PMPEvent', 'PMPController']