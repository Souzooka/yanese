from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

from src.cpu.registers import FlagsRegister, Register8Bit, Register16Bit

if TYPE_CHECKING:
    from src.CPUMemory import CPUMemory


class CPU:
    def __init__(self, memory: CPUMemory) -> None:
        # Memory bus
        self.memory = memory

        # Registers
        # https://www.nesdev.org/wiki/CPU_registers
        self.a = Register8Bit()
        self.x = Register8Bit()
        self.y = Register8Bit()
        self.pc = Register16Bit()
        self.sp = Register8Bit()

        # Status Register
        # https://www.nesdev.org/wiki/Status_flags
        self.flags = FlagsRegister()

        # Cycle counting
        self.cycles = 0
        # "Extra" cycles which occur due to some sort of irregular behavior
        # from an operation (such as indirect accessing accessing an address across
        # a page boundary); applied at the end of the execution of an operation.
        self.extra_cycles = 0

        # TODO: Test coverage
        # CLI/SEI/PLP delay
        # Interpreter handles delayed changing interrupt flag via Interpreter.post_operation
        # CLI/SEI/PLP should also flush this to the interrupt flag as well before overwriting it.
        # (delayed_cycles, flag)
        self.delayed_interrupt_flag: Optional[Tuple[int, bool]] = None
