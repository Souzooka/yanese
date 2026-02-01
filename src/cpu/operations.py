from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List

from src.cpu.addressing import AddressingMode

if TYPE_CHECKING:
    from src.cpu.Instruction import Instruction

"""
Implementations of each operation in Python
"""


class Interpreter:
    @staticmethod
    def brk(instr: Instruction) -> None:
        pass

    brk.address_argument = False

    @staticmethod
    def lda(instr: Instruction) -> None:
        pass

    lda.address_argument = True


class Operation:
    __slots__ = ["interpreter_function", "cycles", "addressing_mode", "address_argument"]

    def __init__(
        self,
        interpreter_function: Callable[[Instruction], None],
        cycles: int,
        addressing_mode: int,
        page_cross_penalty: bool,
    ) -> None:
        self.interpreter_function = interpreter_function
        self.cycles = cycles
        self.addressing_mode = addressing_mode
        self.page_cross_penalty = page_cross_penalty
        # A bit funky -- might want to look into refactoring this later
        # Whether or not a particular operation accepts an address argument
        # or a value (or none) is the same across the operation, regardless
        # of the addressing mode, so I'm wary of defining it explicitly
        # for each individual opcode in the table below.
        self.address_argument: bool = interpreter_function.address_argument


__operations: Dict[int, Operation] = {}

# Now finally convert to a flat list for faster lookup
operations: List[Operation | None] = [__operations.get(i, None) for i in range(0, 0x100)]
del __operations
