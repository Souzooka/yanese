from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cpu.CPU import CPU


class Instruction:
    """
    Represents parameters for each operation to be
    passed into interpreter functions
    """

    # Can extend this later if we wanted to pass the cartridge or whatever
    # (in the event NES2 or (INES+checksum) had any useful info for the interpreter)
    __slots__ = ["cpu", "argument"]

    def __init__(self, cpu: CPU, argument: int = 0) -> None:
        self.cpu = cpu
        self.argument = argument
