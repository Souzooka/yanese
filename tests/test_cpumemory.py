from src.controllers.Controller import Controller
from src.CPUMemory import CPUMemory


class TestCPUMemory:
    # Tests for the CPU memory bus

    def test_wram(self):
        # When initializing CPUMemory, $0000-$07FF
        # (and the mirrors at $0800-$1FFF) should be read
        # as a value of 0
        memory = CPUMemory()

        # Main WRAM
        for i in range(0, 0x800):
            assert memory.read(i) == 0x00

        # Mirrors
        for i in range(0x800, 0x2000):
            assert memory.read(i) == 0x00

        # WRAM + mirrors should return back values written to main WRAM region or mirrors
        memory = CPUMemory()

        for i in range(0, 0x800):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

        memory = CPUMemory()
        for i in range(0x800, 0x1000):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

        memory = CPUMemory()
        for i in range(0x1000, 0x1800):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

        memory = CPUMemory()
        for i in range(0x1800, 0x2000):
            memory.write(i, i & 0xFF)

        for i in range(0, 0x2000):
            assert memory.read(i) == i & 0xFF

    def test_controllers(self):
        # Can read from $4016 and $4017 to poll controller status, and
        # write to $4016 to affect controllers
        controller0 = Controller(0)
        controller1 = Controller(1)
        controller0.on_load(controller1)
        controller1.on_load(controller0)
        memory = CPUMemory()
        memory.on_load(controllers=[controller0, controller1])

        # Hijack the controller on_read and on_write functions to check if they're called
        on_read0_called = False
        on_read1_called = False
        on_write0_called = False
        on_read0 = controller0.on_read
        on_read1 = controller1.on_read
        on_write0 = controller0.on_write

        def read0(*args, **kwargs):
            nonlocal on_read0_called
            on_read0_called = True
            return on_read0(*args, **kwargs)

        def read1(*args, **kwargs):
            nonlocal on_read1_called
            on_read1_called = True
            return on_read1(*args, **kwargs)

        def write0(*args, **kwargs):
            nonlocal on_write0_called
            on_write0_called = True
            return on_write0(*args, **kwargs)

        controller0.on_read = read0
        controller1.on_read = read1
        controller0.on_write = write0

        # Now check the controllers are properly accessed via the CPU memory bus
        memory.read(0x4016)
        assert on_read0_called, "CPU memory bus read ($4016) should read JOY0"
        memory.read(0x4017)
        assert on_read1_called, "CPU memory bus read ($4017) should read JOY1"
        memory.write(0x4016, 1)
        assert on_read0_called, "CPU memory bus write ($4016) should write JOY0"

    def test_read_write16(self):
        # read16/write16 helpers
        memory = CPUMemory()

        # A write of 0x201 to 0x0 should store 0x1 in $0 and 0x2 in $1
        memory.write16(0, 0x201)
        assert memory.read(0) == 0x1
        assert memory.read(1) == 0x2

        # And of course a call to read16 at 0 should return 0x201
        assert memory.read16(0) == 0x201

    def test_save_state(self):
        # Should only need to preserve WRAM here

        # If a state is taken for a new instance of memory, all of WRAM should be 0
        # after restoring the state even after setting memory
        memory = CPUMemory()
        state = memory.get_save_state()
        for i in range(0, 0x800):
            memory.write(i, i & 0xFF)

        memory.set_save_state(state)

        for i in range(0, 0x800):
            assert memory.read(i) == 0x00

        # And the other way around too
        memory = CPUMemory()
        for i in range(0, 0x800):
            memory.write(i, i & 0xFF)
        state = memory.get_save_state()

        for i in range(0, 0x800):
            memory.write(i, 0)

        memory.set_save_state(state)

        for i in range(0, 0x800):
            assert memory.read(i) == i & 0xFF
