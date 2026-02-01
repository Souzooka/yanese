from src.cpu.CPU import CPU
from src.cpu.registers import FlagsRegister, Register8Bit, Register16Bit
from src.CPUMemory import CPUMemory


class TestCPU:
    def test_properties(self):
        # Test CPU's accessible properties
        memory = CPUMemory()
        cpu = CPU(memory)

        # Has accessible memory bus
        assert type(getattr(cpu, "memory", None)) is CPUMemory

        # Has accessible registers
        assert type(getattr(cpu, "a", None)) is Register8Bit
        assert type(getattr(cpu, "x", None)) is Register8Bit
        assert type(getattr(cpu, "y", None)) is Register8Bit
        assert type(getattr(cpu, "sp", None)) is Register8Bit
        assert type(getattr(cpu, "pc", None)) is Register16Bit
        assert type(getattr(cpu, "flags", None)) is FlagsRegister

        # Has accessible cycle counting properties
        assert type(getattr(cpu, "cycles", None)) is int
        assert cpu.cycles == 0
        assert type(getattr(cpu, "extra_cycles", None)) is int
        assert cpu.extra_cycles == 0
