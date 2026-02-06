from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from src.cpu.addressing import addressing_modes
from src.cpu.Instruction import Instruction
from src.cpu.operations import ArgumentType, Interpreter, operations
from src.cpu.registers import FlagsRegister, Register8Bit, Register16Bit
from src.cpu.Stack import Stack
from src.interrupts import Interrupt, interrupts

if TYPE_CHECKING:
    from src.cpu.operations import Operation
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

        # Interface for stack operations
        self.stack = Stack(self.memory, self.sp)

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
        # (delayed_instructions, flag)
        self.delayed_interrupt_flag: Optional[Tuple[int, bool]] = None

        # Represents sources of IRQ requests; if this list is nonempty
        # we should do an IRQ interrupt at the next available opportunity.
        self.__irq_requesters: List[int] = []

    def request_irq(self, source: int) -> None:
        # Sources:
        # 0 - APU DMC Finish
        # 1 = APU Frame Counter
        # 100+ = Reserved for mappers
        if source not in self.__irq_requesters:
            self.__irq_requesters.append(source)

    def clear_irq(self, source: int) -> None:
        if source in self.__irq_requesters:
            del self.__irq_requesters[self.__irq_requesters.index(source)]

    def interrupt(self, interrupt_id: int) -> int:
        """
        Triggers an interrupt. Returns number of CPU cycles executed.
        """
        interrupt = interrupts[interrupt_id]

        # First of all we ignore IRQ if the i flag is set
        if interrupt.id == Interrupt.IRQ and self.flags.i:
            return 0

        # PC, then flags (w/ B flag set depending on type of interrupt) are pushed to stack.
        pc = self.pc.get_value()
        flags = self.flags.to_u8(b_flag=interrupt.b_flag)
        self.stack.push16(pc)
        self.stack.push(flags)

        # Advance 7 cycles
        self.cycles += 7

        # Set the i flag so we don't get interrupted
        self.flags.i = True

        # Then jump to the address at the vector associated with the interrupt
        self.pc.set_value(self.memory.read16(interrupt.vector))

        return 7

    def __fetch_operation(self) -> Operation | None:
        opcode = self.memory.read(self.pc.get_value())
        operation = operations[opcode]
        if operation is None:
            raise RuntimeError(f"Unknown opcode {hex(opcode)}, PC: {hex(self.pc.get_value())}")
        self.pc.increment()
        return operation

    def __fetch_input(self, operation: Operation) -> int:
        size = addressing_modes[operation.addressing_mode].input_size
        value = 0

        match size:
            case 1:
                value = self.memory.read(self.pc.get_value())
                self.pc.increment()
            case 2:
                value = self.memory.read16(self.pc.get_value())
                self.pc.set_value(self.pc.get_value() + 2)

        return value

    def __fetch_argument(self, operation: Operation, op_input: int) -> int:
        mode = addressing_modes[operation.addressing_mode]
        arg_type = operation.argument_type

        if arg_type == ArgumentType.VALUE:
            return mode.get_value(self, op_input, operation.page_cross_penalty)

        return mode.get_address(self, op_input, operation.page_cross_penalty)

    def __add_cycles(self, operation: Operation) -> None:
        cycles = operation.cycles + self.extra_cycles
        self.cycles += cycles
        self.extra_cycles = 0
        return cycles

    def step(self) -> int:
        """
        Executes one instruction. Returns number of cycles executed.
        """
        original_pc = self.pc.get_value()
        operation = self.__fetch_operation()
        op_input = self.__fetch_input(operation)
        argument = self.__fetch_argument(operation, op_input)

        Interpreter.pre_operation(self)
        operation.interpreter_function(Instruction(self, argument))
        Interpreter.post_operation(self)

        cycles = self.__add_cycles(operation)
        return cycles
