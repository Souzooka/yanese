from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Callable, Dict, List

from src.cpu.addressing import AddressingMode
from src.util import byte

if TYPE_CHECKING:
    from src.cpu.CPU import CPU
    from src.cpu.Instruction import Instruction

"""
Implementations of each operation in Python
"""

# Reference for official instructions:
# https://www.nesdev.org/wiki/Instruction_reference


class ArgumentType(IntEnum):
    ADDRESS = 0
    VALUE = 1
    NONE = 2


class Interpreter:
    @staticmethod
    def pre_operation(cpu: CPU) -> None:
        pass

    @staticmethod
    def post_operation(cpu: CPU) -> None:
        Interpreter._handle_delayed_interrupt(cpu)

    @staticmethod
    def _handle_delayed_interrupt(cpu: CPU) -> None:
        if cpu.delayed_interrupt_flag is not None:
            instructions, flag = cpu.delayed_interrupt_flag
            if instructions > 0:
                cpu.delayed_interrupt_flag = (instructions - 1, flag)
            else:
                cpu.flags.i = flag
                cpu.delayed_interrupt_flag = None

    @staticmethod
    def _rmw(cpu: CPU, address: int) -> int:
        """
        Imitates read-modify-write behavior, where the original value is written back to
        the address before the modified value.

        Returns the 8-bit value at the given address.
        """
        value = cpu.memory.read(address)
        cpu.memory.write(address, value)
        return value

    @staticmethod
    def adc(instr: Instruction) -> None:
        """
        ADC - Add with Carry

        ADC adds the carry flag and a memory value to the accumulator.
        See https://www.nesdev.org/wiki/Instruction_reference#ADC which describes flag changes.
        """
        cpu = instr.cpu
        memory = instr.argument
        a = cpu.a.get_value()
        c = int(cpu.flags.c)
        result = a + memory + c
        cpu.a.set_value(byte.to_u8(result))

        # c = result > 0xFF
        # (unsigned overflow occurred)
        cpu.flags.c = result > 0xFF
        # v = (result ^ A) & (result ^ memory) & 0x80
        # (result's sign is different from both original accumulator value and memory's values' sign)
        cpu.flags.v = bool((result ^ a) & (result ^ memory) & 0x80)
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(byte.to_u8(result))

    @staticmethod
    def and_bitwise(instr: Instruction) -> None:
        """
        AND - Bitwise AND

        This ANDs a memory value and the accumulator, bit by bit.
        """
        cpu = instr.cpu
        value = instr.argument
        result = byte.to_u8(cpu.a.get_value() & value)
        cpu.a.set_value(result)
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def _asl(cpu: CPU, value: int) -> None:
        # Result is just the value shifted to the left once
        result = byte.to_u8(value << 1)

        # Set the appropriate status flags
        # c = value bit 7
        cpu.flags.c = bool(value & (1 << 7))
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(result)

        return result

    @staticmethod
    def asl(instr: Instruction) -> None:
        """
        ASL - Arithmetic Shift Left

        ASL shifts all of the bits of a memory value or the accumulator one position to the left,
        moving the value of each bit into the next bit.
        """
        cpu = instr.cpu
        address = instr.argument
        value = Interpreter._rmw(cpu, address)
        result = Interpreter._asl(cpu, value)
        cpu.memory.write(address, result)

    @staticmethod
    def asl_a(instr: Instruction) -> None:
        # Accumulator version of asl
        cpu = instr.cpu
        value = cpu.a.get_value()
        result = Interpreter._asl(cpu, value)
        cpu.a.set_value(result)

    @staticmethod
    def brk(instr: Instruction) -> None:
        pass

    @staticmethod
    def clc(instr: Instruction) -> None:
        """
        CLC - Clear Carry

        CLC clears the carry flag.
        """
        instr.cpu.flags.c = False

    @staticmethod
    def cld(instr: Instruction) -> None:
        """
        CLD - Clear Decimal

        CLD clears the decimal flag.
        """
        instr.cpu.flags.d = False

    @staticmethod
    def cli(instr: Instruction) -> None:
        """
        CLI - Clear Interrupt Disable

        CLI clears the interrupt disable flag.
        This effect is delayed by 1 instruction.
        """
        cpu = instr.cpu
        # Flush previous change on interrupt disable flag
        Interpreter._handle_delayed_interrupt(cpu)
        # Set up a delayed clear of the interrupt flag (after next instruction)
        cpu.delayed_interrupt_flag = (1, False)

    @staticmethod
    def clv(instr: Instruction) -> None:
        """
        CLV - Clear Overflow

        CLV clears the overflow flag.
        """
        instr.cpu.flags.v = False

    @staticmethod
    def dec(instr: Instruction) -> None:
        """
        DEC - Decrement Memory

        DEC subtracts 1 from a memory location.
        """
        cpu = instr.cpu
        address = instr.argument
        value = Interpreter._rmw(cpu, address)
        result = byte.to_u8(value - 1)
        cpu.memory.write(address, result)
        # Also update appropriate flags
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def dex(instr: Instruction) -> None:
        """
        DEX - Decrement X

        DEX subtracts 1 from the X register.
        """
        cpu = instr.cpu
        value = cpu.x.get_value()
        result = byte.to_u8(value - 1)
        cpu.x.set_value(result)
        # Also update appropriate flags
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def dey(instr: Instruction) -> None:
        """
        DEY - Decrement Y

        DEY subtracts 1 from the Y register.
        """
        cpu = instr.cpu
        value = cpu.y.get_value()
        result = byte.to_u8(value - 1)
        cpu.y.set_value(result)
        # Also update appropriate flags
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def inc(instr: Instruction) -> None:
        """
        INC - Increment Memory

        INC adds 1 to a memory location.
        """
        cpu = instr.cpu
        address = instr.argument
        value = Interpreter._rmw(cpu, address)
        result = byte.to_u8(value + 1)
        cpu.memory.write(address, result)
        # Also update appropriate flags
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def inx(instr: Instruction) -> None:
        """
        INX - Increment X

        INX adds 1 to the X register.
        """
        cpu = instr.cpu
        value = cpu.x.get_value()
        result = byte.to_u8(value + 1)
        cpu.x.set_value(result)
        # Also update appropriate flags
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def iny(instr: Instruction) -> None:
        """
        INY - Increment Y

        INY adds 1 to the Y register.
        """
        cpu = instr.cpu
        value = cpu.y.get_value()
        result = byte.to_u8(value + 1)
        cpu.y.set_value(result)
        # Also update appropriate flags
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def lda(instr: Instruction) -> None:
        """
        LDA - Load A

        LDA loads a memory value into the accumulator.
        """
        cpu = instr.cpu
        value = instr.argument

        # Set accumulator
        cpu.a.set_value(value)

        # Update flags of status register
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def ldx(instr: Instruction) -> None:
        """
        LDX - Load X

        LDX loads a memory value into the X register.
        """
        cpu = instr.cpu
        value = instr.argument

        # Set X register
        cpu.x.set_value(value)

        # Update flags of status register
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def ldy(instr: Instruction) -> None:
        """
        LDY - Load Y

        LDY loads a memory value into the Y register.
        """
        cpu = instr.cpu
        value = instr.argument

        # Set Y register
        cpu.y.set_value(value)

        # Update flags of status register
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def _lsr(cpu: CPU, value: int) -> None:
        # Result is just the value shifted to the right once
        result = value >> 1

        # Set the appropriate status flags
        # c = value bit 0
        cpu.flags.c = bool(value & 1)
        # z = result == 0
        # n = 0
        cpu.flags.update_zero_and_negative(result)

        return result

    @staticmethod
    def lsr(instr: Instruction) -> None:
        """
        LSR - Logical Shift Right

        LSR shifts all of the bits of a memory value or the accumulator one position to the right,
        moving the value of each bit into the next bit.
        """
        cpu = instr.cpu
        address = instr.argument
        value = Interpreter._rmw(cpu, address)
        result = Interpreter._lsr(cpu, value)
        cpu.memory.write(address, result)

    @staticmethod
    def lsr_a(instr: Instruction) -> None:
        # Accumulator version of lsr
        cpu = instr.cpu
        value = cpu.a.get_value()
        result = Interpreter._lsr(cpu, value)
        cpu.a.set_value(result)

    @staticmethod
    def nop(instr: Instruction) -> None:
        """
        NOP - No Operation

        NOP - Just burns 2 cycles on the CPU.
              No action necessary here.
        """
        pass

    @staticmethod
    def ora(instr: Instruction) -> None:
        """
        ORA - Bitwise OR

        ORA inclusive-ORs a memory value and the accumulator, bit by bit.
        """
        cpu = instr.cpu
        value = instr.argument
        result = byte.to_u8(cpu.a.get_value() | value)
        cpu.a.set_value(result)
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(result)

    @staticmethod
    def _rol(cpu: CPU, value: int) -> None:
        # Result is just the value rotated to the left once.
        # (e.g. 0b10101000 becomes 0b01010001)
        carry = (value & (1 << 7)) >> 7
        result = byte.to_u8((value << 1) | carry)

        # Set the appropriate status flags
        # c = value bit 7
        cpu.flags.c = bool(carry)
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(result)

        return result

    @staticmethod
    def rol(instr: Instruction) -> None:
        """
        ROL - Rotate Left

        ROL shifts a memory value or the accumulator to the left, moving the value of each bit into the next bit and
        treating the carry flag as though it is both above bit 7 and below bit 0.
        """
        cpu = instr.cpu
        address = instr.argument
        value = Interpreter._rmw(cpu, address)
        result = Interpreter._rol(cpu, value)
        cpu.memory.write(address, result)

    @staticmethod
    def rol_a(instr: Instruction) -> None:
        # Accumulator version of rol
        cpu = instr.cpu
        value = cpu.a.get_value()
        result = Interpreter._rol(cpu, value)
        cpu.a.set_value(result)

    @staticmethod
    def _ror(cpu: CPU, value: int) -> None:
        # Result is just the value rotated to the right once.
        # (e.g. 0b00101001 becomes 0b10010100)
        carry = value & 1
        result = byte.to_u8((value >> 1) | (carry << 7))

        # Set the appropriate status flags
        # c = value bit 0
        cpu.flags.c = bool(carry)
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(result)

        return result

    @staticmethod
    def ror(instr: Instruction) -> None:
        """
        ROR - Rotate Right

        ROR shifts a memory value or the accumulator to the right, moving the value of each bit into the next bit and
        treating the carry flag as though it is both above bit 7 and below bit 0.
        """
        cpu = instr.cpu
        address = instr.argument
        value = Interpreter._rmw(cpu, address)
        result = Interpreter._ror(cpu, value)
        cpu.memory.write(address, result)

    @staticmethod
    def ror_a(instr: Instruction) -> None:
        # Accumulator version of ror
        cpu = instr.cpu
        value = cpu.a.get_value()
        result = Interpreter._ror(cpu, value)
        cpu.a.set_value(result)

    @staticmethod
    def sbc(instr: Instruction) -> None:
        """
        SBC - Subtract with Carry

        ADC adds the carry flag and a memory value to the accumulator.
        SBC subtracts a memory value and the NOT of the carry flag from the accumulator.
        """
        cpu = instr.cpu
        memory = instr.argument
        a = cpu.a.get_value()
        c = int(not cpu.flags.c)
        result = a - memory - c
        cpu.a.set_value(byte.to_u8(result))

        # c = ~(result < $00)
        # (unsigned overflow occurred)
        cpu.flags.c = not result < 0x0
        # v = (result ^ A) & (result ^ memory) & 0x80
        # (result's sign is different from both original accumulator value and memory's values' sign)
        cpu.flags.v = bool((result ^ a) & (result ^ memory) & 0x80)
        # z = result == 0
        # n = result bit 7
        cpu.flags.update_zero_and_negative(byte.to_u8(result))

    @staticmethod
    def sec(instr: Instruction) -> None:
        """
        SEC - Set Carry

        SEC sets the carry flag.
        """
        instr.cpu.flags.c = True

    @staticmethod
    def sed(instr: Instruction) -> None:
        """
        SED - Set Decimal

        SED sets the decimal flag.
        """
        instr.cpu.flags.d = True

    @staticmethod
    def sei(instr: Instruction) -> None:
        """
        SEI - Set Interrupt Disable

        SEI sets the interrupt disable flag.
        This effect is delayed by 1 instruction.
        """
        cpu = instr.cpu
        # Flush previous change on interrupt disable flag
        Interpreter._handle_delayed_interrupt(cpu)
        # Set up a delayed clear of the interrupt flag (after next instruction)
        cpu.delayed_interrupt_flag = (1, True)

    @staticmethod
    def sta(instr: Instruction) -> None:
        """
        STA - Store A

        STA stores the accumulator value into memory.
        """
        cpu = instr.cpu
        address = instr.argument

        # Store A into memory
        cpu.memory.write(address, cpu.a.get_value())

    @staticmethod
    def stx(instr: Instruction) -> None:
        """
        STX - Store X

        STX stores the X register value into memory.
        """
        cpu = instr.cpu
        address = instr.argument

        # Store X into memory
        cpu.memory.write(address, cpu.x.get_value())

    @staticmethod
    def sty(instr: Instruction) -> None:
        """
        STY - Store Y

        STY stores the Y register value into memory.
        """
        cpu = instr.cpu
        address = instr.argument

        # Store Y into memory
        cpu.memory.write(address, cpu.y.get_value())

    @staticmethod
    def tax(instr: Instruction) -> None:
        """
        TAX - Transfer A to X

        TAX copies the accumulator value to the X register.
        """
        cpu = instr.cpu
        value = cpu.a.get_value()
        cpu.x.set_value(value)
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def tay(instr: Instruction) -> None:
        """
        TAX - Transfer A to Y

        TAX copies the accumulator value to the Y register.
        """
        cpu = instr.cpu
        value = cpu.a.get_value()
        cpu.y.set_value(value)
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def tsx(instr: Instruction) -> None:
        """
        TSX - Transfer Stack Pointer to X

        TSX copies the stack pointer value to the X register.
        """
        cpu = instr.cpu
        value = cpu.sp.get_value()
        cpu.x.set_value(value)
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def txa(instr: Instruction) -> None:
        """
        TXA - Transfer X to A

        TXA copies the X register value to the accumulator.
        """
        cpu = instr.cpu
        value = cpu.x.get_value()
        cpu.a.set_value(value)
        cpu.flags.update_zero_and_negative(value)

    @staticmethod
    def txs(instr: Instruction) -> None:
        """
        TXS - Transfer X to Stack Pointer

        TXS copies the X register value to the stack pointer.
        """
        cpu = instr.cpu
        value = cpu.x.get_value()
        cpu.sp.set_value(value)
        # TXS seemingly doesn't update flags.

    @staticmethod
    def tya(instr: Instruction) -> None:
        """
        TYA - Transfer Y to A

        TYA copies the Y register value to the accumulator.
        """
        cpu = instr.cpu
        value = cpu.y.get_value()
        cpu.a.set_value(value)
        cpu.flags.update_zero_and_negative(value)


class Operation:
    __slots__ = ["interpreter_function", "cycles", "addressing_mode", "page_cross_penalty", "argument_type"]

    def __init__(
        self,
        interpreter_function: Callable[[Instruction], None],
        cycles: int,
        addressing_mode: int,
        page_cross_penalty: bool = False,
    ) -> None:
        self.interpreter_function = interpreter_function
        self.cycles = cycles
        self.addressing_mode = addressing_mode
        self.page_cross_penalty = page_cross_penalty
        self.argument_type: ArgumentType = _arguments[interpreter_function]


# All individual instruction types should accept the same argument type,
# regardless of addressing mode
_arguments = {
    Interpreter.and_bitwise: ArgumentType.VALUE,
    Interpreter.adc: ArgumentType.VALUE,
    Interpreter.asl: ArgumentType.ADDRESS,
    Interpreter.asl_a: ArgumentType.NONE,
    Interpreter.clc: ArgumentType.NONE,
    Interpreter.cld: ArgumentType.NONE,
    Interpreter.cli: ArgumentType.NONE,
    Interpreter.clv: ArgumentType.NONE,
    Interpreter.dec: ArgumentType.ADDRESS,
    Interpreter.dex: ArgumentType.NONE,
    Interpreter.dey: ArgumentType.NONE,
    Interpreter.inc: ArgumentType.ADDRESS,
    Interpreter.inx: ArgumentType.NONE,
    Interpreter.iny: ArgumentType.NONE,
    Interpreter.lda: ArgumentType.VALUE,
    Interpreter.ldx: ArgumentType.VALUE,
    Interpreter.ldy: ArgumentType.VALUE,
    Interpreter.lsr: ArgumentType.ADDRESS,
    Interpreter.lsr_a: ArgumentType.NONE,
    Interpreter.nop: ArgumentType.NONE,
    Interpreter.ora: ArgumentType.VALUE,
    Interpreter.rol: ArgumentType.ADDRESS,
    Interpreter.rol_a: ArgumentType.NONE,
    Interpreter.ror: ArgumentType.ADDRESS,
    Interpreter.ror_a: ArgumentType.NONE,
    Interpreter.sbc: ArgumentType.VALUE,
    Interpreter.sec: ArgumentType.NONE,
    Interpreter.sed: ArgumentType.NONE,
    Interpreter.sei: ArgumentType.NONE,
    Interpreter.sta: ArgumentType.ADDRESS,
    Interpreter.stx: ArgumentType.ADDRESS,
    Interpreter.sty: ArgumentType.ADDRESS,
    Interpreter.tax: ArgumentType.NONE,
    Interpreter.tay: ArgumentType.NONE,
    Interpreter.tsx: ArgumentType.NONE,
    Interpreter.txa: ArgumentType.NONE,
    Interpreter.txs: ArgumentType.NONE,
    Interpreter.tya: ArgumentType.NONE,
}

# fmt: off
__operations: Dict[int, Operation] = {
    # $00
    # $01 - ORA (Indirect,X)
    0x01: Operation(
        Interpreter.ora,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_INDIRECT
    ),
    # $02
    # $03
    # $04
    # $05 - ORA Zero Page
    0x05: Operation(
        Interpreter.ora,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $06 - ASL Zero Page
    0x06: Operation(
        Interpreter.asl,
        cycles=5,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $07
    # $08
    # $09 - ORA #Immediate
    0x09: Operation(
        Interpreter.ora,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $0A - ASL Accumulator
    0x0A: Operation(
        Interpreter.asl_a,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $0B
    # $0C
    # $0D - ORA Absolute
    0x0D: Operation(
        Interpreter.ora,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $0E - ASL Absolute
    0x0E: Operation(
        Interpreter.asl,
        cycles=6,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $0F
    # $10
    # $11 - ORA (Indirect),Y
    0x11: Operation(
        Interpreter.ora,
        cycles=5,
        addressing_mode=AddressingMode.INDIRECT_INDEXED,
        page_cross_penalty=True
    ),
    # $12
    # $13
    # $14
    # $15 - ORA Zero Page,X
    0x15: Operation(
        Interpreter.ora,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $16 - ASL Zero Page,X
    0x16: Operation(
        Interpreter.asl,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $17
    # $18 - CLC Implied
    0x18: Operation(
        Interpreter.clc,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $19 - ORA Absolute,Y
    0x19: Operation(
        Interpreter.ora,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y,
        page_cross_penalty=True
    ),
    # $1A
    # $1B
    # $1C
    # $1D - ORA Absolute,X
    0x1D: Operation(
        Interpreter.ora,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X,
        page_cross_penalty=True
    ),
    # $1E
    0x1E: Operation(
        Interpreter.asl,
        cycles=7,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $1F
    # $20
    # $21 - AND (Indirect,X)
    0x21: Operation(
        Interpreter.and_bitwise,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_INDIRECT
    ),
    # $22
    # $23
    # $24
    # $25 - AND Zero Page
    0x25: Operation(
        Interpreter.and_bitwise,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $26 - ROL Zero Page
    0x26: Operation(
        Interpreter.rol,
        cycles=5,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $27
    # $28
    # $29 - AND #Immediate
    0x29: Operation(
        Interpreter.and_bitwise,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $2A - ROL Accumulator
    0x2A: Operation(
        Interpreter.rol_a,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $2B
    # $2C
    # $2D - AND Absolute
    0x2D: Operation(
        Interpreter.and_bitwise,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $2E - ROL Absolute
    0x2E: Operation(
        Interpreter.rol,
        cycles=6,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $2F
    # $30
    # $31 - AND (Indirect),Y
    0x31: Operation(
        Interpreter.and_bitwise,
        cycles=5,
        addressing_mode=AddressingMode.INDIRECT_INDEXED,
        page_cross_penalty=True
    ),
    # $32
    # $33
    # $34
    # $35 - AND Zero Page,X
    0x35: Operation(
        Interpreter.and_bitwise,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $36 - ROL Zero Page,X
    0x36: Operation(
        Interpreter.rol,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $37
    # $38 - SEC Implied
    0x38: Operation(
        Interpreter.sec,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $39 - AND Absolute,Y
    0x39: Operation(
        Interpreter.and_bitwise,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y,
        page_cross_penalty=True
    ),
    # $3A
    # $3B
    # $3C
    # $3D - AND Absolute,X
    0x3D: Operation(
        Interpreter.and_bitwise,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X,
        page_cross_penalty=True
    ),
    # $3E - ROL Absolute,X
    0x3E: Operation(
        Interpreter.rol,
        cycles=7,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $3F
    # $40
    # $41
    # $42
    # $43
    # $44
    # $45
    # $46 - LSR Zero Page
    0x46: Operation(
        Interpreter.lsr,
        cycles=5,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $47
    # $48
    # $49
    # $4A - LSR Logical Shift Right
    0x4A: Operation(
        Interpreter.lsr_a,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $4B
    # $4C
    # $4D
    # $4E - LSR Absolute
    0x4E: Operation(
        Interpreter.lsr,
        cycles=6,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $4F
    # $50
    # $51
    # $52
    # $53
    # $54
    # $55
    # $56 - LSR Zero Page,X
    0x56: Operation(
        Interpreter.lsr,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $57
    # $58 - CLI Implied
    0x58: Operation(
        Interpreter.cli,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $59
    # $5A
    # $5B
    # $5C
    # $5D
    # $5E - LSR Absolute,X
    0x5E: Operation(
        Interpreter.lsr,
        cycles=7,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $5F
    # $60
    # $61 - ADC (Indirect,X)
    0x61: Operation(
        Interpreter.adc,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_INDIRECT
    ),
    # $62
    # $63
    # $64
    # $65 - ADC Zero Page
    0x65: Operation(
        Interpreter.adc,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $66 - ROR Zero Page
    0x66: Operation(
        Interpreter.ror,
        cycles=5,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $67
    # $68
    # $69 - ADC #Immediate
    0x69: Operation(
        Interpreter.adc,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $6A - ROR Accumulator
    0x6A: Operation(
        Interpreter.ror_a,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $6B
    # $6C
    # $6D - ADC Absolute
    0x6D: Operation(
        Interpreter.adc,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $6E - ROR Absolute
    0x6E: Operation(
        Interpreter.ror,
        cycles=6,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $6F
    # $70
    # $71 - ADC (Indirect),Y
    0x71: Operation(
        Interpreter.adc,
        cycles=5,
        addressing_mode=AddressingMode.INDIRECT_INDEXED,
        page_cross_penalty=True
    ),
    # $72
    # $73
    # $74
    # $75 - ADC Zero Page,X
    0x75: Operation(
        Interpreter.adc,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $76 - ROR Zero Page,X
    0x76: Operation(
        Interpreter.ror,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $77
    # $78 - SEI Implied
    0x78: Operation(
        Interpreter.sei,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $79 - ADC Absolute,Y
    0x79: Operation(
        Interpreter.adc,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y,
        page_cross_penalty=True
    ),
    # $7A
    # $7B
    # $7C
    # $7D - ADC Absolute,X
    0x7D: Operation(
        Interpreter.adc,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X,
        page_cross_penalty=True
    ),
    # $7E - ROR Absolute,X
    0x7E: Operation(
        Interpreter.ror,
        cycles=7,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $7F
    # $80
    # $81 - STA (Indirect,X)
    0x81: Operation(
        Interpreter.sta,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_INDIRECT
    ),
    # $82
    # $83
    # $84 - STY Zero Page
    0x84: Operation(
        Interpreter.sty,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $85 - STA Zero Page
    0x85: Operation(
        Interpreter.sta,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $86 - STX Zero Page
    0x86: Operation(
        Interpreter.stx,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $87
    # $88 - DEY Implied
    0x88: Operation(
        Interpreter.dey,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $89
    # $8A - TXA Implied
    0x8A: Operation(
        Interpreter.txa,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $8B
    # $8C - STY Absolute
    0x8C: Operation(
        Interpreter.sty,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $8D - STA Absolute
    0x8D: Operation(
        Interpreter.sta,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $8E
    0x8E: Operation(
        Interpreter.stx,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $8F
    # $90
    # $91 - STA (Indirect),Y
    0x91: Operation(
        Interpreter.sta,
        cycles=6,
        addressing_mode=AddressingMode.INDIRECT_INDEXED
    ),
    # $92
    # $93
    # $94 - STY Zero Page,X
    0x94: Operation(
        Interpreter.sty,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $95 - STA Zero Page,X
    0x95: Operation(
        Interpreter.sta,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $96 - STX Zero Page,Y
    0x96: Operation(
        Interpreter.stx,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_Y
    ),
    # $97
    # $98 - TYA Implied
    0x98: Operation(
        Interpreter.tya,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $99 - STA Absolute,Y
    0x99: Operation(
        Interpreter.sta,
        cycles=5,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y
    ),
    # $9A - TXS Implied
    0x9A: Operation(
        Interpreter.txs,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $9B
    # $9C
    # $9D - STA Absolute,X
    0x9D: Operation(
        Interpreter.sta,
        cycles=5,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $9E
    # $9F
    # $A0 - LDY #Immediate
    0xA0: Operation(
        Interpreter.ldy,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $A1 - LDA (Indirect,X)
    0xA1: Operation(
        Interpreter.lda,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_INDIRECT
    ),
    # $A2 - LDX #Immediate
    0xA2: Operation(
        Interpreter.ldx,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $A3
    # $A4 - LDY Zero Page
    0xA4: Operation(
        Interpreter.ldy,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $A5 - LDA Zero Page
    0xA5: Operation(
        Interpreter.lda,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $A6 - LDX Zero Page
    0xA6: Operation(
        Interpreter.ldx,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $A7
    # $A8 - TAY Implied
    0xA8: Operation(
        Interpreter.tay,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $A9 - LDA #Immediate
    0xA9: Operation(
        Interpreter.lda,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $AA - TAX Implied
    0xAA: Operation(
        Interpreter.tax,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $AB
    # $AC - LDY Absolute
    0xAC: Operation(
        Interpreter.ldy,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $AD - LDA Absolute
    0xAD: Operation(
        Interpreter.lda,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $AE - LDX Absolute
    0xAE: Operation(
        Interpreter.ldx,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $AF
    # $B0
    # $B1 - LDA (Indirect),Y
    0xB1: Operation(
        Interpreter.lda,
        cycles=5,
        addressing_mode=AddressingMode.INDIRECT_INDEXED,
        page_cross_penalty=True
    ),
    # $B2
    # $B3
    # $B4 - LDY Zero Page,X
    0xB4: Operation(
        Interpreter.ldy,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $B5 - LDA Zero Page,X
    0xB5: Operation(
        Interpreter.lda,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $B6 - LDX Zero Page,Y
    0xB6: Operation(
        Interpreter.ldx,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_Y
    ),
    # $B7
    # $B8
    # $B9 - LDA Absolute,Y
    0xB9: Operation(
        Interpreter.lda,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y,
        page_cross_penalty=True
    ),
    # $BA - TSX Implied
    0xBA: Operation(
        Interpreter.tsx,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $BB - CLV Implied
    0xB8: Operation(
        Interpreter.clv,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $BC - LDY Absolute,X
    0xBC: Operation(
        Interpreter.ldy,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X,
        page_cross_penalty=True
    ),
    # $BD - LDA Absolute,X
    0xBD: Operation(
        Interpreter.lda,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X,
        page_cross_penalty=True
    ),
    # $BE - LDX Absolute,Y
    0xBE: Operation(
        Interpreter.ldx,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y,
        page_cross_penalty=True
    ),
    # $BF
    # $C0
    # $C1
    # $C2
    # $C3
    # $C4
    # $C5
    # $C6 - DEC Zero Page
    0xC6: Operation(
        Interpreter.dec,
        cycles=5,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $C7
    # $C8 - INY Implied
    0xC8: Operation(
        Interpreter.iny,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $C9
    # $CA - DEX Implied
    0xCA: Operation(
        Interpreter.dex,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $CB
    # $CC
    # $CD
    # $CE - DEC Absolute
    0xCE: Operation(
        Interpreter.dec,
        cycles=6,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $CF
    # $D0
    # $D1
    # $D2
    # $D3
    # $D4
    # $D5
    # $D6 - DEC Zero Page,X
    0xD6: Operation(
        Interpreter.dec,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $D7
    # $D8 - CLD Implied
    0xD8: Operation(
        Interpreter.cld,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $D9
    # $DA
    # $DB
    # $DC
    # $DD
    # $DE - DEC Absolute,X
    0xDE: Operation(
        Interpreter.dec,
        cycles=7,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $DF
    # $E0
    # $E1 - SBC (Indirect,X)
    0xE1: Operation(
        Interpreter.sbc,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_INDIRECT
    ),
    # $E2
    # $E3
    # $E4
    # $E5 - SBC Zero Page
    0xE5: Operation(
        Interpreter.sbc,
        cycles=3,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $E6 - INC Zero Page
    0xE6: Operation(
        Interpreter.inc,
        cycles=5,
        addressing_mode=AddressingMode.ZERO_PAGE
    ),
    # $E7
    # $E8 - INX Implied
    0xE8: Operation(
        Interpreter.inx,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $E9 - SBC #Immediate
    0xE9: Operation(
        Interpreter.sbc,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $EA - NOP
    0xEA: Operation(
        Interpreter.nop,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $EB
    # $EC
    # $ED - SBC Absolute
    0xED: Operation(
        Interpreter.sbc,
        cycles=4,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $EE - INC Absolute
    0xEE: Operation(
        Interpreter.inc,
        cycles=6,
        addressing_mode=AddressingMode.ABSOLUTE
    ),
    # $EF
    # $F0
    # $F1 - SBC (Indirect),Y
    0xF1: Operation(
        Interpreter.sbc,
        cycles=5,
        addressing_mode=AddressingMode.INDIRECT_INDEXED,
        page_cross_penalty=True
    ),
    # $F2
    # $F3
    # $F4
    # $F5 - SBC Zero Page,X
    0xF5: Operation(
        Interpreter.sbc,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $F6 - INC Zero Page,X
    0xF6: Operation(
        Interpreter.inc,
        cycles=6,
        addressing_mode=AddressingMode.INDEXED_ZERO_PAGE_X
    ),
    # $F7
    # $F8 - SED Implied
    0xF8: Operation(
        Interpreter.sed,
        cycles=2,
        addressing_mode=AddressingMode.IMPLICIT
    ),
    # $F9 - SBC Absolute,Y
    0xF9: Operation(
        Interpreter.sbc,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_Y,
        page_cross_penalty=True
    ),
    # $FA
    # $FB
    # $FC
    # $FD - SBC Absolute,X
    0xFD: Operation(
        Interpreter.sbc,
        cycles=4,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X,
        page_cross_penalty=True
    ),
    # $FE - INC Absolute,X
    0xFE: Operation(
        Interpreter.inc,
        cycles=7,
        addressing_mode=AddressingMode.INDEXED_ABSOLUTE_X
    ),
    # $FF
}
# fmt: on

# Now finally convert to a flat list for faster lookup
operations: List[Operation | None] = [__operations.get(i, None) for i in range(0, 0x100)]
del __operations
del _arguments
