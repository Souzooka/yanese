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
    def test_adc_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#ADC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x69] is not None
        assert operations[0x65] is not None
        assert operations[0x75] is not None
        assert operations[0x6D] is not None
        assert operations[0x7D] is not None
        assert operations[0x79] is not None
        assert operations[0x61] is not None
        assert operations[0x71] is not None

        # #Immediate
        operation = operations[0x69]
        compare_params(operation, Interpreter.adc, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0x65]
        compare_params(operation, Interpreter.adc, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0x75]
        compare_params(operation, Interpreter.adc, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0x6D]
        compare_params(operation, Interpreter.adc, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0x7D]
        compare_params(operation, Interpreter.adc, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0x79]
        compare_params(operation, Interpreter.adc, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0x61]
        compare_params(operation, Interpreter.adc, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0x71]
        compare_params(operation, Interpreter.adc, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_adc(self):
        # Should add the accumulator + provided value + carry flag,
        # and update the appropriate flags.

        cpu = new_cpu()
        cpu.a.set_value(0)
        Interpreter.adc(Instruction(cpu, 0))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0xFE)
        Interpreter.adc(Instruction(cpu, 2))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0x2)
        Interpreter.adc(Instruction(cpu, 0xFE))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0x2)
        Interpreter.adc(Instruction(cpu, 2))
        assert cpu.a.get_value() == 4
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0x60)
        Interpreter.adc(Instruction(cpu, 0x20))
        assert cpu.a.get_value() == 0x80
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.v is True
        assert cpu.flags.n is True

        cpu = new_cpu()
        cpu.a.set_value(0x90)
        Interpreter.adc(Instruction(cpu, 0xA0))
        assert cpu.a.get_value() == 0x30
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.v is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(2)
        cpu.flags.c = True
        Interpreter.adc(Instruction(cpu, 0x2))
        assert cpu.a.get_value() == 0x5
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.v is False
        assert cpu.flags.n is False

    def test_and_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#AND
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x29] is not None
        assert operations[0x25] is not None
        assert operations[0x35] is not None
        assert operations[0x2D] is not None
        assert operations[0x3D] is not None
        assert operations[0x39] is not None
        assert operations[0x21] is not None
        assert operations[0x31] is not None

        # #Immediate
        operation = operations[0x29]
        compare_params(operation, Interpreter.and_bitwise, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0x25]
        compare_params(operation, Interpreter.and_bitwise, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0x35]
        compare_params(operation, Interpreter.and_bitwise, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0x2D]
        compare_params(operation, Interpreter.and_bitwise, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0x3D]
        compare_params(operation, Interpreter.and_bitwise, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0x39]
        compare_params(operation, Interpreter.and_bitwise, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0x21]
        compare_params(operation, Interpreter.and_bitwise, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0x31]
        compare_params(operation, Interpreter.and_bitwise, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_and(self):
        # Should bitwise and the accumulator and provided value
        # and update the appropriate flags.

        cpu = new_cpu()
        cpu.a.set_value(0)
        Interpreter.and_bitwise(Instruction(cpu, 0))
        assert cpu.a.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b10001110)
        Interpreter.and_bitwise(Instruction(cpu, 0b00000110))
        assert cpu.a.get_value() == 0b0110
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0b11111101)
        Interpreter.and_bitwise(Instruction(cpu, 0b10101010))
        assert cpu.a.get_value() == 0b10101000
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_asl_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#ASL
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x0A] is not None
        assert operations[0x06] is not None
        assert operations[0x16] is not None
        assert operations[0x0E] is not None
        assert operations[0x1E] is not None

        # Implied
        operation = operations[0x0A]
        compare_params(operation, Interpreter.asl_a, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

        # Zero Page
        operation = operations[0x06]
        compare_params(operation, Interpreter.asl, 5, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        # Zero Page,X
        operation = operations[0x16]
        compare_params(operation, Interpreter.asl, 6, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        # Absolute
        operation = operations[0x0E]
        compare_params(operation, Interpreter.asl, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        # Absolute,X
        operation = operations[0x1E]
        compare_params(operation, Interpreter.asl, 7, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

    def test_asl_a(self):
        # asl_a should shift the accumulator left 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()

        cpu.a.set_value(0b00111100)
        Interpreter.asl_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b01111000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0)
        Interpreter.asl_a(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b10000000)
        Interpreter.asl_a(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b01000000)
        Interpreter.asl_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b10000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_asl(self):
        # asl should shift the value in the memory address left 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()
        address = 4

        cpu.memory.write(address, 0b00111100)
        Interpreter.asl(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b01111000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.memory.write(address, 0)
        Interpreter.asl(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b10000000)
        Interpreter.asl(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b01000000)
        Interpreter.asl(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b10000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_bcc_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BCC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x90] is not None

        # Relative
        operation = operations[0x90]
        compare_params(operation, Interpreter.bcc, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bcc(self):
        # Should branch if the carry flag is clear
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.c = False
        Interpreter.bcc(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.c = True
        Interpreter.bcc(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

    def test_bcs_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BCS
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xB0] is not None

        # Relative
        operation = operations[0xB0]
        compare_params(operation, Interpreter.bcs, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bcs(self):
        # Should branch if the carry flag is set
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.c = False
        Interpreter.bcs(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.c = True
        Interpreter.bcs(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

    def test_beq_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BEQ
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xF0] is not None

        # Relative
        operation = operations[0xF0]
        compare_params(operation, Interpreter.beq, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_beq(self):
        # Should branch if the zero flag is set
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.z = False
        Interpreter.beq(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.z = True
        Interpreter.beq(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

    def test_bit_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BIT
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x24] is not None
        assert operations[0x2C] is not None

        # Zero Page
        operation = operations[0x24]
        compare_params(operation, Interpreter.bit, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0x2C]
        compare_params(operation, Interpreter.bit, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

    def test_bit(self):
        # Should set flags appropriately
        # BIT is a bitwise AND check against memory, in which the z flag is set if the result is 0
        # Flags v,n are set if the bit6,bit7 of memory are set respectively.
        cpu = new_cpu()
        address = 4

        cpu.a.set_value(0b11111111)
        Interpreter.bit(Instruction(cpu, 0))
        assert cpu.flags.z is True
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu.a.set_value(0b00001111)
        Interpreter.bit(Instruction(cpu, 0b00001110))
        assert cpu.flags.z is False
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu.a.set_value(0b0)
        Interpreter.bit(Instruction(cpu, 0b01000000))
        assert cpu.flags.z is True
        assert cpu.flags.v is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b0)
        Interpreter.bit(Instruction(cpu, 0b10000000))
        assert cpu.flags.z is True
        assert cpu.flags.v is False
        assert cpu.flags.n is True

    def test_bmi_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BMI
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x30] is not None

        # Relative
        operation = operations[0x30]
        compare_params(operation, Interpreter.bmi, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bmi(self):
        # Should branch if the negative flag is set
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.n = False
        Interpreter.bmi(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.n = True
        Interpreter.bmi(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

    def test_bne_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BNE
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xD0] is not None

        # Relative
        operation = operations[0xD0]
        compare_params(operation, Interpreter.bne, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bne(self):
        # Should branch if the zero flag is clear
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.z = False
        Interpreter.bne(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.z = True
        Interpreter.bne(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

    def test_bpl_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BPL
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x10] is not None

        # Relative
        operation = operations[0x10]
        compare_params(operation, Interpreter.bpl, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bpl(self):
        # Should branch if the negative flag is clear
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.n = False
        Interpreter.bpl(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.n = True
        Interpreter.bpl(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

    def test_brk_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BRK
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x00] is not None

        # Implied
        operation = operations[0x00]
        compare_params(operation, Interpreter.brk, 7, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_brk(self):
        # Should invoke an interrupt

        cpu = new_cpu()
        _interrupt = cpu.interrupt
        called = False

        def interrupt(*args, **kwargs):
            nonlocal called
            called = True
            _interrupt(*args, **kwargs)

        cpu.interrupt = interrupt

        Interpreter.brk(Instruction(cpu))
        assert called

    def test_bvc_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BVC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x50] is not None

        # Relative
        operation = operations[0x50]
        compare_params(operation, Interpreter.bvc, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bvc(self):
        # Should branch if the overflow flag is clear
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.v = False
        Interpreter.bvc(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.v = True
        Interpreter.bvc(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

    def test_bvs_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#BVS
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x70] is not None

        # Relative
        operation = operations[0x70]
        compare_params(operation, Interpreter.bvs, 2, AddressingMode.RELATIVE, True, ArgumentType.ADDRESS)

    def test_bvc(self):
        # Should branch if the overflow flag is clear
        address = 4

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.v = False
        Interpreter.bvs(Instruction(cpu, address))
        assert cpu.pc.get_value() == 0

        cpu = new_cpu()
        cpu.pc.set_value(0)
        cpu.flags.v = True
        Interpreter.bvs(Instruction(cpu, address))
        assert cpu.pc.get_value() == address

    def test_clc_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CLC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x18] is not None

        operation = operations[0x18]
        compare_params(operation, Interpreter.clc, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_clc(self):
        # Should clear the carry flag.
        cpu = new_cpu()
        cpu.flags.c = True
        Interpreter.clc(Instruction(cpu))
        assert cpu.flags.c is False

    def test_cld_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CLD
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xD8] is not None

        operation = operations[0xD8]
        compare_params(operation, Interpreter.cld, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_cld(self):
        # Should clear the decimal flag.
        cpu = new_cpu()
        cpu.flags.d = True
        Interpreter.cld(Instruction(cpu))
        assert cpu.flags.d is False

    def test_cli_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CLI
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x58] is not None

        operation = operations[0x58]
        compare_params(operation, Interpreter.cli, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_cli(self):
        # Should clear the interrupt disable flag.
        # This effect is delayed by 1 instruction and is handled by calling
        # Interpreter.pre_operation/Interpreter.post_operation around each instruction.
        cpu = new_cpu()
        cpu.flags.i = True

        Interpreter.pre_operation(cpu)
        Interpreter.cli(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Interrupt Disable should still be set at this point
        assert cpu.flags.i is True

        Interpreter.pre_operation(cpu)
        Interpreter.nop(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Now Interrupt Disable should be clear.
        assert cpu.flags.i is False

        # CLI should also flush the delayed clear to the CPU when called, instead of clobbering the delayed change.
        cpu = new_cpu()
        cpu.flags.i = True

        Interpreter.pre_operation(cpu)
        Interpreter.cli(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Interrupt Disable should still be set at this point
        assert cpu.flags.i is True

        Interpreter.pre_operation(cpu)
        Interpreter.cli(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Interrupt Disable should now be clear
        assert cpu.flags.i is False

    def test_clv_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CLV
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xB8] is not None

        operation = operations[0xB8]
        compare_params(operation, Interpreter.clv, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_clv(self):
        # Should clear the overflow flag.
        cpu = new_cpu()
        cpu.flags.v = True
        Interpreter.clv(Instruction(cpu))
        assert cpu.flags.v is False

    def test_cmp_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CMP
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xC9] is not None
        assert operations[0xC5] is not None
        assert operations[0xD5] is not None
        assert operations[0xCD] is not None
        assert operations[0xDD] is not None
        assert operations[0xD9] is not None
        assert operations[0xC1] is not None
        assert operations[0xD1] is not None

        # #Immediate
        operation = operations[0xC9]
        compare_params(operation, Interpreter.cmp, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xC5]
        compare_params(operation, Interpreter.cmp, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0xD5]
        compare_params(operation, Interpreter.cmp, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xCD]
        compare_params(operation, Interpreter.cmp, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0xDD]
        compare_params(operation, Interpreter.cmp, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0xD9]
        compare_params(operation, Interpreter.cmp, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0xC1]
        compare_params(operation, Interpreter.cmp, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0xD1]
        compare_params(operation, Interpreter.cmp, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_cmp(self):
        # Should set appropriate flags

        cpu = new_cpu()
        cpu.a.set_value(0x90)
        Interpreter.cmp(Instruction(cpu, 0x10))
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is True

        cpu.a.set_value(0x90)
        Interpreter.cmp(Instruction(cpu, 0x20))
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0x90)
        Interpreter.cmp(Instruction(cpu, 0x90))
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0x10)
        Interpreter.cmp(Instruction(cpu, 0x90))
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_cpx_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CPX
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xE0] is not None
        assert operations[0xE4] is not None
        assert operations[0xEC] is not None

        # #Immediate
        operation = operations[0xE0]
        compare_params(operation, Interpreter.cpx, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xE4]
        compare_params(operation, Interpreter.cpx, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xEC]
        compare_params(operation, Interpreter.cpx, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

    def test_cpx(self):
        # Should set appropriate flags

        cpu = new_cpu()
        cpu.x.set_value(0x90)
        Interpreter.cpx(Instruction(cpu, 0x10))
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is True

        cpu.x.set_value(0x90)
        Interpreter.cpx(Instruction(cpu, 0x20))
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.x.set_value(0x90)
        Interpreter.cpx(Instruction(cpu, 0x90))
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.x.set_value(0x10)
        Interpreter.cpx(Instruction(cpu, 0x90))
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_cpy(self):
        # Should set appropriate flags

        cpu = new_cpu()
        cpu.y.set_value(0x90)
        Interpreter.cpy(Instruction(cpu, 0x10))
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is True

        cpu.y.set_value(0x90)
        Interpreter.cpy(Instruction(cpu, 0x20))
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.y.set_value(0x90)
        Interpreter.cpy(Instruction(cpu, 0x90))
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.y.set_value(0x10)
        Interpreter.cpy(Instruction(cpu, 0x90))
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_cpy_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#CPY
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xC0] is not None
        assert operations[0xC4] is not None
        assert operations[0xCC] is not None

        # #Immediate
        operation = operations[0xC0]
        compare_params(operation, Interpreter.cpy, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xC4]
        compare_params(operation, Interpreter.cpy, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xCC]
        compare_params(operation, Interpreter.cpy, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

    def test_dec_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#DEC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xC6] is not None
        assert operations[0xD6] is not None
        assert operations[0xCE] is not None
        assert operations[0xDE] is not None

        # Zero Page
        operation = operations[0xC6]
        compare_params(operation, Interpreter.dec, 5, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        # Zero Page,X
        operation = operations[0xD6]
        compare_params(operation, Interpreter.dec, 6, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        # Absolute
        operation = operations[0xCE]
        compare_params(operation, Interpreter.dec, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        # Absolute,X
        operation = operations[0xDE]
        compare_params(operation, Interpreter.dec, 7, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

    def test_dec(self):
        # Should decrement the value at the memory address and update appropriate flags
        cpu = new_cpu()
        address = 4

        cpu.memory.write(address, 2)
        Interpreter.dec(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0x1
        assert cpu.flags.z is False
        assert cpu.flags.n is False
        Interpreter.dec(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0x0
        assert cpu.flags.z is True
        assert cpu.flags.n is False
        Interpreter.dec(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
        Interpreter.dec(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0xFE
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_dex_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#DEX
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xCA] is not None

        # Implied
        operation = operations[0xCA]
        compare_params(operation, Interpreter.dex, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_dex(self):
        # Should decrement X and update appropriate flags
        cpu = new_cpu()

        cpu.x.set_value(2)
        Interpreter.dex(Instruction(cpu))
        assert cpu.x.get_value() == 0x1
        assert cpu.flags.z is False
        assert cpu.flags.n is False
        Interpreter.dex(Instruction(cpu))
        assert cpu.x.get_value() == 0x0
        assert cpu.flags.z is True
        assert cpu.flags.n is False
        Interpreter.dex(Instruction(cpu))
        assert cpu.x.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
        Interpreter.dex(Instruction(cpu))
        assert cpu.x.get_value() == 0xFE
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_dey_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#DEY
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x88] is not None

        # Implied
        operation = operations[0x88]
        compare_params(operation, Interpreter.dey, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_dey(self):
        # Should decrement Y and update appropriate flags
        cpu = new_cpu()

        cpu.y.set_value(2)
        Interpreter.dey(Instruction(cpu))
        assert cpu.y.get_value() == 0x1
        assert cpu.flags.z is False
        assert cpu.flags.n is False
        Interpreter.dey(Instruction(cpu))
        assert cpu.y.get_value() == 0x0
        assert cpu.flags.z is True
        assert cpu.flags.n is False
        Interpreter.dey(Instruction(cpu))
        assert cpu.y.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
        Interpreter.dey(Instruction(cpu))
        assert cpu.y.get_value() == 0xFE
        assert cpu.flags.z is False
        assert cpu.flags.n is True


    def test_eor_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#EOR
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x49] is not None
        assert operations[0x45] is not None
        assert operations[0x55] is not None
        assert operations[0x4D] is not None
        assert operations[0x5D] is not None
        assert operations[0x59] is not None
        assert operations[0x41] is not None
        assert operations[0x51] is not None

        # #Immediate
        operation = operations[0x49]
        compare_params(operation, Interpreter.eor, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0x45]
        compare_params(operation, Interpreter.eor, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0x55]
        compare_params(operation, Interpreter.eor, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0x4D]
        compare_params(operation, Interpreter.eor, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0x5D]
        compare_params(operation, Interpreter.eor, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0x59]
        compare_params(operation, Interpreter.eor, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0x41]
        compare_params(operation, Interpreter.eor, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0x51]
        compare_params(operation, Interpreter.eor, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_eor(self):
        # Should bitwise exlusive-or the accumulator and provided value
        # and update the appropriate flags.

        cpu = new_cpu()
        cpu.a.set_value(0)
        Interpreter.eor(Instruction(cpu, 0))
        assert cpu.a.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b00001110)
        Interpreter.eor(Instruction(cpu, 0b01100000))
        assert cpu.a.get_value() == 0b01101110
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0b11100000)
        Interpreter.eor(Instruction(cpu, 0b01100001))
        assert cpu.a.get_value() == 0b10000001
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_inc_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#INC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xE6] is not None
        assert operations[0xF6] is not None
        assert operations[0xEE] is not None
        assert operations[0xFE] is not None

        # Zero Page
        operation = operations[0xE6]
        compare_params(operation, Interpreter.inc, 5, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        # Zero Page,X
        operation = operations[0xF6]
        compare_params(operation, Interpreter.inc, 6, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        # Absolute
        operation = operations[0xEE]
        compare_params(operation, Interpreter.inc, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        # Absolute,X
        operation = operations[0xFE]
        compare_params(operation, Interpreter.inc, 7, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

    def test_inc(self):
        # Should decrement the value at the memory address and update appropriate flags
        cpu = new_cpu()
        address = 4

        cpu.memory.write(address, 0xFE)
        Interpreter.inc(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
        Interpreter.inc(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0x0
        assert cpu.flags.z is True
        assert cpu.flags.n is False
        Interpreter.inc(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0x1
        assert cpu.flags.z is False
        assert cpu.flags.n is False
        Interpreter.inc(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0x2
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_inx_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#INX
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xE8] is not None

        # Implied
        operation = operations[0xE8]
        compare_params(operation, Interpreter.inx, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_inx(self):
        # Should increment X and update appropriate flags
        cpu = new_cpu()

        cpu.x.set_value(0xFE)
        Interpreter.inx(Instruction(cpu))
        assert cpu.x.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
        Interpreter.inx(Instruction(cpu))
        assert cpu.x.get_value() == 0x0
        assert cpu.flags.z is True
        assert cpu.flags.n is False
        Interpreter.inx(Instruction(cpu))
        assert cpu.x.get_value() == 0x1
        assert cpu.flags.z is False
        assert cpu.flags.n is False
        Interpreter.inx(Instruction(cpu))
        assert cpu.x.get_value() == 0x2
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_iny_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#INY
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xC8] is not None

        # Implied
        operation = operations[0xC8]
        compare_params(operation, Interpreter.iny, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_iny(self):
        # Should increment Y and update appropriate flags
        cpu = new_cpu()

        cpu.y.set_value(0xFE)
        Interpreter.iny(Instruction(cpu))
        assert cpu.y.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
        Interpreter.iny(Instruction(cpu))
        assert cpu.y.get_value() == 0x0
        assert cpu.flags.z is True
        assert cpu.flags.n is False
        Interpreter.iny(Instruction(cpu))
        assert cpu.y.get_value() == 0x1
        assert cpu.flags.z is False
        assert cpu.flags.n is False
        Interpreter.iny(Instruction(cpu))
        assert cpu.y.get_value() == 0x2
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_jmp_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#JMP
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x4C] is not None
        assert operations[0x6C] is not None

        # Absolute
        operation = operations[0x4C]
        compare_params(operation, Interpreter.jmp, 3, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        # (Indirect)
        operation = operations[0x6C]
        compare_params(operation, Interpreter.jmp, 5, AddressingMode.INDIRECT, False, ArgumentType.ADDRESS)

    def test_jmp(self):
        # Should jump to the PC

        cpu = new_cpu()
        cpu.pc.set_value(0)
        Interpreter.jmp(Instruction(cpu, 4))
        assert cpu.pc.get_value() == 4

    def test_jsr_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#JSR
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x20] is not None

        # Absolute
        operation = operations[0x20]
        compare_params(operation, Interpreter.jsr, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

    def test_jsr(self):
        # Should push PC - 1 to stack and jump to argument

        cpu = new_cpu()
        cpu.pc.set_value(0x1234)
        Interpreter.jsr(Instruction(cpu, 0x2000))
        assert cpu.pc.get_value() == 0x2000
        assert cpu.stack.pop16() == 0x1233

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

    def test_lsr_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#LSR
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x4A] is not None
        assert operations[0x46] is not None
        assert operations[0x56] is not None
        assert operations[0x4E] is not None
        assert operations[0x5E] is not None

        operation = operations[0x4A]
        compare_params(operation, Interpreter.lsr_a, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

        operation = operations[0x46]
        compare_params(operation, Interpreter.lsr, 5, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        operation = operations[0x56]
        compare_params(operation, Interpreter.lsr, 6, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        operation = operations[0x4E]
        compare_params(operation, Interpreter.lsr, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        operation = operations[0x5E]
        compare_params(operation, Interpreter.lsr, 7, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

    def test_lsr_a(self):
        # lsr_a should shift the accumulator right 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()

        cpu.a.set_value(0b00111100)
        Interpreter.lsr_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b00011110
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0)
        Interpreter.lsr_a(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b00000001)
        Interpreter.lsr_a(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b10000000)
        Interpreter.lsr_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b01000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_lsr(self):
        # lsr should shift the value in the memory address right 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()
        address = 4

        cpu.memory.write(address, 0b00111100)
        Interpreter.lsr(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b00011110
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.memory.write(address, 0)
        Interpreter.lsr(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b00000001)
        Interpreter.lsr(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b10000000)
        Interpreter.lsr(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b01000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

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

    def test_ora_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#ORA
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x09] is not None
        assert operations[0x05] is not None
        assert operations[0x15] is not None
        assert operations[0x0D] is not None
        assert operations[0x1D] is not None
        assert operations[0x19] is not None
        assert operations[0x01] is not None
        assert operations[0x11] is not None

        # #Immediate
        operation = operations[0x09]
        compare_params(operation, Interpreter.ora, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0x05]
        compare_params(operation, Interpreter.ora, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0x15]
        compare_params(operation, Interpreter.ora, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0x0D]
        compare_params(operation, Interpreter.ora, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0x1D]
        compare_params(operation, Interpreter.ora, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0x19]
        compare_params(operation, Interpreter.ora, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0x01]
        compare_params(operation, Interpreter.ora, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0x11]
        compare_params(operation, Interpreter.ora, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_ora(self):
        # Should bitwise or the accumulator and provided value
        # and update the appropriate flags.

        cpu = new_cpu()
        cpu.a.set_value(0)
        Interpreter.ora(Instruction(cpu, 0))
        assert cpu.a.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b00001110)
        Interpreter.ora(Instruction(cpu, 0b01100000))
        assert cpu.a.get_value() == 0b01101110
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0b11100000)
        Interpreter.ora(Instruction(cpu, 0b11100001))
        assert cpu.a.get_value() == 0b11100001
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_rol_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#ROL
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x2A] is not None
        assert operations[0x26] is not None
        assert operations[0x36] is not None
        assert operations[0x2E] is not None
        assert operations[0x3E] is not None

        operation = operations[0x2A]
        compare_params(operation, Interpreter.rol_a, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

        operation = operations[0x26]
        compare_params(operation, Interpreter.rol, 5, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        operation = operations[0x36]
        compare_params(operation, Interpreter.rol, 6, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        operation = operations[0x2E]
        compare_params(operation, Interpreter.rol, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        operation = operations[0x3E]
        compare_params(operation, Interpreter.rol, 7, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

    def test_rol_a(self):
        # rol_a should rotate the accumulator left 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()

        cpu.a.set_value(0b00111100)
        Interpreter.rol_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b01111000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0)
        Interpreter.rol_a(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b10000000)
        Interpreter.rol_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b00000001
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0b01000000)
        Interpreter.rol_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b10000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_rol(self):
        # rol should rotate the value in the memory address right 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()
        address = 4

        cpu.memory.write(address, 0b00111100)
        Interpreter.rol(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b01111000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.memory.write(address, 0)
        Interpreter.rol(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b10000000)
        Interpreter.rol(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b00000001
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b01000000)
        Interpreter.rol(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b10000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_ror_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#ROR
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x6A] is not None
        assert operations[0x66] is not None
        assert operations[0x76] is not None
        assert operations[0x6E] is not None
        assert operations[0x7E] is not None

        operation = operations[0x6A]
        compare_params(operation, Interpreter.ror_a, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

        operation = operations[0x66]
        compare_params(operation, Interpreter.ror, 5, AddressingMode.ZERO_PAGE, False, ArgumentType.ADDRESS)

        operation = operations[0x76]
        compare_params(operation, Interpreter.ror, 6, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.ADDRESS)

        operation = operations[0x6E]
        compare_params(operation, Interpreter.ror, 6, AddressingMode.ABSOLUTE, False, ArgumentType.ADDRESS)

        operation = operations[0x7E]
        compare_params(operation, Interpreter.ror, 7, AddressingMode.INDEXED_ABSOLUTE_X, False, ArgumentType.ADDRESS)

    def test_ror_a(self):
        # ror_a should rotate the accumulator right 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()

        cpu.a.set_value(0b00111100)
        Interpreter.ror_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b00011110
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.a.set_value(0)
        Interpreter.ror_a(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.a.set_value(0b00000001)
        Interpreter.ror_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b10000000
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is True

        cpu.a.set_value(0b10000000)
        Interpreter.ror_a(Instruction(cpu))
        assert cpu.a.get_value() == 0b01000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_ror(self):
        # ror should rotate the value in the memory address right 1.
        # Flags (c,z,n) should also be set appropriately
        cpu = new_cpu()
        address = 4

        cpu.memory.write(address, 0b00111100)
        Interpreter.ror(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b00011110
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu.memory.write(address, 0)
        Interpreter.ror(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0
        assert cpu.flags.c is False
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu.memory.write(address, 0b00000001)
        Interpreter.ror(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b10000000
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.n is True

        cpu.memory.write(address, 0b10000000)
        Interpreter.ror(Instruction(cpu, address))
        assert cpu.memory.read(address) == 0b01000000
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_rti_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#RTI
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x40] is not None

        operation = operations[0x40]
        compare_params(operation, Interpreter.rti, 6, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_rti(self):
        # Should pull PC and flags from stack.
        # Interrupt flag is changed immediately.
        cpu = new_cpu()
        cpu.stack.push16(0x1234)
        cpu.stack.push(0b11001111)
        Interpreter.rti(Instruction(cpu))
        assert cpu.pc.get_value() == 0x1234
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.i is True
        assert cpu.flags.d is True
        assert cpu.flags.v is True
        assert cpu.flags.n is True

    def test_rts_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#RTS
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x60] is not None

        operation = operations[0x60]
        compare_params(operation, Interpreter.rts, 6, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_rts(self):
        # Should pull PC from stack, and set PC to PC + 1
        cpu = new_cpu()
        cpu.stack.push16(0x1234)
        Interpreter.rts(Instruction(cpu))
        assert cpu.pc.get_value() == 0x1235

    def test_sbc_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#SBC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xE9] is not None
        assert operations[0xE5] is not None
        assert operations[0xF5] is not None
        assert operations[0xED] is not None
        assert operations[0xFD] is not None
        assert operations[0xF9] is not None
        assert operations[0xE1] is not None
        assert operations[0xF1] is not None

        # #Immediate
        operation = operations[0xE9]
        compare_params(operation, Interpreter.sbc, 2, AddressingMode.IMMEDIATE, False, ArgumentType.VALUE)

        # Zero Page
        operation = operations[0xE5]
        compare_params(operation, Interpreter.sbc, 3, AddressingMode.ZERO_PAGE, False, ArgumentType.VALUE)

        # Zero Page,X
        operation = operations[0xF5]
        compare_params(operation, Interpreter.sbc, 4, AddressingMode.INDEXED_ZERO_PAGE_X, False, ArgumentType.VALUE)

        # Absolute
        operation = operations[0xED]
        compare_params(operation, Interpreter.sbc, 4, AddressingMode.ABSOLUTE, False, ArgumentType.VALUE)

        # Absolute,X
        operation = operations[0xFD]
        compare_params(operation, Interpreter.sbc, 4, AddressingMode.INDEXED_ABSOLUTE_X, True, ArgumentType.VALUE)

        # Absolute,Y
        operation = operations[0xF9]
        compare_params(operation, Interpreter.sbc, 4, AddressingMode.INDEXED_ABSOLUTE_Y, True, ArgumentType.VALUE)

        # (Indirect,X)
        operation = operations[0xE1]
        compare_params(operation, Interpreter.sbc, 6, AddressingMode.INDEXED_INDIRECT, False, ArgumentType.VALUE)

        # (Indirect),Y
        operation = operations[0xF1]
        compare_params(operation, Interpreter.sbc, 5, AddressingMode.INDIRECT_INDEXED, True, ArgumentType.VALUE)

    def test_sbc(self):
        # Should do [A] = [A] - [value] - ~carry
        # and update the appropriate flags.

        cpu = new_cpu()
        cpu.a.set_value(0)
        cpu.flags.c = True
        Interpreter.sbc(Instruction(cpu, 0))
        assert cpu.a.get_value() == 0
        assert cpu.flags.c is True
        assert cpu.flags.z is True
        assert cpu.flags.v is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0x2)
        cpu.flags.c = True
        Interpreter.sbc(Instruction(cpu, 3))
        assert cpu.a.get_value() == 0xFF
        assert cpu.flags.c is False
        assert cpu.flags.z is False
        assert cpu.flags.v is True
        assert cpu.flags.n is True

        cpu = new_cpu()
        cpu.a.set_value(0xFF)
        cpu.flags.c = True
        Interpreter.sbc(Instruction(cpu, 0xFE))
        assert cpu.a.get_value() == 1
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.v is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0x4)
        cpu.flags.c = False
        Interpreter.sbc(Instruction(cpu, 0x2))
        assert cpu.a.get_value() == 1
        assert cpu.flags.c is True
        assert cpu.flags.z is False
        assert cpu.flags.v is False
        assert cpu.flags.n is False

    def test_sec_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#SEC
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x38] is not None

        operation = operations[0x38]
        compare_params(operation, Interpreter.sec, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_sec(self):
        # Should set the carry flag.
        cpu = new_cpu()
        Interpreter.sec(Instruction(cpu))
        assert cpu.flags.c is True

    def test_sed_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#SED
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xF8] is not None

        operation = operations[0xF8]
        compare_params(operation, Interpreter.sed, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_sed(self):
        # Should set the decimal flag.
        cpu = new_cpu()
        Interpreter.sed(Instruction(cpu))
        assert cpu.flags.d is True

    def test_sei_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#SEI
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x78] is not None

        operation = operations[0x78]
        compare_params(operation, Interpreter.sei, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_sei(self):
        # Should set the interrupt disable flag.
        # This effect is delayed by 1 instruction and is handled by calling
        # Interpreter.pre_operation/Interpreter.post_operation around each instruction.
        cpu = new_cpu()
        cpu.flags.i = False

        Interpreter.pre_operation(cpu)
        Interpreter.sei(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Interrupt Disable should still be clear at this point
        assert cpu.flags.i is False

        Interpreter.pre_operation(cpu)
        Interpreter.nop(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Now Interrupt Disable should be set.
        assert cpu.flags.i is True

        # SEI should also flush the delayed set to the CPU when called, instead of clobbering the delayed change.
        cpu = new_cpu()
        cpu.flags.i = False

        Interpreter.pre_operation(cpu)
        Interpreter.sei(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Interrupt Disable should still be clear at this point
        assert cpu.flags.i is False

        Interpreter.pre_operation(cpu)
        Interpreter.sei(Instruction(cpu))
        Interpreter.post_operation(cpu)

        # Interrupt Disable should now be set
        assert cpu.flags.i is True

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

    def test_tax_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#TAX
        # Test that the operation entries conform to what is listed on NES DEV
        # https://www.youtube.com/watch?v=gMdcE8jdz70

        assert operations[0xAA] is not None

        operation = operations[0xAA]
        compare_params(operation, Interpreter.tax, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_tax(self):
        # Should transfer A to X (and set appropriate flags based on transferred value)

        cpu = new_cpu()
        cpu.a.set_value(1)
        Interpreter.tax(Instruction(cpu))
        assert cpu.x.get_value() == 1
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0)
        Interpreter.tax(Instruction(cpu))
        assert cpu.x.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0xFF)
        Interpreter.tax(Instruction(cpu))
        assert cpu.x.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_tay_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#TAY
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xA8] is not None

        operation = operations[0xA8]
        compare_params(operation, Interpreter.tay, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_tay(self):
        # Should transfer A to Y (and set appropriate flags based on transferred value)

        cpu = new_cpu()
        cpu.a.set_value(1)
        Interpreter.tay(Instruction(cpu))
        assert cpu.y.get_value() == 1
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0)
        Interpreter.tay(Instruction(cpu))
        assert cpu.y.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.a.set_value(0xFF)
        Interpreter.tay(Instruction(cpu))
        assert cpu.y.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_tsx_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#TSX
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0xBA] is not None

        operation = operations[0xBA]
        compare_params(operation, Interpreter.tsx, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_tsx(self):
        # Should transfer SP to X (and set appropriate flags based on transferred value)

        cpu = new_cpu()
        cpu.sp.set_value(1)
        Interpreter.tsx(Instruction(cpu))
        assert cpu.x.get_value() == 1
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.sp.set_value(0)
        Interpreter.tsx(Instruction(cpu))
        assert cpu.x.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.sp.set_value(0xFF)
        Interpreter.tsx(Instruction(cpu))
        assert cpu.x.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_txa_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#TXA
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x8A] is not None

        operation = operations[0x8A]
        compare_params(operation, Interpreter.txa, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_txa(self):
        # Should transfer X to A (and set appropriate flags based on transferred value)

        cpu = new_cpu()
        cpu.x.set_value(1)
        Interpreter.txa(Instruction(cpu))
        assert cpu.a.get_value() == 1
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.x.set_value(0)
        Interpreter.txa(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.x.set_value(0xFF)
        Interpreter.txa(Instruction(cpu))
        assert cpu.a.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True

    def test_txs_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#TXS
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x9A] is not None

        operation = operations[0x9A]
        compare_params(operation, Interpreter.txs, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_txs(self):
        # Should transfer X to SP (TXS also does NOT set status flags)

        cpu = new_cpu()
        cpu.x.set_value(1)
        Interpreter.txs(Instruction(cpu))
        assert cpu.sp.get_value() == 1
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.x.set_value(0)
        Interpreter.txs(Instruction(cpu))
        assert cpu.sp.get_value() == 0
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.x.set_value(0xFF)
        Interpreter.txs(Instruction(cpu))
        assert cpu.sp.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is False

    def test_tya_params(self):
        # https://www.nesdev.org/wiki/Instruction_reference#TYA
        # Test that the operation entries conform to what is listed on NES DEV

        assert operations[0x98] is not None

        operation = operations[0x98]
        compare_params(operation, Interpreter.tya, 2, AddressingMode.IMPLICIT, False, ArgumentType.NONE)

    def test_tya(self):
        # Should transfer Y to A (and set appropriate flags based on transferred value)

        cpu = new_cpu()
        cpu.y.set_value(1)
        Interpreter.tya(Instruction(cpu))
        assert cpu.a.get_value() == 1
        assert cpu.flags.z is False
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.y.set_value(0)
        Interpreter.tya(Instruction(cpu))
        assert cpu.a.get_value() == 0
        assert cpu.flags.z is True
        assert cpu.flags.n is False

        cpu = new_cpu()
        cpu.y.set_value(0xFF)
        Interpreter.tya(Instruction(cpu))
        assert cpu.a.get_value() == 0xFF
        assert cpu.flags.z is False
        assert cpu.flags.n is True
