from src.cpu.addressing import AddressingMode, UnsupportedAddressing, addressing_modes
from src.cpu.CPU import CPU
from src.CPUMemory import CPUMemory


def is_unsupported(fn, *args):
    # Test case for unsupported addressing functions
    # Implementation might change later but they raise UnsupportedAddressing right now
    test_pass = False
    try:
        fn(*args)
    except UnsupportedAddressing:
        test_pass = True
    return test_pass


class TestAddressing:
    def test_implicit(self):
        mode = addressing_modes[AddressingMode.IMPLICIT]

        # Should have an input size of 0, of course
        assert mode.input_size == 0

        # Since implicit operations have no argument, we'll just check that there's
        # a callable for implicit operations (and we don't particularly care about return value)
        get_address = mode.get_address
        get_value = mode.get_value

        assert callable(get_address)
        assert callable(get_value)

    def test_immediate(self):
        mode = addressing_modes[AddressingMode.IMMEDIATE]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # Address not supported
        assert is_unsupported(mode.get_address, cpu, 0, False)

        # No transformation needs to be done on immediate values, the CPU fetches the input and the
        # input gets spat back out as is.
        for i in range(0x100):
            assert mode.get_value(cpu, i, False) == i

    def test_absolute(self):
        mode = addressing_modes[AddressingMode.ABSOLUTE]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 2
        assert mode.input_size == 2

        # Address is just returned without transformation
        assert mode.get_address(cpu, 0, False) == 0
        assert mode.get_address(cpu, 0x1000, False) == 0x1000
        assert mode.get_address(cpu, 0x1234, False) == 0x1234
        assert mode.get_address(cpu, 0xFFFF, False) == 0xFFFF

        # Value returns the 8-bit value at the given memory address
        memory.write(0x40, 0xFE)
        assert mode.get_value(cpu, 0x40, False) == 0xFE
        memory.write(0x7FF, 0x2)
        assert mode.get_value(cpu, 0x7FF, False) == 0x2

    def test_zero_page(self):
        mode = addressing_modes[AddressingMode.ZERO_PAGE]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # Basically just absolute, but for the zero page only.
        # Should return address without transformation.
        for i in range(0x100):
            assert mode.get_address(cpu, i, False) == i

        # Value returns the 8-bit value at the given memory address.
        for i in range(0x100):
            memory.write(i, 0xFF - i)
        for i in range(0x100):
            assert mode.get_value(cpu, i, False) == 0xFF - i

    def test_relative(self):
        mode = addressing_modes[AddressingMode.RELATIVE]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # Address is relative to CPU's PC register
        # Zero/Positive offset (no page crossing)
        cpu.pc.set_value(0x3080)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 0, True) == 0x3080
        assert cpu.extra_cycles == 0
        assert mode.get_address(cpu, 0x7F, True) == 0x30FF
        assert cpu.extra_cycles == 0
        # Negative offset (no page crossing)
        cpu.pc.set_value(0x3080)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 0xFF, True) == 0x307F
        assert cpu.extra_cycles == 0
        assert mode.get_address(cpu, 0x80, True) == 0x3000
        assert cpu.extra_cycles == 0

        # Positive offset (page crossing)
        # Page boundary crossings should induce a 1 cycle penalty
        cpu.pc.set_value(0x30F0)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 0x7F, True) == 0x316F
        assert cpu.extra_cycles == 1
        cpu.pc.set_value(0x30FF)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 1, True) == 0x3100
        assert cpu.extra_cycles == 1

        # Negative offset (page crossing)
        # Page boundary crossings should induce a 1 cycle penalty
        cpu.pc.set_value(0x3010)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 0x80, True) == 0x2F90
        assert cpu.extra_cycles == 1
        cpu.pc.set_value(0x3000)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 0xFF, True) == 0x2FFF
        assert cpu.extra_cycles == 1

        # Of course the extra cycle should not be applied if passing page_cross_penalty as False
        cpu.pc.set_value(0x30FF)
        cpu.extra_cycles = 0
        assert mode.get_address(cpu, 1, False) == 0x3100
        assert cpu.extra_cycles == 0

        # Value is unsupported (since this is only for branch operations, value would make no sense)
        assert is_unsupported(mode.get_value, cpu, 0, False)

    def test_indirect(self):
        mode = addressing_modes[AddressingMode.INDIRECT]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 2
        assert mode.input_size == 2

        # Address reads the 16-bit value from memory
        memory.write(0x720, 0x1)
        memory.write(0x721, 0x2)
        assert mode.get_address(cpu, 0x720, False) == 0x201

        # Indirect should cause page wraparound
        # (and also consequentially not induce a cycle penalty)
        memory.write(0x6FF, 0x7)
        memory.write(0x600, 0x6)
        assert mode.get_address(cpu, 0x6FF, True) == 0x607
        assert cpu.extra_cycles == 0

        # Value is unsupported (since this is only for jump operations, value would make no sense)
        assert is_unsupported(mode.get_value, cpu, 0, False)

    def test_indexed_zero_page_x(self):
        mode = addressing_modes[AddressingMode.INDEXED_ZERO_PAGE_X]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # Address returns the provided address + the value of X
        # (this is an unsigned addition)
        # (Wraparound should also occur)
        cpu.x.set_value(0x10)
        assert mode.get_address(cpu, 0x50, True) == 0x60

        cpu.x.set_value(0x10)
        assert mode.get_address(cpu, 0xEF, True) == 0xFF

        cpu.x.set_value(0xE0)
        assert mode.get_address(cpu, 0xE0, True) == 0xC0
        assert cpu.extra_cycles == 0

        cpu.x.set_value(0xE0)
        assert mode.get_address(cpu, 0x20, True) == 0x00
        assert cpu.extra_cycles == 0

        # Value just returns the 8-bit value at the address
        cpu.memory.write(0x22, 0x12)
        cpu.x.set_value(0x21)
        assert mode.get_value(cpu, 0x1, True) == 0x12

    def test_indexed_zero_page_y(self):
        mode = addressing_modes[AddressingMode.INDEXED_ZERO_PAGE_Y]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # Address returns the provided address + the value of Y
        # (this is an unsigned addition)
        # (Wraparound should also occur)
        cpu.y.set_value(0x10)
        assert mode.get_address(cpu, 0x50, True) == 0x60

        cpu.y.set_value(0x10)
        assert mode.get_address(cpu, 0xEF, True) == 0xFF

        cpu.y.set_value(0xE0)
        assert mode.get_address(cpu, 0xE0, True) == 0xC0
        assert cpu.extra_cycles == 0

        cpu.y.set_value(0xE0)
        assert mode.get_address(cpu, 0x20, True) == 0x00
        assert cpu.extra_cycles == 0

        # Value just returns the 8-bit value at the address
        cpu.memory.write(0x22, 0x12)
        cpu.y.set_value(0x21)
        assert mode.get_value(cpu, 0x1, True) == 0x12

    def test_indexed_absolute_x(self):
        mode = addressing_modes[AddressingMode.INDEXED_ABSOLUTE_X]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 2
        assert mode.input_size == 2

        # Address returns the provided address + the value of X
        # (this is an unsigned addition)
        # (Page boundary crossings should induce a cycle penalty)
        cpu.x.set_value(0x10)
        assert mode.get_address(cpu, 0x150, True) == 0x160

        cpu.x.set_value(0xEF)
        assert mode.get_address(cpu, 0x210, True) == 0x2FF

        cpu.x.set_value(0xE0)
        assert mode.get_address(cpu, 0x120, True) == 0x200
        assert cpu.extra_cycles == 1
        cpu.extra_cycles = 0

        cpu.x.set_value(0xE0)
        assert mode.get_address(cpu, 0x1E0, True) == 0x2C0
        assert cpu.extra_cycles == 1
        cpu.extra_cycles = 0

        # Value just returns the 8-bit value at the address
        cpu.memory.write(0x222, 0x12)
        cpu.x.set_value(0x21)
        assert mode.get_value(cpu, 0x201, True) == 0x12

    def test_indexed_absolute_y(self):
        mode = addressing_modes[AddressingMode.INDEXED_ABSOLUTE_Y]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 2
        assert mode.input_size == 2

        # Address returns the provided address + the value of Y
        # (this is an unsigned addition)
        # (Page boundary crossings should induce a cycle penalty)
        cpu.y.set_value(0x10)
        assert mode.get_address(cpu, 0x150, True) == 0x160

        cpu.y.set_value(0xEF)
        assert mode.get_address(cpu, 0x210, True) == 0x2FF

        cpu.y.set_value(0xE0)
        assert mode.get_address(cpu, 0x120, True) == 0x200
        assert cpu.extra_cycles == 1
        cpu.extra_cycles = 0

        cpu.y.set_value(0xE0)
        assert mode.get_address(cpu, 0x1E0, True) == 0x2C0
        assert cpu.extra_cycles == 1
        cpu.extra_cycles = 0

        # Value just returns the 8-bit value at the address
        cpu.memory.write(0x222, 0x12)
        cpu.y.set_value(0x21)
        assert mode.get_value(cpu, 0x201, True) == 0x12

    def test_indexed_indirect(self):
        mode = addressing_modes[AddressingMode.INDEXED_INDIRECT]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # Operand argument + [X] points to lower byte of 16-bit address in memory
        # (w/ zero page wraparound)
        cpu.memory.write(0x20, 0x1)
        cpu.memory.write(0x21, 0x2)
        cpu.x.set_value(0x18)
        assert mode.get_address(cpu, 0x8, False) == 0x201

        cpu.memory.write(0x20, 0x7)
        cpu.memory.write(0x21, 0x6)
        cpu.x.set_value(0x40)
        assert mode.get_address(cpu, 0xE0, True) == 0x607
        assert cpu.extra_cycles == 0

        # get_value should retrieve the 8-bit value at the address specified by get_address
        cpu.memory.write(0x20, 0x1)
        cpu.memory.write(0x21, 0x2)
        cpu.memory.write(0x201, 0x77)
        cpu.x.set_value(0x40)
        assert mode.get_value(cpu, 0xE0, True) == 0x77
        assert cpu.extra_cycles == 0

    def test_indirect_indexed(self):
        mode = addressing_modes[AddressingMode.INDIRECT_INDEXED]
        memory = CPUMemory()
        cpu = CPU(memory)

        # Should have an input size of 1
        assert mode.input_size == 1

        # get_address should return [input]+[Y]
        cpu.memory.write(0x20, 0x1)
        cpu.memory.write(0x21, 0x2)
        cpu.y.set_value(0xF)
        assert mode.get_address(cpu, 0x20, False) == 0x210

        # Zero page wraparound should occur too
        cpu.memory.write(0xFF, 0x1)
        cpu.memory.write(0x00, 0x2)
        cpu.y.set_value(0x2F)
        assert mode.get_address(cpu, 0xFF, True) == 0x230
        assert cpu.extra_cycles == 0

        # When indexing crosses a page boundary a cycle penalty should be incurred
        cpu.memory.write(0x20, 0x1)
        cpu.memory.write(0x21, 0x2)
        cpu.y.set_value(0xFF)
        assert mode.get_address(cpu, 0x20, True) == 0x300
        assert cpu.extra_cycles == 1
        cpu.extra_cycles = 0

        # get_value should just return the 8-bit value at the address provided by get_address
        cpu.memory.write(0x20, 0x1)
        cpu.memory.write(0x21, 0x2)
        cpu.memory.write(0x300, 0x77)
        cpu.y.set_value(0xFF)
        assert mode.get_value(cpu, 0x20, True) == 0x77
        assert cpu.extra_cycles == 1
        cpu.extra_cycles = 0
