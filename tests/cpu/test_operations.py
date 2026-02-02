from __future__ import annotations

from src.cpu.addressing import AddressingMode
from src.cpu.CPU import CPU
from src.cpu.Instruction import Instruction
from src.cpu.operations import ArgumentType, Interpreter, Operation, operations
from src.CPUMemory import CPUMemory


def new_cpu(_class=CPU):
    return _class(CPUMemory())


def compare_params(operation: Operation, fn, cycles, addressing_mode, page_cross_penalty, argument_type):
    assert operation.interpreter_function is fn
    assert operation.cycles == cycles
    assert operation.addressing_mode == addressing_mode
    assert operation.page_cross_penalty is page_cross_penalty
    assert operation.argument_type == argument_type


# fmt: off
class TestOperationsOfficial:
    def test_lda_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#LDA
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xA9] is not None
        assert operations[0xA5] is not None
        assert operations[0xB5] is not None
        assert operations[0xAD] is not None
        assert operations[0xBD] is not None
        assert operations[0xB9] is not None
        assert operations[0xA1] is not None
        assert operations[0xB1] is not None

        # #Immediate
        operation = operations[0xA9]
        compare_params(operation, Interpreter.lda, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xA5]
        compare_params(operation, Interpreter.lda, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0xB5]
        compare_params(operation, Interpreter.lda, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xAD]
        compare_params(operation, Interpreter.lda, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0xBD]
        compare_params(operation, Interpreter.lda, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0xB9]
        compare_params(operation, Interpreter.lda, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0xA1]
        compare_params(operation, Interpreter.lda, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0xB1]
        compare_params(operation, Interpreter.lda, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_lda(self):
        # Should load value to [A]
        cpu = new_cpu()
        Interpreter.lda(Instruction(cpu, 0x77))
        assert cpu.a.get_value() == 0x77
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        # Sets z,n status flags
        Interpreter.lda(Instruction(cpu, 0x00))
        assert cpu.a.get_value() == 0x00
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        Interpreter.lda(Instruction(cpu, 0x80))
        assert cpu.a.get_value() == 0x80
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_ldx_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#LDX
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xA2] is not None
        assert operations[0xA6] is not None
        assert operations[0xB6] is not None
        assert operations[0xAE] is not None
        assert operations[0xBE] is not None

        # #Immediate
        operation = operations[0xA2]
        compare_params(operation, Interpreter.ldx, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xA6]
        compare_params(operation, Interpreter.ldx, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,Y
        operation = operations[0xB6]
        compare_params(operation, Interpreter.ldx, 4, AddressingMode.INDEXED_ZERO_PAGE_Y, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xAE]
        compare_params(operation, Interpreter.ldx, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0xBE]
        compare_params(operation, Interpreter.ldx, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

    def test_ldx(self):
        # Should load value to [X]
        cpu = new_cpu()
        Interpreter.ldx(Instruction(cpu, 0x77))
        assert cpu.x.get_value() == 0x77
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        # Sets z,n status flags
        Interpreter.ldx(Instruction(cpu, 0x00))
        assert cpu.x.get_value() == 0x00
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        Interpreter.ldx(Instruction(cpu, 0x80))
        assert cpu.x.get_value() == 0x80
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_ldy_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#LDY
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xA0] is not None
        assert operations[0xA4] is not None
        assert operations[0xB4] is not None
        assert operations[0xAC] is not None
        assert operations[0xBC] is not None

        # #Immediate
        operation = operations[0xA0]
        compare_params(operation, Interpreter.ldy, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xA4]
        compare_params(operation, Interpreter.ldy, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,Y
        operation = operations[0xB4]
        compare_params(operation, Interpreter.ldy, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xAC]
        compare_params(operation, Interpreter.ldy, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0xBC]
        compare_params(operation, Interpreter.ldy, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

    def test_ldy(self):
        # Should load value to [Y]
        cpu = new_cpu()
        Interpreter.ldy(Instruction(cpu, 0x77))
        assert cpu.y.get_value() == 0x77
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        # Sets z,n status flags
        Interpreter.ldy(Instruction(cpu, 0x00))
        assert cpu.y.get_value() == 0x00
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        Interpreter.ldy(Instruction(cpu, 0x80))
        assert cpu.y.get_value() == 0x80
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_nop_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#NOP
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xEA] is not None

        operation = operations[0xEA]
        compare_params(operation, Interpreter.nop, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_nop(self):
        # Should run and not do anything.
        # You better not be changing state when I'm not looking.
        class CPUWrapper(CPU):
            def __init__(self, memory):
                self._init = False
                super().__init__(memory)
                self._init = True
            def __getattribute__(self, name):
                if name != "_init" and self._init: assert False, "NOP is affecting CPU state"
                return object.__getattribute__(self, name)
            def __setattr__(self, name, value):
                if name != "_init" and self._init: assert False, "NOP is affecting CPU state"
                return object.__setattr__(self, name, value)

        cpu = new_cpu(CPUWrapper)
        Interpreter.nop(Instruction(cpu, 0))

    def test_sta_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#STA
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x85] is not None
        assert operations[0x95] is not None
        assert operations[0x8D] is not None
        assert operations[0x9D] is not None
        assert operations[0x99] is not None
        assert operations[0x81] is not None
        assert operations[0x91] is not None

        # Zero Page
        operation = operations[0x85]
        compare_params(operation, Interpreter.sta, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        # Zero Page,X
        operation = operations[0x95]
        compare_params(operation, Interpreter.sta, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        # Absolute
        operation = operations[0x8D]
        compare_params(operation, Interpreter.sta, 4, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        # Absolute,X
        operation = operations[0x9D]
        compare_params(operation, Interpreter.sta, 5, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

        # Absolute,Y
        operation = operations[0x99]
        compare_params(operation, Interpreter.sta, 5, AddressingMode.INDEXED_ABSOLUTE_Y, False, ArgumentType.ADDRESS)

        # (Indirect,X)
        operation = operations[0x81]
        compare_params(operation, Interpreter.sta, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.ADDRESS)

        # (Indirect),Y
        operation = operations[0x91]
        compare_params(operation, Interpreter.sta, 6, AddressingMode.INDIRECT_INDEXED, False, ArgumentType.ADDRESS)

    def test_sta(self):
        # Should store the value of A to memory
        # (and doesn't affect status flags)
        cpu = new_cpu()

        cpu.a.set_value(0x80)
        Interpreter.sta(Instruction(cpu, 0x320))
        assert cpu.memory.read(0x320) == 0x80
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0x00)
        Interpreter.sta(Instruction(cpu, 0x320))
        assert cpu.memory.read(0x320) == 0x00
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_stx_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#STX
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x86] is not None
        assert operations[0x96] is not None
        assert operations[0x8E] is not None

        # Zero Page
        operation = operations[0x86]
        compare_params(operation, Interpreter.stx, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        # Zero Page,Y
        operation = operations[0x96]
        compare_params(operation, Interpreter.stx, 4, AddressingMode.INDEXED_ZERO_PAGE_Y, False, ArgumentType.ADDRESS)

        # Absolute
        operation = operations[0x8E]
        compare_params(operation, Interpreter.stx, 4, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

    def test_stx(self):
        # Should store the value of X to memory
        # (and doesn't affect status flags)
        cpu = new_cpu()

        cpu.x.set_value(0x80)
        Interpreter.stx(Instruction(cpu, 0x320))
        assert cpu.memory.read(0x320) == 0x80
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.x.set_value(0x00)
        Interpreter.stx(Instruction(cpu, 0x320))
        assert cpu.memory.read(0x320) == 0x00
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_sty_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#STY
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x84] is not None
        assert operations[0x94] is not None
        assert operations[0x8C] is not None

        # Zero Page
        operation = operations[0x84]
        compare_params(operation, Interpreter.sty, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        # Zero Page,X
        operation = operations[0x94]
        compare_params(operation, Interpreter.sty, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        # Absolute
        operation = operations[0x8C]
        compare_params(operation, Interpreter.sty, 4, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

    def test_sty(self):
        # Should store the value of Y to memory
        # (and doesn't affect status flags)
        cpu = new_cpu()

        cpu.y.set_value(0x80)
        Interpreter.sty(Instruction(cpu, 0x320))
        assert cpu.memory.read(0x320) == 0x80
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.y.set_value(0x00)
        Interpreter.sty(Instruction(cpu, 0x320))
        assert cpu.memory.read(0x320) == 0x00
        assert cpu.flags.z is False
        assert cpu.flags.n is False
