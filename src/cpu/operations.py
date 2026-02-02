from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Callable, Dict, List

from src.cpu.addressing import AddressingMode

if TYPE_CHECKING:
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
    def brk(instr: Instruction) -> None:
        pass

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
    Interpreter.lda: ArgumentType.VALUE,
    Interpreter.ldx: ArgumentType.VALUE,
    Interpreter.ldy: ArgumentType.VALUE,
}

# fmt: off
__operations: Dict[int, Operation] = {
    # $00
    # $01
    # $02
    # $03
    # $04
    # $05
    # $06
    # $07
    # $08
    # $09
    # $0A
    # $0B
    # $0C
    # $0D
    # $0E
    # $0F
    # $10
    # $11
    # $12
    # $13
    # $14
    # $15
    # $16
    # $17
    # $18
    # $19
    # $1A
    # $1B
    # $1C
    # $1D
    # $1E
    # $1F
    # $20
    # $21
    # $22
    # $23
    # $24
    # $25
    # $26
    # $27
    # $28
    # $29
    # $2A
    # $2B
    # $2C
    # $2D
    # $2E
    # $2F
    # $30
    # $31
    # $32
    # $33
    # $34
    # $35
    # $36
    # $37
    # $38
    # $39
    # $3A
    # $3B
    # $3C
    # $3D
    # $3E
    # $3F
    # $40
    # $41
    # $42
    # $43
    # $44
    # $45
    # $46
    # $47
    # $48
    # $49
    # $4A
    # $4B
    # $4C
    # $4D
    # $4E
    # $4F
    # $50
    # $51
    # $52
    # $53
    # $54
    # $55
    # $56
    # $57
    # $58
    # $59
    # $5A
    # $5B
    # $5C
    # $5D
    # $5E
    # $5F
    # $60
    # $61
    # $62
    # $63
    # $64
    # $65
    # $66
    # $67
    # $68
    # $69
    # $6A
    # $6B
    # $6C
    # $6D
    # $6E
    # $6F
    # $70
    # $71
    # $72
    # $73
    # $74
    # $75
    # $76
    # $77
    # $78
    # $79
    # $7A
    # $7B
    # $7C
    # $7D
    # $7E
    # $7F
    # $80
    # $81
    # $82
    # $83
    # $84
    # $85
    # $86
    # $87
    # $88
    # $89
    # $8A
    # $8B
    # $8C
    # $8D
    # $8E
    # $8F
    # $90
    # $91
    # $92
    # $93
    # $94
    # $95
    # $96
    # $97
    # $98
    # $99
    # $9A
    # $9B
    # $9C
    # $9D
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
    # $A8
    # $A9 - LDA #Immediate
    0xA9: Operation(
        Interpreter.lda,
        cycles=2,
        addressing_mode=AddressingMode.IMMEDIATE
    ),
    # $AA
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
    # $BA
    # $BB
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
    # $C6
    # $C7
    # $C8
    # $C9
    # $CA
    # $CB
    # $CC
    # $CD
    # $CE
    # $CF
    # $D0
    # $D1
    # $D2
    # $D3
    # $D4
    # $D5
    # $D6
    # $D7
    # $D8
    # $D9
    # $DA
    # $DB
    # $DC
    # $DD
    # $DE
    # $DF
    # $E0
    # $E1
    # $E2
    # $E3
    # $E4
    # $E5
    # $E6
    # $E7
    # $E8
    # $E9
    # $EA
    # $EB
    # $EC
    # $ED
    # $EE
    # $EF
    # $F0
    # $F1
    # $F2
    # $F3
    # $F4
    # $F5
    # $F6
    # $F7
    # $F8
    # $F9
    # $FA
    # $FB
    # $FC
    # $FD
    # $FE
    # $FF
}
# fmt: on

# Now finally convert to a flat list for faster lookup
operations: List[Operation | None] = [__operations.get(i, None) for i in range(0, 0x100)]
del __operations
del _arguments
