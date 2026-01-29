from __future__ import annotations

from typing import Any, Dict, Optional


class ControllerBase:
    """
    Abstract class meant to represent any particular NES input device
    """

    def __init__(self):
        self.other: Optional[ControllerBase] = None

    def on_load(self, other: ControllerBase) -> None:
        self.other = other

    def on_read(self) -> int:
        pass

    def on_write(self, value: int) -> None:
        pass

    def get_save_state(self) -> Dict[str, Any]:
        return {}

    def set_save_state(self, state: Dict[str, Any]) -> None:
        pass
