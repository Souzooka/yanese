from src.cpu.registers import Register8Bit
from src.cpu.Stack import Stack
from src.CPUMemory import CPUMemory


class TestStack:
    def test_push(self):
        memory = CPUMemory()
        sp = Register8Bit()
        stack = Stack(memory, sp)

        # Stack.push should push a value to the stack.
        # This decrements the stack pointer (underflowing if needed)
        # and saves the value to memory at the address the stack pointer
        # was pointing at before decrementing.
        sp.set_value(0)
        stack.push(0x20)
        assert memory.read(0x100) == 0x20
        assert sp.get_value() == 0xFF

        # Stack.push16 should push a 16-bit value to the stack.
        # This is effectively a push operation done twice, with the
        # high byte of the value being pushed first, then the low byte.
        sp.set_value(0)
        stack.push16(0x1234)
        assert memory.read(0x100) == 0x12
        assert memory.read(0x1FF) == 0x34

    def test_pop(self):
        memory = CPUMemory()
        sp = Register8Bit()
        stack = Stack(memory, sp)

        # Stack.pop should return a value on the stack.
        # The stack pointer first increments, then the
        # value at the address the stack pointer indicates
        # is read.
        sp.set_value(0)
        stack.push(0x20)
        assert stack.pop() == 0x20
        assert sp.get_value() == 0

        # Stack.pop16 returns a 16-bit value from the stack.
        # This is effectively the same as two pop operations.
        sp.set_value(0)
        stack.push16(0x1234)
        assert stack.pop16() == 0x1234
        assert sp.get_value() == 0
