from __future__ import annotations

from enum import IntEnum, unique
from typing import Any, Dict, Optional

from src.controllers.ControllerBase import ControllerBase


class Controller(ControllerBase):
    """
    Represents a standard NES/Famicom controller.
    In NES2 format, a controller being expected is indicated by a 0 or 1 in byte 15 of the ROM.
    https://www.nesdev.org/wiki/Standard_controller
    """

    @unique
    class Button(IntEnum):
        A = 0
        B = 1
        SELECT = 2
        START = 3
        UP = 4
        DOWN = 5
        LEFT = 6
        RIGHT = 7

    def __init__(self, controller_id: int) -> None:
        self.__id = controller_id

        self.other: Optional[Controller] = None
        """The other paired controller (i.e. controller 1 if this is controller 0, and vice versa)"""

        # The NES controller has 8 button states, just indicating whether the button is down or not.
        # 0 - A
        # 1 - B
        # 2 - Select
        # 3 - Start
        # 4 - Up
        # 5 - Down
        # 6 - Left
        # 7 - Right
        # These buttons are read in order after a write to the controller port;
        # after all buttons are read, official controllers return 1 until another
        # write to the controller port
        # (we simulate this with a psuedo-9th button which is always pressed as a logic optimization)
        self.__buttons = [0] * 8 + [1]

        self.__cursor = 0
        """Indicates which button state will be read from memory (assuming .strobe is False)"""

        self.__strobe = False
        """Set via write to controller port 0 (depending on if bit0 is 0 or 1).
        Also sets strobe value of controller 1 when set.
        If set, reads return the state of the first button (A).
        """

        # Future NOTE/TODO: The second Famicom controller has a pretty cursed microphone

    def on_load(self, other: Controller) -> None:
        # Second initialization in order to receive other controller instance
        self.other = other

    def on_read(self) -> int:
        # If strobe is set, internal shift register is being reset so we just get back A
        if self.__strobe:
            return self.__buttons[0]
        # Otherwise we return back the button indicated by the internal register and increment it
        button = self.__buttons[self.__cursor]
        self.__cursor = min(self.__cursor + 1, len(self.__buttons) - 1)
        return button

    def on_write(self, value: int) -> None:
        # Writing to $4017 (port 1) should do nothing in this case, afaik
        if self.__id == 1:
            return

        strobe = value & 1
        if strobe:
            # Reset both controllers' button indices
            self.__cursor = 0
            self.other.__cursor = 0

        # Set strobe state on both controllers
        self.__strobe = strobe
        self.other.__strobe = strobe

    # Direct button manipulation
    # (used for tests but probably useful for handling inputs from a frontend later too)

    def get_button(self, button_index: Controller.Button | int) -> int:
        return self.__buttons[button_index]

    def set_button(self, button_index: Controller.Button | int, value: int | bool) -> None:
        value = int(bool(value))
        self.__buttons[button_index] = value

    # Save states

    def get_save_state(self) -> Dict[str, Any]:
        # not sure we want buttons here
        return {
            # "buttons": self.__buttons[0:8],
            "cursor": self.__cursor,
            "strobe": int(self.__strobe),
        }

    def set_save_state(self, state: Dict[str, Any]) -> None:
        # elf.__buttons[0:8] = state["buttons"]
        self.__cursor = state["cursor"]
        self.__strobe = bool(state["strobe"])
