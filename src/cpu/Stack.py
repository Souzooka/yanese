from __future__ import annotations

from typing import TYPE_CHECKING

from src.util import byte

if TYPE_CHECKING:
    from src.cpu.registers import Register8Bit
    from src.CPUMemory import CPUMemory


class Stack:
    """
    Abstracted interface for CPU stack operations.
    """

    def __init__(self, memory: CPUMemory, sp: Register8Bit) -> None:
        self.memory = memory
        self.sp = sp

    def __get_address(self) -> int:
        # Stack is on page 1 (0x100-0x1FF)
        return 0x100 | self.sp.get_value()

    def push(self, value: int) -> None:
        # Push the value
        self.memory.write(self.__get_address(), value)
        # And decrement SP
        self.sp.decrement()

    def push16(self, value: int) -> None:
        hi = (value >> 8) & 0xFF
        lo = value & 0xFF
        self.push(hi)
        self.push(lo)

    def pop(self) -> int:
        # Increment SP
        self.sp.increment()
        # Read the value SP now points to
        return self.memory.read(self.__get_address())

    def pop16(self) -> int:
        lo = self.pop()
        hi = self.pop()
        return byte.build_u16(lo, hi)
